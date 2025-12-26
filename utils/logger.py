import logging
import sys

# Định dạng cho logger
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

def get_logger(name, level=logging.INFO):
    """
    Thiết lập và trả về một đối tượng logger.
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Nếu logger đã có handler, không thêm nữa
    if logger.hasHandlers():
        return logger

    # Tạo handler cho console (stdout)
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setLevel(level)
    stream_handler.setFormatter(logging.Formatter(LOG_FORMAT))
    logger.addHandler(stream_handler)

    # (Tùy chọn) Tạo handler để ghi ra file
    # file_handler = logging.FileHandler("app.log", encoding="utf-8")
    # file_handler.setLevel(level)
    # file_handler.setFormatter(logging.Formatter(LOG_FORMAT))
    # logger.addHandler(file_handler)

    return logger