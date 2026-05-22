import datetime

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
import json, os
import bcrypt

from app import models, schemas, database
from app.database import engine, get_db

# Initialize database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Internal Employee Management System")

# Security Configuration
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# --- SECURITY HELPERS ---

def verify_password(plain_password, hashed_password):
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def get_password_hash(password: str):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    # We use 'token' here to find the user, satisfying the 'unused' warning
    user = db.query(models.User).filter(models.User.username == token).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication"
        )
    return user

def admin_only(current_user: models.User = Depends(get_current_user)):
    # Logic uses 'current_user', satisfying the 'unused' warning
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return current_user

# --- AUTH & USER MANAGEMENT ---

@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == form_data.username).first()

    # 1. Check if user exists
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    # 2. Verify hashed password
    password_bytes = form_data.password.encode('utf-8')
    hash_bytes = user.password_hash.encode('utf-8')

    if not bcrypt.checkpw(password_bytes, hash_bytes):
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    return {"access_token": user.username, "token_type": "bearer"}

@app.post("/register", response_model=schemas.UserResponse, tags=["Admin Only"])
def register_user(user_data: schemas.UserCreate, db: Session = Depends(database.get_db), _=Depends(admin_only)):
    hashed_pwd = get_password_hash(user_data.password)
    new_user = models.User(username=user_data.username, password_hash=hashed_pwd)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# --- SYSTEM OPERATIONS (THE JSON REQUIREMENT) ---

@app.post("/system/sync-all", tags=["System"])
def sync_all_data(db: Session = Depends(get_db), _user: models.User = Depends(admin_only)):
    file_path = "app/internal_records.json"

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    with open(file_path, "r") as f:
        employees_list = json.load(f)

    try:
        for emp_data in employees_list:
            # Check if employee already exists by email
            db_emp = db.query(models.Employee).filter(models.Employee.email == emp_data["email"]).first()

            if not db_emp:
                new_employee = models.Employee(
                    first_name=emp_data.get("first_name"),
                    last_name=emp_data.get("last_name"),
                    email=emp_data.get("email"),
                    # Mapping the JSON string "1" to an Integer 1
                    department_id=int(emp_data.get("department")),
                    role_id=int(emp_data.get("role"))
                )
                db.add(new_employee)

        db.commit()
        return {"message": f"Successfully synced {len(employees_list)} employees to the database."}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Sync Error: {str(e)}")

# --- CORE MODULES (CRUD) ---

@app.get("/employees", response_model=list[schemas.EmployeeOut], tags=["Organization"])
def get_employees(db: Session = Depends(get_db), _user: models.User = Depends(get_current_user)):
    return db.query(models.Employee).all()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)

@app.get("/departments", tags=["Organization"])
def get_departments(db: Session = Depends(database.get_db), _=Depends(get_current_user)):
    return db.query(models.Department).all()

@app.post("/attendance", tags=["Logs"])
def log_attendance(record: schemas.AttendanceCreate, db: Session = Depends(database.get_db), _=Depends(get_current_user)):
    new_entry = models.Attendance(**record.model_dump())
    db.add(new_entry)
    db.commit()
    return {"message": "Attendance recorded."}


@app.post("/attendance/clock-out", tags=["Logs"])
def clock_out(employee_id: int, db: Session = Depends(get_db)):
    # 1. Find today's record
    # Use datetime.date.today()
    today_date = datetime.date.today()

    attendance_record = db.query(models.Attendance).filter(
        models.Attendance.employee_id == employee_id,
        models.Attendance.date == today_date,
        models.Attendance.clock_out == None
    ).first()

    if not attendance_record:
        raise HTTPException(
            status_code=400,
            detail="No active clock-in record found for today."
        )

    # 2. Update the clock_out time
    # Use datetime.datetime.now()
    attendance_record.clock_out = datetime.datetime.now()
    db.commit()

    return {"message": "Clocked out successfully", "time": attendance_record.clock_out}

@app.post("/leave-requests", tags=["Logs"])
def request_leave(leave: schemas.LeaveCreate, db: Session = Depends(database.get_db), _=Depends(get_current_user)):
    new_leave = models.LeaveRequest(**leave.model_dump())
    db.add(new_leave)
    db.commit()
    return {"message": "Leave request submitted."}

@app.get("/roles", tags=["Organization"])
def list_roles(db: Session = Depends(database.get_db), _=Depends(admin_only)):
    return db.query(models.Role).all()