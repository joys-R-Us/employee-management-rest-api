# employee-management-rest-api

**Project Overview**

  The Employee Management REST API is a backend system developed for managing company employee information through RESTful API endpoints. This project is designed as a scenario-based laboratory activity focusing on Python development, API implementation, database management, authentication, testing, and Git version control.
The system allows administrations to manage employee and department records while demonstrating proper collaboration workflow using Git and Github.

**Scenario** 

  A software company requires a simple internal backend system that exposes employee data through an API. The development team is tasked with creating and maintaining the system while following proper version control practices using Git and Github. 

**Objectives** 
* **Production Architecture**: Develop a Python-based REST API using FastAPI.
* **Data Integrity**: Implement complete relational CRUD workflows for Employees, Departments, and Roles.
* **Data Consistency**: Enforce strict data type checking and input verification using Pydantic schemas.
* **Secure Access Layer**: Apply OAuth2 authentication, strict password hashing (`bcrypt`), and Role-Based Access Control (RBAC).
* **System Synchronization**: Handle structured storage parsing via local JSON seed operations.
* **Git Lifecycle Compliance**: Demonstrate industry-standard Git branching, pull request lifecycle steps, and conflict resolution management.

**Features** 
* **Role-Based Access Control (RBAC):** Restricts dangerous system operations and administrative actions (like registrations and role updates) to validated Admin credentials.
* **Comprehensive Attendance Logging**: Tracks real-time clock-in markers, checks matching system constraints, and tracks state variables (e.g., `Present`, `Late`).
* **Automated Shift Closing**: Exposes persistent state queries using optimized filtering logic for seamless daily checkout loops.
* **Bulk Serialization Engine**: Reads external legacy storage profiles (`internal_records.json`) to programmatically verify and ingest structural data records safely.
* **Relational Database Engine**: Uses MySQL connection pools handled via SQLAlchemy transactional contexts.

**Tools & Technology**

**Category**                 |       **Technology**

Programming Language         |       Python
Framework Architecture       |       FastAPI
Data Validation Layer        |       Pydantic v2
ORM / Database Engine        |       SQLAlchemy & PyMySQL
Database Server              |       MySQL
Authentication Module        |       OAuth2 Password Bearer & Bcrypt
Version Control              |       Git & GitHub


**Project Structure** 
employee-management-rest-api/
│
├── app/
│   ├── seed.py              # Standalone administrative execution script to seed initial base roles/users 
│   ├── database.py          # MySQL Engine connection pooling and session context
│   ├── models.py            # Declarative SQLAlchemy Database Blueprints
│   ├── schemas.py           # Pydantic validation schemas & API contracts
│   └── internal_records.json# Local JSON seed data packet for bulk synchronization
│
├── venv/                    # Local isolated execution environment
├── main.py                  # Core Application entrypoint, routers, and server execution
├── requirements.txt         # Package dependencies inventory
└── README.md                # Project architecture documentation


**API Endpoints Matrix**
Authentication & Access Control
* POST /login - Public access point. Exchanges validated credentials for secure Bearer strings.
* POST /register - Admin Only. Spawns persistent database user logins with encrypted passwords.

**System & Integration Operations**
* POST /system/sync-all - Admin Only. Ingests and normalizes raw properties from local JSON arrays directly into MySQL.

**Corporate Layout & Structural Queries**
* GET /employees - Returns structural details containing linked assignment IDs.
* GET /departments - Lists corporate organizational blocks.
* GET /roles - Admin Only. Returns configured specialized job descriptions.

**Attendance & Log Module**
* POST /attendance - Enforces real-time tracking entries based on model structural properties.
* POST /attendance/clock-out - Locates matching daily logs to commit persistent clock-out timestamps.
* POST /leave-requests - Logs temporary time-off requests under explicit text length bounds.

**Relational Database Schema** 
**users Table** 
Tracks access keys, credential records, and security roles.
* id (INT, Primary Key, Auto-Increment)
* username (VARCHAR, Unique, Indexed)
* password_hash (VARCHAR)
* role (VARCHAR, Default: "staff")

**employees Table**
Houses personnel entities linked to corporate properties.
* id (INT, Primary Key, Auto-Increment)
* first_name (VARCHAR)
* last_name (VARCHAR)
* email (VARCHAR, Unique, Indexed)
* department_id (INT, Foreign Key -> departments.id)
* role_id (INT, Foreign Key -> roles.id)

**attendance Table**
Tracks real-time operational time logs.
* id (INT, Primary Key, Auto-Increment)
* employee_id (INT, Foreign Key -> employees.id)
* status (VARCHAR, Default: "Present")
* date (DATE)
* clock_in (DATETIME)
* clock_out (DATETIME, Nullable)

**Git Workflow** 

**Branch Architecture**

To guarantee trunk safety and isolate deployment tasks, the team leveraged a modular branch layout:
* main / master - Production-stable, deployment-ready release branch.
* feature/documentation - Dedicated workspace for structural design logs, testing, and documentation tracks.
* dev / specialized topic branches - Isolated feature playgrounds for authentication blocks, endpoint construction, and model binding updates.


**Conflict Resolution Blueprint**

When changes overlapped across main.py and schemas.py, the team applied professional local git mitigation strategies:
* Fetched upstream parity states: git fetch origin
* Pulled structural updates into feature vectors: git pull origin main
* Leveraged IDE-driven 3-pane visual indicators to resolve structural blocks, organize route execution queues, and verify data formatting bounds before staging changes safely.


**API Testing** 

API endpoints are tested using FastAPI.

**Documentation** 

http://127.0.0.1:8000/docs#/ 

**Deliverables** 
* Complete source code
* Github repository
* API documentation
* Database schema
* README documentation
* Git commit history

**License**

This project is intended for educational and laboratory purposes only.
