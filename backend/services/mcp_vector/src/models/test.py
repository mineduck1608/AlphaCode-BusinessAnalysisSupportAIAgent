from sqlalchemy import text
from models.db import engine
def test_connection():
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✅ Kết nối database thành công!")
            return True
    except Exception as e:
        print(f"❌ Lỗi kết nối: {e}")
        return False

# Test kết nối
test_connection()