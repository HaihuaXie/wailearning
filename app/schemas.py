from pydantic import BaseModel, field_validator
from typing import Optional, List
from datetime import datetime
from enum import Enum

class UserRole(str, Enum):
    ADMIN = "admin"
    CLASS_TEACHER = "class_teacher"
    TEACHER = "teacher"

class Gender(str, Enum):
    MALE = "male"
    FEMALE = "female"

class AttendanceStatus(str, Enum):
    PRESENT = "present"
    ABSENT = "absent"
    LATE = "late"
    LEAVE = "leave"

class UserBase(BaseModel):
    username: str
    real_name: str
    role: str = "teacher"
    class_id: Optional[int] = None
    
    @field_validator('role', mode='before')
    @classmethod
    def convert_role(cls, v):
        if isinstance(v, UserRole):
            return v.value
        return v

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    username: Optional[str] = None
    real_name: Optional[str] = None
    role: Optional[str] = None
    class_id: Optional[int] = None
    is_active: Optional[bool] = None

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    class_id: Optional[int] = None

    class Config:
        from_attributes = True

class LoginRequest(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class ClassCreate(BaseModel):
    name: str
    grade: int

class ClassUpdate(BaseModel):
    name: Optional[str] = None
    grade: Optional[int] = None

class ClassResponse(BaseModel):
    id: int
    name: str
    grade: int
    created_at: datetime
    student_count: int = 0

    class Config:
        from_attributes = True

class StudentBase(BaseModel):
    name: str
    student_no: str
    gender: Gender
    phone: Optional[str] = None
    parent_phone: Optional[str] = None
    address: Optional[str] = None
    class_id: int

class StudentCreate(StudentBase):
    pass

class StudentUpdate(BaseModel):
    name: Optional[str] = None
    student_no: Optional[str] = None
    gender: Optional[Gender] = None
    phone: Optional[str] = None
    parent_phone: Optional[str] = None
    address: Optional[str] = None
    class_id: Optional[int] = None

class StudentResponse(StudentBase):
    id: int
    teacher_id: Optional[int] = None
    created_at: datetime
    class_name: Optional[str] = None

    class Config:
        from_attributes = True

class StudentListResponse(BaseModel):
    total: int
    data: List[StudentResponse]

class SubjectCreate(BaseModel):
    name: str
    teacher_id: Optional[int] = None

class SubjectUpdate(BaseModel):
    name: Optional[str] = None
    teacher_id: Optional[int] = None

class SubjectResponse(BaseModel):
    id: int
    name: str
    teacher_id: Optional[int] = None

    class Config:
        from_attributes = True

class SemesterCreate(BaseModel):
    name: str
    year: int
    is_current: bool = False

class SemesterUpdate(BaseModel):
    name: Optional[str] = None
    year: Optional[int] = None
    is_current: Optional[bool] = None

class SemesterResponse(BaseModel):
    id: int
    name: str
    year: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class ScoreBase(BaseModel):
    student_id: int
    subject_id: int
    class_id: int
    semester: str
    exam_type: str
    score: float
    exam_date: Optional[str] = None

class ScoreCreate(ScoreBase):
    pass

class ScoreUpdate(BaseModel):
    score: Optional[float] = None
    exam_type: Optional[str] = None
    exam_date: Optional[str] = None

class ScoreResponse(ScoreBase):
    id: int
    student_name: Optional[str] = None
    subject_name: Optional[str] = None
    class_name: Optional[str] = None

    class Config:
        from_attributes = True

class ScoreListResponse(BaseModel):
    total: int
    data: List[ScoreResponse]

class AttendanceBase(BaseModel):
    student_id: int
    class_id: int
    date: str
    status: AttendanceStatus
    remark: Optional[str] = None

class AttendanceCreate(AttendanceBase):
    pass

class AttendanceUpdate(BaseModel):
    status: Optional[AttendanceStatus] = None
    remark: Optional[str] = None

class AttendanceResponse(AttendanceBase):
    id: int
    student_name: Optional[str] = None
    class_name: Optional[str] = None

    class Config:
        from_attributes = True

class AttendanceListResponse(BaseModel):
    total: int
    data: List[AttendanceResponse]

class ClassRanking(BaseModel):
    class_id: int
    class_name: str
    avg_score: float
    rank: int

class DashboardStats(BaseModel):
    total_students: int
    total_classes: int
    total_scores: int = 0
    avg_score: float
    attendance_rate: float = 0.0
    recent_scores: List[ScoreResponse] = []
    class_rankings: List[ClassRanking] = []

class StudentRanking(BaseModel):
    student_id: int
    student_name: str
    class_name: str
    avg_score: float
    rank: int

class OperationLogResponse(BaseModel):
    id: int
    user_id: Optional[int] = None
    username: Optional[str] = None
    action: str
    target_type: str
    target_id: Optional[int] = None
    target_name: Optional[str] = None
    details: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    result: str
    created_at: datetime

    class Config:
        from_attributes = True

class OperationLogListResponse(BaseModel):
    total: int
    data: List[OperationLogResponse]
