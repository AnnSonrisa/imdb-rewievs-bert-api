from app.celery_app import celery
from app.core.database import get_sync_db, Review
import logging

from app.services.embedding_service import generate_embedding

logger = logging.getLogger(__name__)


@celery.task(bind=True, max_retries=3)
def generate_and_store_embedding_task(self, review_id: int, text: str):
    """Task of generation and save of embedding."""
    try:
        with get_sync_db() as db:
            embedding = generate_embedding(text)
            if not embedding:
                raise ValueError("Embedding generation failed.")
            review = db.query(Review).get(review_id)
            if not review:
                logger.warning(f"Review {review_id} not found.")
                return
            review.embedding = embedding
            db.commit()
            logger.info(f"Embedding stored for review {review_id}.")

    except Exception as exc:
        logger.error(f"Task failed: {str(exc)}")
        self.retry(exc=exc, countdown=2 ** self.request.retry)


@celery.task(bind=True, max_retries=3)
def find_similar_reviews_task(self, text: str, top_n: int = 3):
    """Task of search similar reviews."""
    try:
        embedding = generate_and_store_embedding_task(text)
        if not embedding:
            raise ValueError("Embedding generation failed.")
        with get_sync_db() as db:
            return [
                {
                    "id": r.id,
                    "text": r.text,
                    "similarity": float(r.distance)
                }
                for r in db.query(
                    Review.id,
                    Review.text,
                    Review.embedding.cosine_distance(embedding).label('distance')
                ).order_by('distance')
                .limit(top_n)
            ]
    except Exception as exc:
        logger.exception("Search task failed.")
        self.retry(exc=exc, countdown=2 ** self.request.retry)