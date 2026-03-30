from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.auth import get_current_active_user
from app.course_access import ensure_course_access
from app.database import get_db
from app.models import Class, Homework, Subject, User, UserRole
from app.routers.classes import get_accessible_class_ids
from app.schemas import HomeworkCreate, HomeworkListResponse, HomeworkResponse, HomeworkUpdate


router = APIRouter(prefix="/api/homeworks", tags=["作业管理"])


def is_teacher(user: User) -> bool:
    return user.role in [UserRole.ADMIN, UserRole.CLASS_TEACHER, UserRole.TEACHER]


def _serialize_homework(homework: Homework) -> HomeworkResponse:
    return HomeworkResponse(
        id=homework.id,
        title=homework.title,
        content=homework.content,
        class_id=homework.class_id,
        subject_id=homework.subject_id,
        due_date=homework.due_date,
        created_by=homework.created_by,
        created_at=homework.created_at,
        updated_at=homework.updated_at,
        class_name=homework.class_obj.name if homework.class_obj else None,
        subject_name=homework.subject.name if homework.subject else None,
        creator_name=homework.creator.real_name if homework.creator else None,
    )


@router.get("", response_model=HomeworkListResponse)
def get_homeworks(
    class_id: Optional[int] = None,
    subject_id: Optional[int] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    query = db.query(Homework)
    allowed_class_ids = get_accessible_class_ids(current_user, db)

    if current_user.role != UserRole.ADMIN:
        if not allowed_class_ids:
            return HomeworkListResponse(total=0, data=[])
        query = query.filter(Homework.class_id.in_(allowed_class_ids))

    if class_id:
        if current_user.role != UserRole.ADMIN and class_id not in allowed_class_ids:
            return HomeworkListResponse(total=0, data=[])
        query = query.filter(Homework.class_id == class_id)

    if subject_id:
        ensure_course_access(subject_id, current_user, db)
        query = query.filter(Homework.subject_id == subject_id)

    total = query.count()
    homeworks = query.order_by(desc(Homework.created_at)).offset((page - 1) * page_size).limit(page_size).all()
    return HomeworkListResponse(total=total, data=[_serialize_homework(homework) for homework in homeworks])


@router.get("/{homework_id}", response_model=HomeworkResponse)
def get_homework(
    homework_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    homework = db.query(Homework).filter(Homework.id == homework_id).first()
    if not homework:
        raise HTTPException(status_code=404, detail="Homework not found.")

    allowed_class_ids = get_accessible_class_ids(current_user, db)
    if current_user.role != UserRole.ADMIN and homework.class_id not in allowed_class_ids:
        raise HTTPException(status_code=403, detail="You do not have access to this homework.")

    if homework.subject_id:
        ensure_course_access(homework.subject_id, current_user, db)

    return _serialize_homework(homework)


@router.post("", response_model=HomeworkResponse)
def create_homework(
    data: HomeworkCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    if not is_teacher(current_user):
        raise HTTPException(status_code=403, detail="Only teachers can create homework.")

    allowed_class_ids = get_accessible_class_ids(current_user, db)
    if current_user.role != UserRole.ADMIN and data.class_id not in allowed_class_ids:
        raise HTTPException(status_code=403, detail="You do not have access to this class.")

    class_obj = db.query(Class).filter(Class.id == data.class_id).first()
    if not class_obj:
        raise HTTPException(status_code=404, detail="Class not found.")

    if data.subject_id:
        course = ensure_course_access(data.subject_id, current_user, db)
        if course.class_id and course.class_id != data.class_id:
            raise HTTPException(status_code=400, detail="The selected course does not belong to this class.")

    homework = Homework(
        title=data.title,
        content=data.content,
        class_id=data.class_id,
        subject_id=data.subject_id,
        due_date=data.due_date,
        created_by=current_user.id,
    )
    db.add(homework)
    db.commit()
    db.refresh(homework)
    return _serialize_homework(homework)


@router.put("/{homework_id}", response_model=HomeworkResponse)
def update_homework(
    homework_id: int,
    data: HomeworkUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    if not is_teacher(current_user):
        raise HTTPException(status_code=403, detail="Only teachers can update homework.")

    homework = db.query(Homework).filter(Homework.id == homework_id).first()
    if not homework:
        raise HTTPException(status_code=404, detail="Homework not found.")

    allowed_class_ids = get_accessible_class_ids(current_user, db)
    if current_user.role != UserRole.ADMIN and homework.class_id not in allowed_class_ids:
        raise HTTPException(status_code=403, detail="You do not have access to this homework.")

    if data.subject_id is not None:
        course = ensure_course_access(data.subject_id, current_user, db)
        if course.class_id and course.class_id != homework.class_id:
            raise HTTPException(status_code=400, detail="The selected course does not belong to this class.")

    if data.title is not None:
        homework.title = data.title
    if data.content is not None:
        homework.content = data.content
    if data.subject_id is not None:
        homework.subject_id = data.subject_id
    if data.due_date is not None:
        homework.due_date = data.due_date

    db.commit()
    db.refresh(homework)
    return _serialize_homework(homework)


@router.delete("/{homework_id}")
def delete_homework(
    homework_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    if not is_teacher(current_user):
        raise HTTPException(status_code=403, detail="Only teachers can delete homework.")

    homework = db.query(Homework).filter(Homework.id == homework_id).first()
    if not homework:
        raise HTTPException(status_code=404, detail="Homework not found.")

    allowed_class_ids = get_accessible_class_ids(current_user, db)
    if current_user.role != UserRole.ADMIN and homework.class_id not in allowed_class_ids:
        raise HTTPException(status_code=403, detail="You do not have access to this homework.")

    db.delete(homework)
    db.commit()
    return {"message": "Homework deleted successfully."}
