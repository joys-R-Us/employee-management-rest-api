"""Employee routes protected by Admin role."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.oauth2 import get_current_admin

# These imports are expected to exist in the project.
# If your project uses different module paths, adjust accordingly.
from app.db.session import get_db  # type: ignore
from app import models  # type: ignore
from app.models import User  # type: ignore

router = APIRouter()


@router.delete("/employees/{id}")
def delete_employee(
    id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    """Delete an employee.

    Route is protected: ONLY users with role == "Admin" can access it.
    """

    employee = db.query(models.Employee).filter(models.Employee.id == id).first()
    if not employee:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found")

    db.delete(employee)
    db.commit()
    return {"message": "Employee deleted successfully"}

