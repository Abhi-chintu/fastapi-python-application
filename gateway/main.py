import os
import httpx
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import Response

app = FastAPI(title="API Gateway")
PRODUCTS_URL = os.getenv("PRODUCTS_URL", "http://localhost:8001").rstrip("/")

@app.get("/health")
def health():
    return {"status": "ok", "service": "gateway"}

@app.api_route("/products", methods=["GET", "POST"])
@app.api_route("/products/{product_id}", methods=["GET", "PUT", "DELETE"])
async def products_proxy(request: Request, product_id: str = ""):
    url = PRODUCTS_URL + "/products" + (f"/{product_id}" if product_id else "")
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.request(request.method, url, params=request.query_params,
                content=await request.body(),
                headers={"content-type": request.headers.get("content-type", "application/json")})
    except httpx.HTTPError as exc:
        raise HTTPException(502, "Products service unavailable") from exc
    return Response(r.content, status_code=r.status_code,
                    media_type=r.headers.get("content-type", "application/json"))
