import os, time
import psycopg2
from psycopg2.extras import RealDictCursor
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(title="Products API")
CFG = dict(host=os.getenv("DB_HOST", "localhost"), port=int(os.getenv("DB_PORT", "5432")),
           dbname=os.getenv("DB_NAME", "products"), user=os.getenv("DB_USER", "appuser"),
           password=os.getenv("DB_PASSWORD", "localdevpassword"))

class ProductIn(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    price: float = Field(ge=0)

def connect():
    return psycopg2.connect(**CFG, cursor_factory=RealDictCursor)

def init_db():
    last = None
    for _ in range(30):
        try:
            with connect() as conn:
                with conn.cursor() as cur:
                    cur.execute("CREATE TABLE IF NOT EXISTS products (id SERIAL PRIMARY KEY, name VARCHAR(200) NOT NULL, price NUMERIC(10,2) NOT NULL CHECK(price >= 0), created_at TIMESTAMPTZ NOT NULL DEFAULT NOW())")
            return
        except psycopg2.OperationalError as exc:
            last = exc
            time.sleep(2)
    raise RuntimeError(f"PostgreSQL unavailable: {last}")

@app.on_event("startup")
def startup():
    init_db()

@app.get("/health")
def health():
    try:
        with connect() as conn:
            with conn.cursor() as cur: cur.execute("SELECT 1")
        return {"status": "ok", "service": "products", "database": "connected"}
    except psycopg2.Error as exc:
        raise HTTPException(503, "Database unavailable") from exc

@app.get("/products")
def list_products():
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id,name,price,created_at FROM products ORDER BY id")
            return cur.fetchall()

@app.post("/products", status_code=201)
def create_product(p: ProductIn):
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO products(name,price) VALUES (%s,%s) RETURNING id,name,price,created_at", (p.name,p.price))
            return cur.fetchone()

@app.get("/products/{product_id}")
def get_product(product_id: int):
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id,name,price,created_at FROM products WHERE id=%s", (product_id,))
            row = cur.fetchone()
    if not row: raise HTTPException(404, "Product not found")
    return row

@app.put("/products/{product_id}")
def update_product(product_id: int, p: ProductIn):
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute("UPDATE products SET name=%s,price=%s WHERE id=%s RETURNING id,name,price,created_at", (p.name,p.price,product_id))
            row = cur.fetchone()
    if not row: raise HTTPException(404, "Product not found")
    return row

@app.delete("/products/{product_id}", status_code=204)
def delete_product(product_id: int):
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM products WHERE id=%s RETURNING id", (product_id,))
            row = cur.fetchone()
    if not row: raise HTTPException(404, "Product not found")
    return None
