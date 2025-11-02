# Sử dụng Python base image chính thức cho môi trường production
FROM python:3.11-slim

# Thiết lập biến môi trường (ENV)
# Thiết lập PTYHONUNBUFFERED=1 để luồng output được hiển thị ngay lập tức trong container logs
ENV PYTHONUNBUFFERED 1

# Thiết lập thư mục làm việc trong container
WORKDIR /app

# SAO CHÉP FILE CẤU HÌNH MÔI TRƯỜNG
# Copy file .env TỪ thư mục gốc vào container.
COPY .env /app/.env

# Sao chép file requirements.txt TỪ thư mục api
# SỬA LỖI: Sử dụng đường dẫn api/requirements.txt để khắc phục lỗi 'not found'
COPY requirements.txt /app/

# Cài đặt dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Sao chép toàn bộ mã nguồn của dự án vào thư mục làm việc
# (Bao gồm api, core, repositories, services,...)
# Chú ý: .dockerignore sẽ loại trừ các file không cần thiết như .git, venv
COPY . /app

# Đặt ENTRYPOINT để chạy ứng dụng bằng Uvicorn
ENTRYPOINT ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]

# Mở port mà ứng dụng đang lắng nghe
EXPOSE 8000