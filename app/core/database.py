from contextlib import asynccontextmanager, contextmanager

from sqlalchemy import create_engine, Column, Integer, Text, text
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from pgvector.sqlalchemy import Vector
from app.core.config import settings

Base = declarative_base()

class Review(Base):
    __tablename__ = "reviews"
    id = Column(Integer, primary_key=True, index=True)
    text = Column(Text, nullable=False)
    embedding = Column(Vector(768))

sync_engine = create_engine(settings.SYNC_DATABASE_URL)
SyncSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)

async_engine = create_async_engine(
    settings.ASYNC_DATABASE_URL,
    future=True,
    pool_size=20,
    max_overflow=10
)
AsyncSessionLocal = sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)

def init_db():
    with sync_engine.begin() as conn:
        check_extension = text(
            "SELECT 1 FROM pg_extension WHERE extname = 'vector'"
        )
        result = conn.execute(check_extension).scalar()
        if not result:
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        Base.metadata.create_all(bind=conn)

@asynccontextmanager
async def get_async_db():
    async with AsyncSessionLocal() as session:
        yield session

@contextmanager
def get_sync_db():
    with SyncSessionLocal() as db:
        yield db


async def find_similar_reviews(embedding: list):
    """
    Поиск похожих отзывов по косинусной близости.
    """
    async with AsyncSessionLocal() as session:
        similar = session.execute(
            text("""
SELECT text, 
       1 - (embedding <=> :embedding) AS similarity
FROM reviews 
ORDER BY embedding <=> :embedding 
LIMIT 3
"""),
            {"embedding": embedding}
        )
        return similar.all()
