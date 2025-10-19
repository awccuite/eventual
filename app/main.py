from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from uuid import uuid4
from app.database import engine, Base, get_db
from app.routers import tasks, users
from app.models.classes import User, Task
from app.tests import (
    UserCreateTest, UserReadTest, UserUpdateTest, UserDeleteTest, UserListTest,
    TaskCreateTest, TaskReadTest, TaskUpdateTest, TaskDeleteTest, TaskListTest, 
    TaskSummaryTest, TaskFilterByUserTest
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
        # SUCCESS TESTS
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
        TaskFilterByUserTest(),
        
        # Cleanup
        TaskDeleteTest(),
        UserDeleteTest(),
    ]
    
    # Run success tests
    results = []
    for test in test_suite:
        result = test.run(db, context)
        results.append(result)
    
    # Clear context for error tests
    context.clear()
    
    # ERROR TESTS - Same classes, but expecting errors
    error_test_suite = [
        UserReadTest(
            expected_email="",
            expect_error=True,
            expected_error_msg="No user_id in context"
        ),
        UserUpdateTest(
            new_name="Should Fail",
            expect_error=True,
            expected_error_msg="No user_id in context"
        ),
        UserDeleteTest(
            expect_error=True,
            expected_error_msg="No user_id in context"
        ),
        TaskReadTest(
            expected_title="",
            expect_error=True,
            expected_error_msg="No task_id in context"
        ),
        TaskUpdateTest(
            new_status=0,
            expect_error=True,
            expected_error_msg="No task_id in context"
        ),
        TaskDeleteTest(
            expect_error=True,
            expected_error_msg="No task_id in context"
        ),
        
        # Duplicate email test
        UserCreateTest(
            expected_name="Unique User",
            expected_email="unique@example.com",
            expected_phone="555-UNIQ"
        ),
        UserCreateTest(
            expected_name="Duplicate",
            expected_email="unique@example.com",
            expected_phone="555-DUPE",
            expect_error=True,
            expected_error_msg="duplicate key value"
        ),
        UserDeleteTest(),  # Cleanup
        
        # Invalid user_id for task
        TaskCreateTest(
            expected_title="Bad Task",
            expected_status=0,
            expect_error=True,
            expected_error_msg="No user_id in context"
        ),
    ]
    
    # Run error tests
    for test in error_test_suite:
        result = test.run(db, context)
        results.append(result)
    
    # Build response
    response = {
        "status": "running",
        "tests": results,
        "errors": []
    }
    
    # Collect errors
    for test_result in results:
        if test_result["status"] == "ERROR":
            response["errors"].append({
                "test": test_result["name"],
                "error": test_result["error"]
            })
    
    # Calculate summary
    passed = sum(1 for test in results if test["status"] == "PASS")
    failed = sum(1 for test in results if test["status"] == "FAIL")
    errors = sum(1 for test in results if test["status"] == "ERROR")
    total = len(results)
    
    response["summary"] = {
        "total": total,
        "passed": passed,
        "failed": failed,
        "errors": errors
    }
    
    if errors > 0:
        response["status"] = "ERROR"
    elif failed > 0:
        response["status"] = f"PARTIAL: {passed}/{total} PASSED"
    else:
        response["status"] = "ALL TESTS PASSED"
    
    return response
