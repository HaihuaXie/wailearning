from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth import get_current_active_user
from app.course_access import (
    ensure_course_access,
    get_accessible_courses_query,
    get_enrolled_students,
    remove_optional_course_enrollment,
    sync_course_enrollments,
)
from app.database import get_db
from app.models import Class, CourseEnrollment, Subject, User, UserRole
from app.schemas import (
    CourseEnrollmentResponse,
    SubjectCreate,
    SubjectResponse,
    SubjectUpdate,
)


router = APIRouter(prefix="/api/subjects", tags=["课程管理"])


def _serialize_course(course: Subject, db: Session) -> SubjectResponse:
    student_count = db.query(CourseEnrollment).filter(CourseEnrollment.subject_id == course.id).count()
    return SubjectResponse(
        id=course.id,
        name=course.name,
        teacher_id=course.teacher_id,
        class_id=course.class_id,
        course_type=course.course_type or "required",
        status=course.status or "active",
        semester=course.semester,
        description=course.description,
        teacher_name=course.teacher.real_name if course.teacher else None,
        class_name=course.class_obj.name if course.class_obj else None,
        student_count=student_count,
        created_at=course.created_at,
    )


def _serialize_enrollment(enrollment: CourseEnrollment) -> CourseEnrollmentResponse:
    return CourseEnrollmentResponse(
        id=enrollment.id,
        subject_id=enrollment.subject_id,
        student_id=enrollment.student_id,
        class_id=enrollment.class_id,
        can_remove=enrollment.can_remove,
        created_at=enrollment.created_at,
        student_name=enrollment.student.name if enrollment.student else None,
        student_no=enrollment.student.student_no if enrollment.student else None,
        class_name=enrollment.class_obj.name if enrollment.class_obj else None,
    )


@router.get("", response_model=List[SubjectResponse])
def get_subjects(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    courses = (
        get_accessible_courses_query(current_user, db)
        .order_by(Subject.status.asc(), Subject.created_at.desc())
        .all()
    )
    return [_serialize_course(course, db) for course in courses]


@router.get("/{subject_id}", response_model=SubjectResponse)
def get_subject(
    subject_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    try:
        course = ensure_course_access(subject_id, current_user, db)
    except ValueError:
        raise HTTPException(status_code=404, detail="Course not found.")
    except PermissionError:
        raise HTTPException(status_code=403, detail="You do not have access to this course.")

    return _serialize_course(course, db)


@router.post("", response_model=SubjectResponse)
def create_subject(
    subject_data: SubjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Only administrators can create courses.")

    class_obj = db.query(Class).filter(Class.id == subject_data.class_id).first()
    if not class_obj:
        raise HTTPException(status_code=400, detail="Class not found.")

    existing = (
        db.query(Subject)
        .filter(
            Subject.name == subject_data.name,
            Subject.class_id == subject_data.class_id,
            Subject.semester == subject_data.semester,
        )
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="A course with the same name already exists for this class and semester.")

    course = Subject(
        name=subject_data.name,
        teacher_id=subject_data.teacher_id,
        class_id=subject_data.class_id,
        course_type=subject_data.course_type,
        status=subject_data.status,
        semester=subject_data.semester,
        description=subject_data.description,
    )
    db.add(course)
    db.flush()
    sync_course_enrollments(course, db)
    db.commit()
    db.refresh(course)
    return _serialize_course(course, db)


@router.put("/{subject_id}", response_model=SubjectResponse)
def update_subject(
    subject_id: int,
    subject_data: SubjectUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Only administrators can update courses.")

    course = db.query(Subject).filter(Subject.id == subject_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found.")

    original_class_id = course.class_id

    for field in ["name", "teacher_id", "class_id", "course_type", "status", "semester", "description"]:
        value = getattr(subject_data, field)
        if value is not None:
            setattr(course, field, value)

    if course.class_id is None:
        raise HTTPException(status_code=400, detail="Course must belong to a class.")

    if course.class_id != original_class_id:
        db.query(CourseEnrollment).filter(CourseEnrollment.subject_id == course.id).delete()

    sync_course_enrollments(course, db)
    db.commit()
    db.refresh(course)
    return _serialize_course(course, db)


@router.delete("/{subject_id}")
def delete_subject(
    subject_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Only administrators can delete courses.")

    course = db.query(Subject).filter(Subject.id == subject_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found.")

    db.query(CourseEnrollment).filter(CourseEnrollment.subject_id == subject_id).delete()
    db.delete(course)
    db.commit()
    return {"message": "Course deleted successfully."}


@router.get("/{subject_id}/students", response_model=List[CourseEnrollmentResponse])
def get_subject_students(
    subject_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    try:
        ensure_course_access(subject_id, current_user, db)
    except ValueError:
        raise HTTPException(status_code=404, detail="Course not found.")
    except PermissionError:
        raise HTTPException(status_code=403, detail="You do not have access to this course.")

    enrollments = get_enrolled_students(subject_id, db)
    return [_serialize_enrollment(enrollment) for enrollment in enrollments]


@router.delete("/{subject_id}/students/{student_id}")
def remove_subject_student(
    subject_id: int,
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    if current_user.role == UserRole.STUDENT:
        raise HTTPException(status_code=403, detail="Students cannot modify course rosters.")

    try:
        ensure_course_access(subject_id, current_user, db)
    except ValueError:
        raise HTTPException(status_code=404, detail="Course not found.")
    except PermissionError:
        raise HTTPException(status_code=403, detail="You do not have access to this course.")

    try:
        removed = remove_optional_course_enrollment(subject_id, student_id, db)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    if not removed:
        raise HTTPException(status_code=404, detail="Course student not found.")

    db.commit()
    return {"message": "Student removed from course successfully."}
