from langchain_huggingface import HuggingFaceEmbeddings
from config import settings
from utils.logger import get_logger

logger = get_logger(__name__)

def download_hugging_face_embeddings():
    """
    Tải mô hình embeddings từ HuggingFace dựa trên tên trong settings.
    """
    logger.info(f"Đang tải mô hình embedding: {settings.EMBEDDING_MODEL_NAME}...")
    try:
        embeddings = HuggingFaceEmbeddings(
            model_name=settings.EMBEDDING_MODEL_NAME,
            model_kwargs={'device': 'cpu'} 
        )
        logger.info("Tải embedding thành công.")
        return embeddings
    except Exception as e:
        logger.error(f"Lỗi khi tải mô hình embedding: {e}", exc_info=True)
        raise