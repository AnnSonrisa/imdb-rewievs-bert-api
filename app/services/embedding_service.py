import logging
import torch
from transformers import DistilBertModel, DistilBertTokenizer
from app.core.config import settings

logger = logging.getLogger(__name__)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
logger.info(f"Using device: {device}")

try:
    model = DistilBertModel.from_pretrained(settings.MODEL_PATH).to(device).eval()
    tokenizer = DistilBertTokenizer.from_pretrained(settings.MODEL_PATH)
    logger.info("Embedding model loaded successfully.")
except Exception as e:
    logger.exception("Error loading embedding model.")
    raise


def generate_embedding(text: str) -> list[float] | None:
    try:
        inputs = tokenizer(
            text,
            return_tensors='pt',
            max_length=512,
            truncation=True,
            padding='max_length'
        ).to(device)
        with torch.no_grad():
            outputs = model(**inputs)
        return outputs.last_hidden_state.mean(dim=1).squeeze().tolist()
    except Exception as e:
        logger.exception("Embedding generation failed.")
        return None