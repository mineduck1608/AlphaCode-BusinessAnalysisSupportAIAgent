# Sử dụng Python 3.10-slim làm base image
FROM python:3.10-slim

# Thiết lập biến môi trường để Python không tạo file .pyc và xuất log trực tiếp
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

# Thiết lập thư mục làm việc bên trong container
WORKDIR /app

# Sao chép file dependencies và cài đặt chúng
# Việc này giúp tận dụng Docker cache nếu requirements.txt không thay đổi
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Sao chép toàn bộ code còn lại vào thư mục làm việc
COPY gateway /app/gateway

# Mở cổng mà ứng dụng (Uvicorn/FastAPI) sẽ chạy
# Mặc định thường là 8000
EXPOSE 8000

# Lệnh chạy ứng dụng khi container khởi động
# Dùng uvicorn để chạy server.py (hoặc main.py)
# Giả sử ứng dụng của bạn là 'server:app' hoặc 'main:app'
# Cần thay đổi 'server:app' nếu tên file/biến khác
CMD ["uvicorn", "gateway.server:app", "--host", "0.0.0.0", "--port", "8000"]