from celery.result import AsyncResult
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import Review
from app.api.schemas import ReviewCreate, TextRequest, ReviewResponse
from app.tasks.embeddings import generate_and_store_embedding_task, find_similar_reviews_task
from app.api.dependencies import get_db

router = APIRouter()


@router.post("/add_review", response_model=ReviewResponse)
async def create_review(
        review: ReviewCreate,
        db: AsyncSession = Depends(get_db)
):
    """
    Task of creating of review.
    """
    db_review = Review(text=review.text)
    db.add(db_review)
    await db.commit()
    await db.refresh(db_review)
    print("ID после сохранения:", db_review.id)  # Отладка
    generate_and_store_embedding_task.delay(db_review.id, review.text)
    return {"id": db_review.id, "text": review.text}

@router.post("/find_similar")
async def find_similar(request: TextRequest):
    """
    Task of searching for similar reviews.
    """
    task = find_similar_reviews_task.delay(request.text, request.top_n)
    return {
        "task_id": task.id
    }

@router.get("/status/{task_id}")
async def get_task_status(task_id: str):
    """
    Method for returns the current task status and the result.
    """
    task_result = AsyncResult(task_id)
    if not task_result.ready():
        return {
            "task_id": task_id,
            "status": task_result.status,
            "result": None
        }

    if task_result.failed():
        raise HTTPException(
            status_code=500,
            detail=f"Task completion error: {task_result.result}."
        )
    return {
        "task_id": task_id,
        "status": "SUCCESS",
        "result": task_result.result
    }