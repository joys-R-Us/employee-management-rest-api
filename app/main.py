from fastapi import FastAPI, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.database import engine, get_db
from app import models

app = FastAPI(title="Employee Management REST API")

models.Base.metadata.create_all(bind=engine)


@app.get("/")
def home():
    return {"status": "Online", "database": "Connected"}


# Upgraded Employee Route with Search, Filtering, and Pagination built-in
@app.get("/employees")
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