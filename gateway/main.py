import os
from pathlib import Path

import httpx
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import Response
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="API Gateway")

PRODUCTS_URL = os.getenv(
    "PRODUCTS_URL",
    "http://products:8001"
).rstrip("/")


@app.get("/health")
def health():
    return {"status": "ok", "service": "gateway"}


@app.api_route("/products", methods=["GET", "POST"])
@app.api_route(
    "/products/{product_id}",
    methods=["GET", "PUT", "DELETE"]
)
async def products_proxy(
    request: Request,
    product_id: str = ""
):
    url = PRODUCTS_URL + "/products"
    if product_id:
        url += f"/{product_id}"

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.request(
                request.method,
                url,
                params=request.query_params,
                content=await request.body(),
                headers={
                    "content-type": request.headers.get(
                        "content-type",
                        "application/json"
                    )
                }
            )
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=502,
            detail="Products service unavailable"
        ) from exc

    return Response(
        content=response.content,
        status_code=response.status_code,
        media_type=response.headers.get(
            "content-type",
            "application/json"
        )
    )


STATIC_DIR = Path(__file__).resolve().parent / "static"

app.mount(
    "/",
    StaticFiles(directory=str(STATIC_DIR), html=True),
    name="frontend"
)