from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from app.database import engine, Base, get_db
from app.routers import tasks, users
from app.models.classes import User, Task
from app.tests import (
    UserCreateTest, UserReadTest, UserUpdateTest, UserDeleteTest, UserListTest,
    TaskCreateTest, TaskReadTest, TaskUpdateTest, TaskDeleteTest, TaskListTest, TaskSummaryTest
)

# Create database tables
Base.metadata.create_all(bind=engine)
app = FastAPI(title="Eventual API", version="1.0.0")

# Include routers
app.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
app.include_router(users.router, prefix="/users", tags=["users"])

@app.get("/")
def read_root():
    return {"message": "Welcome to Eventual API"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

# Endpoint to run unit tests
@app.get("/test")
def run_tests(db: Session = Depends(get_db)):
    context = {}
    
    test_suite = [
        UserCreateTest(
            expected_name="Test User",
            expected_email="test@example.com",
            expected_phone="555-TEST"
        ),
        UserReadTest(expected_email="test@example.com"),
        UserUpdateTest(new_name="Updated Test User"),
        UserListTest(min_expected=1),
        
        TaskCreateTest(
            expected_title="Test Task",
            expected_status=0,
            expected_idm_key="TEST-001"
        ),
        TaskReadTest(expected_title="Test Task"),
        TaskUpdateTest(new_status=2),
        TaskListTest(min_expected=1),
        TaskSummaryTest(),
        
        TaskDeleteTest(),
        UserDeleteTest(),
    ]
    
    results = {
        "status": "running",
        "tests": [],
        "errors": []
    }
    
    for test in test_suite:
        try:
            test_result = test.run(db, context)
            results["tests"].append(test_result)
            
            if test_result["status"] == "ERROR":
                results["errors"].append({
                    "test": test_result["name"],
                    "error": test_result["error"]
                })
        except Exception as e:
            results["errors"].append({
                "test": test.name,
                "error": str(e)
            })
    
    passed = sum(1 for test in results["tests"] if test["status"] == "PASS")
    failed = sum(1 for test in results["tests"] if test["status"] == "FAIL")
    errors = sum(1 for test in results["tests"] if test["status"] == "ERROR")
    total = len(results["tests"])
    
    results["summary"] = {
        "total": total,
        "passed": passed,
        "failed": failed,
        "errors": errors
    }
    
    if errors > 0:
        results["status"] = "ERROR"
    elif failed > 0:
        results["status"] = f"PARTIAL: {passed}/{total} PASSED"
    else:
        results["status"] = "ALL TESTS PASSED"
    
    return results
