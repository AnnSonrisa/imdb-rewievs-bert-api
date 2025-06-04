from fastapi import FastAPI
from app.core.database import init_db
from app.api.endpoints import router as api_router
from app.core.config import settings
import uvicorn
from sqlalchemy_utils import database_exists, create_database

def ensure_database_exists():
    if not database_exists(settings.SYNC_DATABASE_URL):
        create_database(settings.SYNC_DATABASE_URL)
        print(f"Database created: {settings.SYNC_DATABASE_URL}")

ensure_database_exists()

# Initialize database
init_db()

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION
)

app.include_router(api_router, prefix="/api")

@app.get("/")
def health_check():
    return {"status": "ok", "service": settings.APP_NAME}

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)