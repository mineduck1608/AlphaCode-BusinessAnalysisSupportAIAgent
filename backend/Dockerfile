# ---- Base image ----
FROM python:3.11-slim

# ---- Set working directory ----
WORKDIR /app

# ---- Install system dependencies (nếu cần) ----
# RUN apt-get update && apt-get install -y build-essential

# ---- Copy requirements & install ----
COPY api-gateway/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# ---- Copy entire backend ----
COPY . .

# ---- Expose port (tuỳ app của bạn chạy port nào) ----
EXPOSE 8000

# ---- Run application ----
# Nếu dùng FastAPI (uvicorn)
# CMD ["uvicorn", "api-gateway.main:app", "--host", "0.0.0.0", "--port", "8000"]

# Nếu bạn chạy file main.py trực tiếp:
CMD ["python", "api-gateway/main.py"]
