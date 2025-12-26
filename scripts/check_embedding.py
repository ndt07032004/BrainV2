import sys
import os
# Thêm dòng này để chạy script từ thư mục gốc
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain_community.vectorstores import Chroma
from src.helper import download_hugging_face_embeddings
from config import settings
from utils.logger import get_logger

logger = get_logger(__name__)

def check_database():
    logger.info("--- BẮT ĐẦU KIỂM TRA DATABASE ---")
    
    if not os.path.exists(settings.PERSIST_DIRECTORY):
        logger.error(f"LỖI: Không tìm thấy thư mục CSDL: '{settings.PERSIST_DIRECTORY}'")
        logger.error("Vui lòng chạy 'python -m scripts.store_data_from_csv' trước.")
        return

    try:
        logger.info("Đang tải mô hình embedding để kiểm tra...")
        embeddings = download_hugging_face_embeddings()
        
        logger.info(f"Đang tải CSDL từ '{settings.PERSIST_DIRECTORY}'...")
        vectordb = Chroma(
            persist_directory=settings.PERSIST_DIRECTORY,
            embedding_function=embeddings
        )
        
        collection = vectordb._collection
        count = collection.count()
        logger.info(f"KIỂM TRA THÀNH CÔNG: Đã tải CSDL. Tổng số vector: {count}")
        
        if count == 0:
            logger.warning("CSDL không có vector nào. Có thể đã xảy ra lỗi khi nạp dữ liệu.")
            return

        # Thực hiện một truy vấn thử (dựa trên test.py)
        test_query = "Súng trường sks"
        logger.info(f"Đang thực hiện truy vấn thử với: '{test_query}'...")
        results = vectordb.similarity_search(test_query, k=1)
        
        if results:
            logger.info("--- KẾT QUẢ TRUY VẤN THỬ (Top 1) ---")
            logger.info(f"Nội dung: {results[0].page_content}")
            logger.info(f"Metadata: {results[0].metadata}")
            logger.info("--- KIỂM TRA HOÀN TẤT ---")
        else:
            logger.warning("Truy vấn thử không trả về kết quả.")

    except Exception as e:
        logger.error(f"Lỗi nghiêm trọng khi kiểm tra CSDL: {e}", exc_info=True)

if __name__ == "__main__":
    check_database()