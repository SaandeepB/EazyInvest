from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import audit, holdings, portfolio, scenarios, users
from app.db.database import Base, engine
from app.utils.defaults import APP_NAME


load_dotenv(Path(__file__).resolve().parent.parent / ".env", override=True)

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=f"{APP_NAME} API",
    description="Deterministic portfolio management with CSV-backed market proxy data and response-scoped audit traces.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router)
app.include_router(holdings.router)
app.include_router(portfolio.router)
app.include_router(scenarios.router)
app.include_router(audit.router)


@app.get("/")
def root():
    return {
        "name": APP_NAME,
        "message": f"{APP_NAME} API",
        "market_source": "csv_proxy",
        "docs": "/docs",
    }


@app.get("/health")
def health():
    return {"status": "ok"}
