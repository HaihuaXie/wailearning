from sqlalchemy import create_engine, text

DATABASE_URL = "postgresql://ddclass:iTiipYXa64BjM7bF@81.70.103.192:5432/ddclass"

def fix_enum():
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        trans = conn.begin()
        
        try:
            # 查看当前枚举值
            result = conn.execute(text("SELECT enumlabel FROM pg_enum WHERE enumtypid = 'userrole'::regtype"))
            print("当前枚举值:")
            for row in result:
                print(f"  - {row[0]}")
            
            # 修改列类型为varchar（同时转换数据为小写）
            print("\n修改列类型为varchar并转换为小写...")
            conn.execute(text("ALTER TABLE users ALTER COLUMN role TYPE varchar(50) USING LOWER(role::text)"))
            
            # 删除旧枚举类型
            print("删除旧枚举类型...")
            conn.execute(text("DROP TYPE IF EXISTS userrole"))
            
            # 创建新枚举类型
            print("创建新枚举类型...")
            conn.execute(text("CREATE TYPE userrole AS ENUM ('admin', 'class_teacher', 'teacher')"))
            
            # 修改列类型回枚举
            print("修改列类型回枚举...")
            conn.execute(text("ALTER TABLE users ALTER COLUMN role TYPE userrole USING role::userrole"))
            
            # 验证新枚举值
            result = conn.execute(text("SELECT enumlabel FROM pg_enum WHERE enumtypid = 'userrole'::regtype"))
            print("\n新枚举值:")
            for row in result:
                print(f"  - {row[0]}")
            
            # 验证用户角色
            result = conn.execute(text("SELECT id, username, role FROM users"))
            print("\n用户角色:")
            for row in result:
                print(f"  - {row[0]}: {row[1]} -> {row[2]}")
            
            trans.commit()
            print("\n枚举修复完成！")
            
        except Exception as e:
            trans.rollback()
            print(f"修复失败: {e}")
            raise

if __name__ == "__main__":
    fix_enum()
