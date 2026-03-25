from app.database import SessionLocal, engine
from app.models import User, UserRole, Base
import sys

def migrate():
    db = SessionLocal()
    try:
        # 检查现有用户的角色
        users = db.query(User).all()
        print(f"找到 {len(users)} 个用户")
        
        for user in users:
            print(f"用户: {user.username}, 当前角色: {user.role}")
            
            # 如果角色字段是大写的，转换为小写
            if user.role and user.role.value in ['ADMIN', 'CLASS_TEACHER', 'TEACHER']:
                if user.role.value == 'ADMIN':
                    user.role = UserRole.admin
                    print(f"  -> 更新为 admin")
                elif user.role.value == 'CLASS_TEACHER':
                    user.role = UserRole.class_teacher
                    print(f"  -> 更新为 class_teacher")
                elif user.role.value == 'TEACHER':
                    user.role = UserRole.teacher
                    print(f"  -> 更新为 teacher")
            elif not user.role or user.role.value not in ['admin', 'class_teacher', 'teacher']:
                print(f"  -> 更新为 teacher")
                user.role = UserRole.teacher
            else:
                print(f"  -> 保持不变")
        
        db.commit()
        print("\n迁移完成！")
        
    except Exception as e:
        print(f"迁移失败: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    migrate()
