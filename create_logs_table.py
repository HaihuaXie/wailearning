from sqlalchemy import create_engine, text

DATABASE_URL = "postgresql://ddclass:iTiipYXa64BjM7bF@81.70.103.192:5432/ddclass"

def create_logs_table():
    engine = create_engine(DATABASE_URL)

    with engine.connect() as conn:
        trans = conn.begin()

        try:
            # 检查表是否存在
            result = conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables
                    WHERE table_schema = 'public'
                    AND table_name = 'operation_logs'
                )
            """))

            if result.scalar():
                print("operation_logs 表已存在")
            else:
                # 创建表
                print("创建 operation_logs 表...")
                conn.execute(text("""
                    CREATE TABLE operation_logs (
                        id SERIAL PRIMARY KEY,
                        user_id INTEGER REFERENCES users(id),
                        username VARCHAR,
                        action VARCHAR NOT NULL,
                        target_type VARCHAR NOT NULL,
                        target_id INTEGER,
                        target_name VARCHAR,
                        details VARCHAR,
                        ip_address VARCHAR,
                        user_agent VARCHAR,
                        result VARCHAR DEFAULT 'success',
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                    )
                """))
                print("operation_logs 表创建成功！")

            # 创建索引
            print("创建索引...")
            conn.execute(text("CREATE INDEX idx_operation_logs_created_at ON operation_logs(created_at DESC)"))
            conn.execute(text("CREATE INDEX idx_operation_logs_user_id ON operation_logs(user_id)"))
            conn.execute(text("CREATE INDEX idx_operation_logs_action ON operation_logs(action)"))
            conn.execute(text("CREATE INDEX idx_operation_logs_target_type ON operation_logs(target_type)"))

            trans.commit()
            print("索引创建成功！")

        except Exception as e:
            trans.rollback()
            print(f"创建失败: {e}")
            raise

if __name__ == "__main__":
    create_logs_table()
