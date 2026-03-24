from app.database import engine
from sqlalchemy import text

def add_exam_date_column():
    with engine.connect() as conn:
        try:
            conn.execute(text("ALTER TABLE scores ADD COLUMN exam_date TIMESTAMP WITH TIME ZONE"))
            conn.commit()
            print("Added exam_date column to scores table")
        except Exception as e:
            if "already exists" in str(e):
                print("Column already exists")
            else:
                print(f"Error: {e}")

if __name__ == "__main__":
    add_exam_date_column()
