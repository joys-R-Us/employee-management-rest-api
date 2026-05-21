from fastapi import FastAPI, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional, List
from app.database import engine, get_db
from app import models, schemas

# Initialize FastAPI App
app = FastAPI(title="Employee Management REST API")

# Ensure database tables are created automatically on startup
models.Base.metadata.create_all(bind=engine)


# ==========================================
# 1. READ ALL EMPLOYEES (With Search & Pagination)
# ==========================================
@app.get("/employees", response_model=List[schemas.EmployeeResponse], status_code=status.HTTP_200_OK)
def get_employees(
        db: Session = Depends(get_db),
        search: Optional[str] = Query(None),
        department_id: Optional[int] = Query(None),
        skip: int = Query(0),
        limit: int = Query(10)
):
    query = db.query(models.Employee)
    if search:
        query = query.filter(
            (models.Employee.first_name.ilike(f"%{search}%")) |
            (models.Employee.last_name.ilike(f"%{search}%"))
        )
    if department_id:
        query = query.filter(models.Employee.department_id == department_id)
    return query.offset(skip).limit(limit).all()


# ==========================================
# 2. CREATE AN EMPLOYEE (POST) - Forces Exact Swagger Key Ordering
# ==========================================
@app.post(
    "/employees",
    response_model=schemas.EmployeeResponse,
    status_code=status.HTTP_201_CREATED,
    openapi_extra={
        "requestBody": {
            "content": {
                "application/json": {
                    "example": {
                        "first_name": "User",
                        "last_name": "Testing",
                        "email": "user.testing@company.com",
                        "phone": "+9876543210",
                        "address": "456 Boulevard St, New Jersey",
                        "hire_date": "2026-05-22",
                        "salary": 20000,
                        "status": "Active",
                        "department_id": 1,
                        "role_id": 1,
                        "employee_id": 0
                    }
                }
            }
        }
    }
)
def create_employee(employee: schemas.EmployeeCreate, db: Session = Depends(get_db)):
    # Verify unique email constraint
    db_employee = db.query(models.Employee).filter(models.Employee.email == employee.email).first()
    if db_employee:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An employee with this email address already exists."
        )

    new_employee = models.Employee(**employee.model_dump())

    try:
        db.add(new_employee)
        db.commit()
        db.refresh(new_employee)
        return new_employee
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database execution error: {str(e)}"
        )


# ==========================================
# 3. READ SINGLE EMPLOYEE BY ID (GET)
# ==========================================
@app.get("/employees/{employee_id}", response_model=schemas.EmployeeResponse, status_code=status.HTTP_200_OK)
def get_employee_by_id(employee_id: int, db: Session = Depends(get_db)):
    employee = db.query(models.Employee).filter(models.Employee.employee_id == employee_id).first()
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee with ID {employee_id} was not found."
        )
    return employee


# ==========================================
# 4. UPDATE AN EMPLOYEE RECORD (PUT)
# ==========================================
@app.put("/employees/{employee_id}", response_model=schemas.EmployeeResponse, status_code=status.HTTP_200_OK)
def update_employee(employee_id: int, updated_data: schemas.EmployeeUpdate, db: Session = Depends(get_db)):
    employee_query = db.query(models.Employee).filter(models.Employee.employee_id == employee_id)
    employee = employee_query.first()

    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cannot update. Employee with ID {employee_id} does not exist."
        )

    try:
        employee_query.update(updated_data.model_dump(), synchronize_session=False)
        db.commit()
        db.refresh(employee)
        return employee
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update database record: {str(e)}"
        )


# ==========================================
# 5. DELETE AN EMPLOYEE RECORD (DELETE)
# ==========================================
@app.delete("/employees/{employee_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_employee(employee_id: int, db: Session = Depends(get_db)):
    employee = db.query(models.Employee).filter(models.Employee.employee_id == employee_id).first()

    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cannot delete. Employee with ID {employee_id} does not exist."
        )

    try:
        db.delete(employee)
        db.commit()
        return None  # HTTP 204 Content requires empty body mapping
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to remove employee record: {str(e)}"
        )