from sqlalchemy import Column, Integer, String, Date, DateTime, Time, Text, ForeignKey, DECIMAL, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


# =========================
# Department Model
# =========================
class Department(Base):
    __tablename__ = "departments"

    department_id = Column(Integer, primary_key=True, index=True)
    department_name = Column(String(100), nullable=False, unique=True)
    description = Column(Text)

    # Relationship back-link to access employees in a department
    employees = relationship("Employee", back_populates="department")


# =========================
# Role Model (For Access Control)
# =========================
class Role(Base):
    __tablename__ = "roles"

    role_id = Column(Integer, primary_key=True, index=True)
    role_name = Column(String(50), nullable=False, unique=True)
    permissions = Column(Text)

    employees = relationship("Employee", back_populates="role")


# =========================
# Employee Model (Core Table)
# =========================
class Employee(Base):
    __tablename__ = "employees"

    employee_id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, nullable=False)
    phone = Column(String(20))
    address = Column(Text)
    hire_date = Column(Date, nullable=False)
    salary = Column(DECIMAL(10, 2), nullable=False)

    status = Column(
        Enum("Active", "Inactive", name="employee_status"),
        default="Active"
    )
    created_at = Column(DateTime, default=datetime.utcnow)

    # Foreign Keys mapping to other tables
    department_id = Column(Integer, ForeignKey("departments.department_id"))
    role_id = Column(Integer, ForeignKey("roles.role_id"))

    # Relationships to enable easy cross-table querying
    department = relationship("Department", back_populates="employees")
    role = relationship("Role", back_populates="employees")

    attendance_records = relationship("Attendance", back_populates="employee", cascade="all, delete")
    leave_requests = relationship("LeaveRequest", back_populates="employee", cascade="all, delete")
    user_account = relationship("User", back_populates="employee", uselist=False)


# =========================
# Attendance Model
# =========================
class Attendance(Base):
    __tablename__ = "attendance"

    attendance_id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.employee_id"), nullable=False)
    date = Column(Date, nullable=False)
    time_in = Column(Time)
    time_out = Column(Time)

    status = Column(
        Enum("Present", "Absent", "Late", name="attendance_status"),
        default="Present"
    )

    employee = relationship("Employee", back_populates="attendance_records")


# =========================
# Leave Request Model
# =========================
class LeaveRequest(Base):
    __tablename__ = "leave_requests"

    leave_id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.employee_id"), nullable=False)
    leave_type = Column(String(50), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    reason = Column(Text)

    status = Column(
        Enum("Pending", "Approved", "Rejected", name="leave_status"),
        default="Pending"
    )

    employee = relationship("Employee", back_populates="leave_requests")


# =========================
# User Authentication Model
# =========================
class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)

    employee_id = Column(Integer, ForeignKey("employees.employee_id"), unique=True)

    employee = relationship("Employee", back_populates="user_account")