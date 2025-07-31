
from ..routers.todos import get_db, get_current_user
from fastapi import status
from ..models import Users, Todos
from .utils import *

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user


def test_read_all_authenticated(test_todo):
    response = client.get("/todos")
    assert response.status_code == status.HTTP_200_OK
    # Construct expected response dynamically based on test_todo
    expected = [{
        'complete': test_todo.complete,
        'title': test_todo.title,
        'description': test_todo.description,
        'priority': test_todo.priority,
        'archive': test_todo.archive,
        'owner_id': test_todo.owner_id,
        'id': test_todo.id,
        'date_created': test_todo.date_created.isoformat(),  # Convert to ISO 8601
        'date_modified': test_todo.date_modified.isoformat()  # Convert to ISO 8601
    }]
    assert response.json() == expected
    
def test_read_one_authenticated(test_todo):
    response = client.get("/todos/todo/1")
    assert response.status_code == status.HTTP_200_OK
    # Construct expected response dynamically based on test_todo
    # expected = []
    assert response.json() == {
        'complete': test_todo.complete,
        'title': test_todo.title,
        'description': test_todo.description,
        'priority': test_todo.priority,
        'archive': test_todo.archive,
        'owner_id': test_todo.owner_id,
        'id': test_todo.id,
        'date_created': test_todo.date_created.isoformat(),  # Convert to ISO 8601
        'date_modified': test_todo.date_modified.isoformat()  # Convert to ISO 8601
    }
    
def test_read_one_not_found():
    response = client.get("/todos/todo/999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Todo not found"}
    
    
def test_create_todo(test_todo):
    request_data = {
        "title": "New Todo",
        "description": "This is a new todo item",
        "priority": 2,
        "complete": False,
        "archive": False
    }
    
    response = client.post("/todos/todo", json=request_data)
    assert response.status_code == status.HTTP_201_CREATED
    
    db = TestingSessionLocal()
    model = db.query(Todos).filter(Todos.id == 2).first()
    assert model.title == request_data["title"] 
    assert model.description == request_data["description"] 
    assert model.priority == request_data["priority"] 
    assert model.complete == request_data["complete"] 
    assert model.archive == request_data["archive"] 
    
 
def update_todo(test_todo):
    request_data = {
        "title": "Updated Todo",
        "description": "This todo item has been updated",
        "priority": 3,
        "complete": True,
        "archive": True
    }
    
    response = client.put("/todos/todo/1", json=request_data)
    assert response.status_code == status.HTTP_204_NO_CONTENT
    
    db = TestingSessionLocal()
    model = db.query(Todos).filter(Todos.id == 1).first()
    assert model.title == request_data["title"] 
    assert model.description == request_data["description"] 
    assert model.priority == request_data["priority"] 
    assert model.complete == request_data["complete"] 
    assert model.archive == request_data["archive"]
    
def test_update_todo_not_found(test_todo):
    request_data = {
        "title": "Updated Todo",
        "description": "This todo item has been updated",
        "priority": 3,
        "complete": True,
        "archive": True
    }
    
    response = client.put("/todos/todo/20", json=request_data)
    assert response.status_code == 404
    assert response.json() == {"detail": "Todo not found"}
    
    
def test_delete_todo(test_todo):
    response = client.delete("/todos/todo/1")
    assert response.status_code == status.HTTP_204_NO_CONTENT
    
    db = TestingSessionLocal()
    model = db.query(Todos).filter(Todos.id == 1).first()
    assert model is None  # Ensure the todo was deleted
    

def test_delete_todo_not_found(test_todo):
    response = client.delete("/todos/todo/999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Todo not found"}
    
    
