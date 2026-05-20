from pydantic import BaseModel, EmailStr, Field
from datetime import date
from typing import Optional
from decimal import Decimal

# Base properties shared across creation and updates
class EmployeeBase(BaseModel):
    first_name: str = Field(..., max_length=100, examples=["John"])
    last_name: str = Field(..., max_length=100, examples=["Doe"])
    email: EmailStr = Field(..., examples=["john.doe@company.com"])
    phone: Optional[str] = Field(None, max_length=20, examples=["+123456789"])
    address: Optional[str] = Field(None, examples=["123 Main St, New York"])
    hire_date: date
    salary: Decimal = Field(..., max_digits=10, decimal_places=2, gt=0)
    status: str = Field("Active", examples=["Active", "Inactive"])
    department_id: Optional[int] = None
    role_id: Optional[int] = None

# Model used when creating an employee (POST)
class EmployeeCreate(EmployeeBase):
    pass

# Model used when updating an employee (PUT)
class EmployeeUpdate(EmployeeBase):
    pass

# Model used for API Responses (GET/POST/PUT)
class EmployeeResponse(EmployeeBase):
    employee_id: int

    class Config:
        from_attributes = True