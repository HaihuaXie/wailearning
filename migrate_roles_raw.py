from sqlalchemy import create_engine, text

DATABASE_URL = "postgresql://ddclass:iTiipYXa64BjM7bF@81.70.103.192:5432/ddclass"

def migrate():
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        trans = conn.begin()
        
        try:
            result = conn.execute(text("SELECT id, username, role FROM users"))
            print("当前用户角色：")
            for row in result:
                print(f"  {row[1]}: {row[2]}")
            
            print("\n更新角色值...")
            conn.execute(text("UPDATE users SET role = 'admin' WHERE role = 'ADMIN'"))
            conn.execute(text("UPDATE users SET role = 'class_teacher' WHERE role = 'CLASS_TEACHER'"))
            conn.execute(text("UPDATE users SET role = 'teacher' WHERE role = 'TEACHER'"))
            
            result = conn.execute(text("SELECT id, username, role FROM users"))
            print("\n更新后用户角色：")
            for row in result:
                print(f"  {row[1]}: {row[2]}")
            
            trans.commit()
            print("\n迁移完成！")
            
        except Exception as e:
            trans.rollback()
            print(f"迁移失败: {e}")
            raise

if __name__ == "__main__":
    migrate()
