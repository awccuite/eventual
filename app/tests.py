"""
Unit-like test classes for API testing
Each test class represents a specific operation with expected inputs/outputs
"""
from typing import Any, Dict, Optional
from sqlalchemy.orm import Session
from app.models.classes import User, Task

# BASE TEST CLASS
class BaseTest:
    """Base class for all tests"""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.status = "PENDING"
        self.result = {}
        self.error = None
    
    def run(self, db: Session, context: Dict[str, Any]) -> Dict[str, Any]:
        """Run the test and return result"""
        try:
            self._execute(db, context)
            self.status = "PASS" if self._validate(context) else "FAIL"
        except Exception as e:
            self.status = "ERROR"
            self.error = str(e)
        
        return {
            "name": self.name,
            "description": self.description,
            "status": self.status,
            "result": self.result,
            "error": self.error
        }
    
    def _execute(self, db: Session, context: Dict[str, Any]):
        pass
    
    def _validate(self, context: Dict[str, Any]) -> bool:
        pass

# USER TESTS
class UserCreateTest(BaseTest):
    """Test creating a user"""
    
    def __init__(self, expected_name: str, expected_email: str, expected_phone: str):
        super().__init__(
            name="user_create",
            description="Create a new user and verify attributes"
        )
        self.expected_name = expected_name
        self.expected_email = expected_email
        self.expected_phone = expected_phone
    
    def _execute(self, db: Session, context: Dict[str, Any]):
        user = User(
            name=self.expected_name,
            email=self.expected_email,
            phone_number=self.expected_phone
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        context["test_user_id"] = user.id
        self.result = {
            "user_id": str(user.id),
            "name": user.name,
            "email": user.email
        }
    
    def _validate(self, context: Dict[str, Any]) -> bool:
        return (
            context.get("test_user_id") is not None and
            self.result.get("name") == self.expected_name and
            self.result.get("email") == self.expected_email
        )

class UserReadTest(BaseTest):
    """Test reading a user by ID"""
    
    def __init__(self, expected_email: str):
        super().__init__(
            name="user_read",
            description="Read user by ID and verify data"
        )
        self.expected_email = expected_email
    
    def _execute(self, db: Session, context: Dict[str, Any]):
        user_id = context.get("test_user_id")
        if not user_id:
            raise ValueError("No user_id in context")
        
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("User not found")
        
        self.result = {
            "user_id": str(user.id),
            "name": user.name,
            "email": user.email
        }
    
    def _validate(self, context: Dict[str, Any]) -> bool:
        return self.result.get("email") == self.expected_email

class UserUpdateTest(BaseTest):
    """Test updating a user"""
    
    def __init__(self, new_name: str):
        super().__init__(
            name="user_update",
            description="Update user name and verify change"
        )
        self.new_name = new_name
    
    def _execute(self, db: Session, context: Dict[str, Any]):
        user_id = context.get("test_user_id")
        if not user_id:
            raise ValueError("No user_id in context")
        
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("User not found")
        
        old_name = user.name
        user.name = self.new_name
        db.commit()
        db.refresh(user)
        
        self.result = {
            "old_name": old_name,
            "new_name": user.name
        }
    
    def _validate(self, context: Dict[str, Any]) -> bool:
        return self.result.get("new_name") == self.new_name

class UserDeleteTest(BaseTest):
    """Test deleting a user"""
    
    def __init__(self):
        super().__init__(
            name="user_delete",
            description="Delete user and verify removal"
        )
    
    def _execute(self, db: Session, context: Dict[str, Any]):
        user_id = context.get("test_user_id")
        if not user_id:
            raise ValueError("No user_id in context")
        
        deleted_count = db.query(User).filter(User.id == user_id).delete()
        db.commit()
        
        # Verify deletion
        user = db.query(User).filter(User.id == user_id).first()
        
        self.result = {
            "deleted_count": deleted_count,
            "still_exists": user is not None
        }
    
    def _validate(self, context: Dict[str, Any]) -> bool:
        return (
            self.result.get("deleted_count") == 1 and
            self.result.get("still_exists") is False
        )


class UserListTest(BaseTest):
    """Test listing all users"""
    
    def __init__(self, min_expected: int = 0):
        super().__init__(
            name="user_list",
            description="List all users and verify count"
        )
        self.min_expected = min_expected
    
    def _execute(self, db: Session, context: Dict[str, Any]):
        users = db.query(User).all()
        self.result = {
            "count": len(users),
            "users": [{"id": str(u.id), "name": u.name, "email": u.email} for u in users]
        }
    
    def _validate(self, context: Dict[str, Any]) -> bool:
        return self.result.get("count", 0) >= self.min_expected

# TASK TESTS
class TaskCreateTest(BaseTest):
    """Test creating a task"""
    
    def __init__(self, expected_title: str, expected_status: int, expected_idm_key: Optional[str] = None):
        super().__init__(
            name="task_create",
            description="Create a new task and verify attributes"
        )
        self.expected_title = expected_title
        self.expected_status = expected_status
        self.expected_idm_key = expected_idm_key
    
    def _execute(self, db: Session, context: Dict[str, Any]):
        user_id = context.get("test_user_id")
        if not user_id:
            raise ValueError("No user_id in context")
        
        task = Task(
            title=self.expected_title,
            user_id=user_id,
            status=self.expected_status,
            idm_key=self.expected_idm_key
        )
        db.add(task)
        db.commit()
        db.refresh(task)
        
        context["test_task_id"] = task.id
        self.result = {
            "task_id": str(task.id),
            "title": task.title,
            "status": task.status
        }
    
    def _validate(self, context: Dict[str, Any]) -> bool:
        return (
            context.get("test_task_id") is not None and
            self.result.get("title") == self.expected_title and
            self.result.get("status") == self.expected_status
        )

class TaskReadTest(BaseTest):
    """Test reading a task by ID"""
    
    def __init__(self, expected_title: str):
        super().__init__(
            name="task_read",
            description="Read task by ID and verify data"
        )
        self.expected_title = expected_title
    
    def _execute(self, db: Session, context: Dict[str, Any]):
        task_id = context.get("test_task_id")
        if not task_id:
            raise ValueError("No task_id in context")
        
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            raise ValueError("Task not found")
        
        self.result = {
            "task_id": str(task.id),
            "title": task.title,
            "status": task.status
        }
    
    def _validate(self, context: Dict[str, Any]) -> bool:
        return self.result.get("title") == self.expected_title

class TaskUpdateTest(BaseTest):
    """Test updating a task"""
    
    def __init__(self, new_status: int):
        super().__init__(
            name="task_update",
            description="Update task status and verify change"
        )
        self.new_status = new_status
    
    def _execute(self, db: Session, context: Dict[str, Any]):
        task_id = context.get("test_task_id")
        if not task_id:
            raise ValueError("No task_id in context")
        
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            raise ValueError("Task not found")
        
        old_status = task.status
        task.status = self.new_status
        db.commit()
        db.refresh(task)
        
        self.result = {
            "old_status": old_status,
            "new_status": task.status
        }
    
    def _validate(self, context: Dict[str, Any]) -> bool:
        return self.result.get("new_status") == self.new_status

class TaskDeleteTest(BaseTest):
    """Test deleting a task"""
    
    def __init__(self):
        super().__init__(
            name="task_delete",
            description="Delete task and verify removal"
        )
    
    def _execute(self, db: Session, context: Dict[str, Any]):
        task_id = context.get("test_task_id")
        if not task_id:
            raise ValueError("No task_id in context")
        
        deleted_count = db.query(Task).filter(Task.id == task_id).delete()
        db.commit()
        
        # Verify deletion
        task = db.query(Task).filter(Task.id == task_id).first()
        
        self.result = {
            "deleted_count": deleted_count,
            "still_exists": task is not None
        }
    
    def _validate(self, context: Dict[str, Any]) -> bool:
        return (
            self.result.get("deleted_count") == 1 and
            self.result.get("still_exists") is False
        )

class TaskListTest(BaseTest):
    """Test listing all tasks"""
    
    def __init__(self, min_expected: int = 0):
        super().__init__(
            name="task_list",
            description="List all tasks and verify count"
        )
        self.min_expected = min_expected
    
    def _execute(self, db: Session, context: Dict[str, Any]):
        tasks = db.query(Task).all()
        self.result = {
            "count": len(tasks),
            "tasks": [{"id": str(t.id), "title": t.title, "status": t.status} for t in tasks]
        }
    
    def _validate(self, context: Dict[str, Any]) -> bool:
        return self.result.get("count", 0) >= self.min_expected

class TaskSummaryTest(BaseTest):
    """Test task summary by status"""
    
    def __init__(self, expected_summary: Optional[Dict[int, int]] = None):
        super().__init__(
            name="task_summary",
            description="Get task counts by status"
        )
        self.expected_summary = expected_summary or {}
    
    def _execute(self, db: Session, context: Dict[str, Any]):
        summary = {}
        for status in [0, 1, 2]:
            count = db.query(Task).filter(Task.status == status).count()
            summary[status] = count
        
        self.result = {"summary": summary}
    
    def _validate(self, context: Dict[str, Any]) -> bool:
        if not self.expected_summary:
            return True  # No expected values to check
        
        actual = self.result.get("summary", {})
        return all(
            actual.get(status) == count
            for status, count in self.expected_summary.items()
        )
