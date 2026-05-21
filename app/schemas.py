from pydantic import BaseModel, EmailStr, Field
from datetime import date
from typing import Optional
from decimal import Decimal

class EmployeeBase(BaseModel):
    first_name: str = Field(..., max_length=100)
    last_name: str = Field(..., max_length=100)
    email: EmailStr
    phone: Optional[str] = None
    address: Optional[str] = None
    hire_date: date
    salary: Decimal = Field(..., max_digits=10, decimal_places=2, gt=0)
    status: str = Field("Active")
    department_id: Optional[int] = None
    role_id: Optional[int] = None

class EmployeeCreate(EmployeeBase):
    pass

class EmployeeUpdate(EmployeeBase):
    pass

class EmployeeResponse(EmployeeBase):
    employee_id: int

    class Config:
        from_attributes = True