import os
from collections.abc import AsyncIterator, Iterator, Mapping
from contextlib import asynccontextmanager, contextmanager
from decimal import Decimal
from typing import Any

import psycopg2
from fastapi import FastAPI, HTTPException, Response, status
from pydantic import BaseModel, Field
from psycopg2.extensions import connection as PostgreSQLConnection
from psycopg2.extras import RealDictCursor

DB_HOST = os.getenv("DB_HOST", "postgres")
DB_PORT = int(os.getenv("DB_PORT", "5432"))
DB_NAME = os.getenv("DB_NAME", "products")
DB_USER = os.getenv("DB_USER", "appuser")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")


class ProductInput(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    price: Decimal = Field(ge=0, max_digits=12, decimal_places=2)


@contextmanager
def database_connection() -> Iterator[PostgreSQLConnection]:
    connection = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        connect_timeout=5,
    )
    try:
        yield connection
    finally:
        connection.close()


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    with database_connection() as connection:
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS products (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR(255) NOT NULL,
                        price NUMERIC(12, 2) NOT NULL CHECK (price >= 0)
                    )
                    """
                )
    yield


app = FastAPI(title="Products API", lifespan=lifespan)


def product_response(row: Mapping[str, Any]) -> dict[str, int | str | float]:
    return {
        "id": row["id"],
        "name": row["name"],
        "price": float(row["price"]),
    }


def normalized_name(name: str) -> str:
    name = name.strip()
    if not name:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Product name must not be blank",
        )
    return name


@app.get("/health")
def health() -> dict:
    with database_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
    return {"status": "ok", "service": "products"}


@app.get("/products")
def list_products() -> list[dict[str, int | str | float]]:
    with database_connection() as connection:
        with connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("SELECT id, name, price FROM products ORDER BY id")
            rows = cursor.fetchall()
    return [product_response(row) for row in rows]


@app.post("/products", status_code=status.HTTP_201_CREATED)
def create_product(product: ProductInput) -> dict[str, int | str | float]:
    name = normalized_name(product.name)
    with database_connection() as connection:
        with connection:
            with connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(
                    """
                    INSERT INTO products (name, price)
                    VALUES (%s, %s)
                    RETURNING id, name, price
                    """,
                    (name, product.price),
                )
                row = cursor.fetchone()
    return product_response(row)


@app.put("/products/{product_id}")
def update_product(
    product_id: int,
    product: ProductInput,
) -> dict[str, int | str | float]:
    name = normalized_name(product.name)
    with database_connection() as connection:
        with connection:
            with connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(
                    """
                    UPDATE products
                    SET name = %s, price = %s
                    WHERE id = %s
                    RETURNING id, name, price
                    """,
                    (name, product.price, product_id),
                )
                row = cursor.fetchone()
                if row is None:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Product not found",
                    )
    return product_response(row)


@app.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(product_id: int) -> Response:
    with database_connection() as connection:
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "DELETE FROM products WHERE id = %s",
                    (product_id,),
                )
                if cursor.rowcount == 0:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Product not found",
                    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
