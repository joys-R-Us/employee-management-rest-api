from fastapi import FastAPI, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional, List  # <-- FIXED: Added Optional here
from app.database import engine, get_db
from app import models, schemas

app = FastAPI(title="Employee Management REST API")

models.Base.metadata.create_all(bind=engine)


@app.get("/")
def home():
    return {"status": "Online", "database": "Connected"}


# Upgraded Employee Route with Search, Filtering, and Pagination built-in
# Added response_model=List[schemas.EmployeeResponse] to match your CRUD structure cleanly
@app.get("/employees", response_model=List[schemas.EmployeeResponse], status_code=status.HTTP_200_OK)
def get_employees(
        db: Session = Depends(get_db),
        search: Optional[str] = Query(None, description="Search by first or last name"),
        department_id: Optional[int] = Query(None, description="Filter by Department ID"),
        skip: int = Query(0, description="Number of records to skip (for pagination)"),
        limit: int = Query(10, description="Max number of records to return per page")
):
    # Start a base query on the Employee table
    query = db.query(models.Employee)

    # 1. Handle Search Filter (if provided)
    if search:
        query = query.filter(
            (models.Employee.first_name.ilike(f"%{search}%")) |
            (models.Employee.last_name.ilike(f"%{search}%"))
        )

    # 2. Handle Department Filtering (if provided)
    if department_id:
        query = query.filter(models.Employee.department_id == department_id)

    # 3. Handle Pagination (Skip and Limit)
    # offset() skips the first X rows, limit() takes only the next Y rows
    employees = query.offset(skip).limit(limit).all()

    return employees


# 1. CREATE an Employee (POST)
@app.post("/employees", response_model=schemas.EmployeeResponse, status_code=status.HTTP_201_CREATED)
def create_employee(employee: schemas.EmployeeCreate, db: Session = Depends(get_db)):
    # Validate unique email constraint
    db_employee = db.query(models.Employee).filter(models.Employee.email == employee.email).first()
    if db_employee:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An employee with this email address already exists."
        )

    # Convert Pydantic model to SQLAlchemy Model
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


# 2. READ a single Employee by ID (GET)
@app.get("/employees/{employee_id}", response_model=schemas.EmployeeResponse, status_code=status.HTTP_200_OK)
def get_employee_by_id(employee_id: int, db: Session = Depends(get_db)):
    employee = db.query(models.Employee).filter(models.Employee.employee_id == employee_id).first()
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee with ID {employee_id} was not found."
        )
    return employee


# 3. UPDATE an Employee record (PUT)
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
        # Perform update matching schema payload fields
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


# 4. DELETE an Employee record (DELETE)
@app.delete("/employees/{employee_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_employee(employee_id: int, db: Session = Depends(get_db)):
    employee_query = db.query(models.Employee).filter(models.Employee.employee_id == employee_id)
    employee = employee_query.first()

    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cannot delete. Employee with ID {employee_id} does not exist."
        )

    try:
        employee_query.delete(synchronize_session=False)
        db.commit()
        return None  # HTTP 204 No Content expects no return body
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to remove employee record: {str(e)}"
        )