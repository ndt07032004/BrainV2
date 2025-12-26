import sys
import os
# Thêm dòng này để chạy script từ thư mục gốc
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import csv
from langchain_chroma import Chroma
from langchain.schema import Document
from src.helper import download_hugging_face_embeddings
from config import settings
from utils.logger import get_logger
import shutil

logger = get_logger(__name__)

def load_data_from_csv(filepath="dataset.csv"):
    """
    Đọc dữ liệu từ tệp CSV và tạo danh sách Documents cho LangChain.
    """
    documents = []
    logger.info(f"Đang đọc tệp {filepath}...")
    
    try:
        with open(filepath, encoding="utf-8") as file:
            reader = csv.reader(file)
            header = next(reader) # Bỏ qua dòng tiêu đề
            
            count = 0
            for i, line in enumerate(reader):
                if len(line) < 5: 
                    logger.warning(f"Bỏ qua dòng {i+2}: không đủ cột.")
                    continue
                
                # Ghép các thông tin làm nội dung (content)
                content = (
                    f"Thông tin hiện vật: {line[1]}. "
                    f"Đặc điểm chi tiết: {line[2]}. "
                    f"Hiện vật thuộc thời kỳ lịch sử: {line[3]}. "
                    f"Công dụng chính hoặc ý nghĩa lịch sử là: {line[4]}."
                )
                
                # Tạo metadata
                metadata = {
                    "item_id": line[0],
                    "ten": line[1],
                    "thoi_ky": line[3],
                    "source": filepath
                }
                
                documents.append(Document(page_content=content, metadata=metadata))
                count += 1
                
        logger.info(f"Đã đọc thành công {count} tài liệu từ CSV.")
        return documents
        
    except FileNotFoundError:
        logger.error(f"LỖI: Không tìm thấy tệp {filepath}. Vui lòng kiểm tra lại.")
        return []
    except Exception as e:
        logger.error(f"Lỗi khi đọc CSV: {e}", exc_info=True)
        return []

def main():
    logger.info("--- BẮT ĐẦU QUÁ TRÌNH NẠP DỮ LIỆU ---")
    
    documents = load_data_from_csv("dataset.csv")
    
    if not documents:
        logger.error("Không có dữ liệu để xử lý. Dừng lại.")
        return

    embeddings = download_hugging_face_embeddings()

    logger.info(f"Đang tạo/lưu trữ vector vào thư mục: '{settings.PERSIST_DIRECTORY}'...")
    
    if os.path.exists(settings.PERSIST_DIRECTORY):
        logger.warning(f"Phát hiện thư mục cũ. Đang xóa: '{settings.PERSIST_DIRECTORY}'")
        shutil.rmtree(settings.PERSIST_DIRECTORY)

    try:
        vectordb = Chroma.from_documents(
            documents=documents,
            embedding=embeddings,
            persist_directory=settings.PERSIST_DIRECTORY
        )
        logger.info(f"Đã lưu thành công {len(documents)} vector vào ChromaDB.")
        logger.info("--- HOÀN TẤT NẠP DỮ LIỆU VÀO CHROMA ---")
    except Exception as e:
        logger.error(f"Lỗi khi nạp vào ChromaDB: {e}", exc_info=True)

if __name__ == "__main__":
    main()