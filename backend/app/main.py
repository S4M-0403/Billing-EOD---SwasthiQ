from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.billing import router as billing_router


app = FastAPI(
    title="SwasthiQ EOD Billing API",
    version="1.0.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(billing_router)


@app.get("/health")
def health_check():
    return {"status": "ok"}