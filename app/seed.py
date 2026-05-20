from datetime import date, time
from app.database import SessionLocal, engine
from app import models


def seed_database():
    db = SessionLocal()
    try:
        print("Purging old data and restarting seed process...")
        # Optional: clear tables to avoid duplicate key issues during re-seeding
        db.query(models.LeaveRequest).delete()
        db.query(models.Attendance).delete()
        db.query(models.User).delete()
        db.query(models.Employee).delete()
        db.query(models.Role).delete()
        db.query(models.Department).delete()

        print("Inserting fresh relational database records...")

        # 1. POPULATE DEPARTMENTS
        depts = {
            "IT": models.Department(department_name="Information Technology",
                                    description="Software development and infrastructure."),
            "HR": models.Department(department_name="Human Resources",
                                    description="Talent acquisition and employee welfare."),
            "FIN": models.Department(department_name="Finance",
                                     description="Payroll, accounting, and financial planning.")
        }
        db.add_all(depts.values())
        db.flush()  # Locks IDs in place

        # 2. POPULATE ROLES
        roles = {
            "Admin": models.Role(role_name="Admin", permissions="All Access"),
            "Manager": models.Role(role_name="Manager", permissions="Department Read/Write"),
            "Staff": models.Role(role_name="Staff", permissions="Standard Profile Access")
        }
        db.add_all(roles.values())
        db.flush()

        # 3. POPULATE EMPLOYEES (A mix of departments, roles, and statuses)
        employees_data = [
            {"first_name": "Rizza Joy", "last_name": "Aradillos", "email": "joy.aradillos@company.com", "phone": "+123456781",
             "address": "New York", "hire_date": date(2023, 1, 15), "salary": 95000.00, "status": "Active",
             "dept": "IT", "role": "Admin"},
            {"first_name": "Esper", "last_name": "Mandigma", "email": "esper.mandigma@company.com", "phone": "+123456782",
             "address": "Chicago", "hire_date": date(2023, 6, 1), "salary": 82000.00, "status": "Active", "dept": "IT",
             "role": "Manager"},
            {"first_name": "CJ", "last_name": "Pizon", "email": "cj.pizon@company.com", "phone": "+123456783",
             "address": "Austin", "hire_date": date(2024, 2, 10), "salary": 60000.00, "status": "Active", "dept": "IT",
             "role": "Staff"},
            {"first_name": "Lucerys", "last_name": "Velaryon", "email": "luke.velaryon@company.com", "phone": "+123456784",
             "address": "Los Angeles", "hire_date": date(2022, 11, 20), "salary": 90000.00, "status": "Active",
             "dept": "HR", "role": "Manager"},
            {"first_name": "Aemond", "last_name": "Targayen", "email": "one.eyed@company.com", "phone": "+123456785",
             "address": "Boston", "hire_date": date(2024, 5, 1), "salary": 55000.00, "status": "Active", "dept": "HR",
             "role": "Staff"},
            {"first_name": "Fiona", "last_name": "Palacios", "email": "fiona.g@company.com", "phone": "+123456786",
             "address": "Chicago", "hire_date": date(2023, 3, 12), "salary": 78000.00, "status": "Inactive",
             "dept": "FIN", "role": "Manager"},
            {"first_name": "Peter", "last_name": "Parker", "email": "pparkour.c@company.com", "phone": "+123456787",
             "address": "Miami", "hire_date": date(2025, 1, 8), "salary": 65000.00, "status": "Active", "dept": "FIN",
             "role": "Staff"},
        ]

        created_employees = []
        for emp in employees_data:
            new_emp = models.Employee(
                first_name=emp["first_name"],
                last_name=emp["last_name"],
                email=emp["email"],
                phone=emp["phone"],
                address=emp["address"],
                hire_date=emp["hire_date"],
                salary=emp["salary"],
                status=emp["status"],
                department_id=depts[emp["dept"]].department_id,
                role_id=roles[emp["role"]].role_id
            )
            db.add(new_emp)
            created_employees.append(new_emp)

        db.flush()

        # 4. POPULATE RELATED ATTENDANCE LOGS (For Alice and Bob)
        attendance_logs = [
            models.Attendance(employee_id=created_employees[0].employee_id, date=date(2026, 5, 19), time_in=time(8, 45),
                              time_out=time(17, 0), status="Present"),
            models.Attendance(employee_id=created_employees[1].employee_id, date=date(2026, 5, 19), time_in=time(9, 15),
                              time_out=time(17, 30), status="Late")
        ]
        db.add_all(attendance_logs)

        # 5. POPULATE RELATED LEAVE REQUESTS (For Charlie)
        leave_req = models.LeaveRequest(
            employee_id=created_employees[2].employee_id,
            leave_type="Medical",
            start_date=date(2026, 6, 1),
            end_date=date(2026, 6, 3),
            reason="Routine wisdom teeth extraction surgery.",
            status="Pending"
        )
        db.add(leave_req)

        # Commit everything to XAMPP permanently
        db.commit()
        print("Success! Relational data fully seeded.")

    except Exception as e:
        print(f"Error occurred: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()