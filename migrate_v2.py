from app.database import engine, Base
from sqlalchemy import text, inspect
import sys

def create_semesters_table():
    print("=" * 50)
    print("开始迁移：创建学期表")
    print("=" * 50)
    
    with engine.connect() as conn:
        try:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS semesters (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR NOT NULL UNIQUE,
                    year INTEGER NOT NULL,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                )
            """))
            conn.commit()
            print("✓ 学期表创建成功")
        except Exception as e:
            print(f"✗ 创建学期表失败: {e}")
            return False
    
    with engine.connect() as conn:
        try:
            result = conn.execute(text("SELECT COUNT(*) FROM semesters"))
            count = result.scalar()
            
            if count == 0:
                semesters = [
                    ("2024-1", 2024),
                    ("2024-2", 2024),
                    ("2025-1", 2025),
                    ("2025-2", 2025),
                ]
                
                for name, year in semesters:
                    conn.execute(text(
                        "INSERT INTO semesters (name, year, is_active) VALUES (:name, :year, TRUE)",
                    ), {"name": name, "year": year})
                
                conn.commit()
                print(f"✓ 初始化 {len(semesters)} 个学期数据")
            else:
                print(f"✓ 学期表已有 {count} 条数据")
                
        except Exception as e:
            print(f"✗ 初始化学期数据失败: {e}")
            return False
    
    return True

def update_student_unique_constraint():
    print("\n" + "=" * 50)
    print("开始迁移：修改学生学号唯一性约束")
    print("=" * 50)
    
    with engine.connect() as conn:
        try:
            inspector = inspect(engine)
            indexes = inspector.get_indexes('students')
            
            has_composite_index = False
            for idx in indexes:
                if idx['name'] == 'uq_student_class_no':
                    has_composite_index = True
                    break
            
            if not has_composite_index:
                conn.execute(text("""
                    CREATE UNIQUE INDEX uq_student_class_no 
                    ON students (class_id, student_no)
                """))
                conn.commit()
                print("✓ 创建班级-学号复合唯一索引")
            else:
                print("✓ 复合唯一索引已存在")
            
            unique_constraints = inspector.get_unique_constraints('students')
            has_global_unique = False
            for uc in unique_constraints:
                if 'student_no' in str(uc.get('column_names', [])):
                    has_global_unique = True
                    break
            
            if has_global_unique:
                try:
                    conn.execute(text("""
                        ALTER TABLE students 
                        DROP CONSTRAINT IF EXISTS students_student_no_key
                    """))
                    conn.commit()
                    print("✓ 删除学号全局唯一约束")
                except Exception as e:
                    print(f"! 删除约束时出现警告: {e}")
            else:
                print("✓ 学号全局唯一约束已不存在")
                
            result = conn.execute(text("""
                SELECT indexname, indexdef 
                FROM pg_indexes 
                WHERE tablename = 'students' 
                AND indexname = 'ix_students_student_no'
            """))
            if result.fetchone():
                conn.execute(text("DROP INDEX IF EXISTS ix_students_student_no"))
                conn.commit()
                print("✓ 删除学号单独唯一索引")
            
        except Exception as e:
            print(f"✗ 修改学生表约束失败: {e}")
            return False
    
    return True

def verify_migration():
    print("\n" + "=" * 50)
    print("验证迁移结果")
    print("=" * 50)
    
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name = 'semesters'
        """))
        if result.fetchone():
            print("✓ semesters 表存在")
        else:
            print("✗ semesters 表不存在")
            return False
        
        result = conn.execute(text("SELECT COUNT(*) FROM semesters"))
        count = result.scalar()
        print(f"✓ 学期表有 {count} 条记录")
        
        result = conn.execute(text("""
            SELECT indexname, indexdef 
            FROM pg_indexes 
            WHERE tablename = 'students' 
            AND indexname = 'uq_student_class_no'
        """))
        if result.fetchone():
            print("✓ 班级-学号复合唯一索引存在")
        else:
            print("✗ 班级-学号复合唯一索引不存在")
            return False
    
    return True

if __name__ == "__main__":
    print("\n" + "=" * 50)
    print("数据库迁移脚本 v2")
    print("=" * 50)
    
    try:
        success = True
        
        if not create_semesters_table():
            success = False
        
        if not update_student_unique_constraint():
            success = False
        
        if not verify_migration():
            success = False
        
        if success:
            print("\n" + "=" * 50)
            print("✓ 所有迁移成功完成！")
            print("=" * 50)
            sys.exit(0)
        else:
            print("\n" + "=" * 50)
            print("✗ 迁移过程中出现错误")
            print("=" * 50)
            sys.exit(1)
            
    except Exception as e:
        print(f"\n✗ 迁移失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
