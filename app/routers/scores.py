from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session

from app.auth import get_current_active_user
from app.course_access import ensure_course_access
from app.database import get_db
from app.models import Score, Student, Subject, User, UserRole
from app.routers.classes import get_accessible_class_ids
from app.schemas import ScoreCreate, ScoreListResponse, ScoreResponse, ScoreUpdate


router = APIRouter(prefix="/api/scores", tags=["成绩管理"])


def _ensure_score_write_access(current_user: User):
    if current_user.role == UserRole.STUDENT:
        raise HTTPException(status_code=403, detail="Students cannot modify scores.")


def _serialize_score(score: Score) -> ScoreResponse:
    return ScoreResponse(
        id=score.id,
        student_id=score.student_id,
        subject_id=score.subject_id,
        class_id=score.class_id,
        score=score.score,
        exam_type=score.exam_type,
        exam_date=score.exam_date,
        semester=score.semester,
        created_at=score.created_at,
        student_name=score.student.name if score.student else None,
        subject_name=score.subject.name if score.subject else None,
        class_name=score.class_obj.name if score.class_obj else None,
    )


@router.get("", response_model=ScoreListResponse)
def get_scores(
    class_id: Optional[int] = None,
    student_id: Optional[int] = None,
    subject_id: Optional[int] = None,
    semester: Optional[str] = None,
    exam_type: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    class_ids = get_accessible_class_ids(current_user, db)
    query = db.query(Score).filter(Score.class_id.in_(class_ids))

    if class_id:
        if class_id not in class_ids:
            raise HTTPException(status_code=403, detail="You do not have access to this class.")
        query = query.filter(Score.class_id == class_id)
    if student_id:
        query = query.filter(Score.student_id == student_id)
    if subject_id:
        ensure_course_access(subject_id, current_user, db)
        query = query.filter(Score.subject_id == subject_id)
    if semester:
        query = query.filter(Score.semester == semester)
    if exam_type:
        query = query.filter(Score.exam_type == exam_type)

    total = query.count()
    scores = query.order_by(Score.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return ScoreListResponse(total=total, data=[_serialize_score(score) for score in scores])


@router.post("", response_model=ScoreResponse)
def create_score(
    score_data: ScoreCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    _ensure_score_write_access(current_user)
    class_ids = get_accessible_class_ids(current_user, db)
    if score_data.class_id not in class_ids:
        raise HTTPException(status_code=403, detail="You do not have access to this class.")

    student = db.query(Student).filter(Student.id == score_data.student_id).first()
    if not student or student.class_id != score_data.class_id:
        raise HTTPException(status_code=400, detail="Student not found in the selected class.")

    subject = db.query(Subject).filter(Subject.id == score_data.subject_id).first()
    if not subject:
        raise HTTPException(status_code=400, detail="Course not found.")
    if subject.class_id and subject.class_id != score_data.class_id:
        raise HTTPException(status_code=400, detail="The selected course does not belong to this class.")

    score = Score(
        student_id=score_data.student_id,
        subject_id=score_data.subject_id,
        class_id=score_data.class_id,
        score=score_data.score,
        exam_type=score_data.exam_type,
        exam_date=score_data.exam_date,
        semester=score_data.semester,
    )
    db.add(score)
    db.commit()
    db.refresh(score)
    return _serialize_score(score)


@router.put("/{score_id}", response_model=ScoreResponse)
def update_score(
    score_id: int,
    score_data: ScoreUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    _ensure_score_write_access(current_user)
    score = db.query(Score).filter(Score.id == score_id).first()
    if not score:
        raise HTTPException(status_code=404, detail="Score not found.")

    class_ids = get_accessible_class_ids(current_user, db)
    if score.class_id not in class_ids:
        raise HTTPException(status_code=403, detail="You do not have access to this score.")

    if score_data.score is not None:
        score.score = score_data.score
    if score_data.exam_type is not None:
        score.exam_type = score_data.exam_type
    if score_data.semester is not None:
        score.semester = score_data.semester
    if score_data.exam_date is not None:
        score.exam_date = score_data.exam_date

    db.commit()
    db.refresh(score)
    return _serialize_score(score)


@router.delete("/{score_id}")
def delete_score(
    score_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    _ensure_score_write_access(current_user)
    score = db.query(Score).filter(Score.id == score_id).first()
    if not score:
        raise HTTPException(status_code=404, detail="Score not found.")

    class_ids = get_accessible_class_ids(current_user, db)
    if score.class_id not in class_ids:
        raise HTTPException(status_code=403, detail="You do not have access to this score.")

    db.delete(score)
    db.commit()
    return {"message": "Score deleted successfully."}


@router.get("/student/{student_id}")
def get_student_scores(
    student_id: int,
    semester: Optional[str] = None,
    subject_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found.")

    class_ids = get_accessible_class_ids(current_user, db)
    if student.class_id not in class_ids:
        raise HTTPException(status_code=403, detail="You do not have access to this student.")

    query = db.query(Score).filter(Score.student_id == student_id)
    if semester:
        query = query.filter(Score.semester == semester)
    if subject_id:
        ensure_course_access(subject_id, current_user, db)
        query = query.filter(Score.subject_id == subject_id)

    scores = query.all()
    return [
        {
            "id": score.id,
            "subject_id": score.subject_id,
            "subject_name": score.subject.name if score.subject else None,
            "score": score.score,
            "exam_type": score.exam_type,
            "semester": score.semester,
        }
        for score in scores
    ]


@router.post("/batch")
async def create_scores_batch(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    _ensure_score_write_access(current_user)
    import json

    body = await request.body()
    body_str = body.decode("utf-8").replace("\x00", "").replace("\ufeff", "")

    try:
        data = json.loads(body_str)
        scores_list = data.get("scores", []) if isinstance(data, dict) else data
    except Exception as exc:
        return {"success": 0, "failed": 1, "errors": [f"JSON parse error: {exc}"]}

    if not scores_list:
        return {"success": 0, "failed": 0, "errors": ["No valid score data found."]}

    class_ids = get_accessible_class_ids(current_user, db)
    results = []
    errors = []

    for index, score_data in enumerate(scores_list, 1):
        if not isinstance(score_data, dict):
            errors.append(f"Row {index}: invalid record format.")
            continue

        class_id = score_data.get("class_id")
        if class_id not in class_ids:
            errors.append(f"Row {index}: no access to the selected class.")
            continue

        student_no = score_data.get("student_no")
        subject_id = score_data.get("subject_id")
        if not student_no:
            errors.append(f"Row {index}: missing student number.")
            continue
        if not subject_id:
            errors.append(f"Row {index}: missing course ID.")
            continue

        student = db.query(Student).filter(Student.student_no == student_no, Student.class_id == class_id).first()
        if not student:
            errors.append(f"Row {index}: student {student_no} not found in class.")
            continue

        subject = db.query(Subject).filter(Subject.id == subject_id).first()
        if not subject:
            errors.append(f"Row {index}: course not found.")
            continue
        if subject.class_id and subject.class_id != class_id:
            errors.append(f"Row {index}: selected course does not belong to this class.")
            continue

        try:
            score_value = float(score_data.get("score"))
        except (TypeError, ValueError):
            errors.append(f"Row {index}: invalid score value.")
            continue

        if score_value < 0 or score_value > 100:
            errors.append(f"Row {index}: score must be between 0 and 100.")
            continue

        exam_date = score_data.get("exam_date")
        if isinstance(exam_date, str) and exam_date:
            try:
                exam_date = datetime.fromisoformat(exam_date.replace("Z", "+00:00"))
            except ValueError:
                exam_date = None

        db.add(
            Score(
                student_id=student.id,
                subject_id=subject_id,
                class_id=class_id,
                score=score_value,
                exam_type=score_data.get("exam_type", "期中考试"),
                exam_date=exam_date,
                semester=score_data.get("semester", ""),
            )
        )
        results.append(f"{student.name}-{subject.name}")

    try:
        db.commit()
    except Exception as exc:
        db.rollback()
        errors.append(f"Database error: {exc}")

    return {"success": len(results), "failed": len(errors), "errors": errors}
