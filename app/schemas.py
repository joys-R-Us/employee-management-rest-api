import datetime
from pydantic import BaseModel, ConfigDict, Field, EmailStr
from typing import Optional, List

class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

# --- ATTENDANCE SCHEMAS ---
class AttendanceBase(BaseModel):
    employee_id: int
    status: Optional[str] = "Present"

class AttendanceCreate(AttendanceBase):
    clock_in: datetime.datetime = Field(default_factory=datetime.datetime.now)

class AttendanceOut(BaseSchema):
    id: int
    employee_id: int
    date: datetime.date
    clock_in: datetime.datetime
    clock_out: Optional[datetime.datetime] = None

class AttendanceResponse(BaseSchema):
    id: int
    employee_id: int
    status: str
    clock_in: datetime.datetime
    clock_out: Optional[datetime.datetime] = None

# --- LEAVE REQUEST SCHEMAS ---
class LeaveRequestBase(BaseModel):
    employee_id: int
    start_date: datetime.date
    end_date: datetime.date
    reason: str = Field(..., min_length=10, max_length=500)

class LeaveCreate(LeaveRequestBase):
    pass

class LeaveRequestUpdate(BaseModel):
    status: str = Field(..., pattern="^(Approved|Rejected|Pending)$")

class LeaveResponse(BaseSchema):
    id: int
    employee_id: int
    start_date: datetime.date
    end_date: datetime.date
    reason: str
    status: str

# --- EMPLOYEE SCHEMAS ---
class EmployeeBase(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    department_id: Optional[int] = None

class EmployeeResponse(BaseSchema):
    id: int
    first_name: str
    last_name: str
    email: EmailStr
    department_id: Optional[int] = None
    attendance_logs: List[AttendanceResponse] = []

    model_config = ConfigDict(from_attributes=True)

# AUTH & USER SCHEMAS
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str

class UserResponse(BaseSchema):
    id: int
    username: str
    role: str

class DepartmentBase(BaseModel):
    name: str
    description: Optional[str] = None

class DepartmentOut(BaseSchema):
    id: int
    name: str
    description: Optional[str] = None

class RoleBase(BaseModel):
    title: str

class RoleOut(BaseSchema):
    id: int
    name: str
    department: Optional[DepartmentOut] = None

class EmployeeOut(BaseSchema):
    id: int
    first_name: str
    last_name: str
    email: EmailStr
    department_id: Optional[int] = None
    role_id: Optional[int] = None
