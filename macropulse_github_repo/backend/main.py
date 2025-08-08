from fastapi import FastAPI
from backend.db import init_db
from backend.api.data_routes_secure import router as data_router

app = FastAPI(title="MacroPulse Data Engine")

@app.on_event("startup")
def startup(): init_db()

@app.get("/")
def root(): return {"status":"ok","service":"macropulse-data-engine"}

app.include_router(data_router)
