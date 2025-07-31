from .utils import *
from ..routers.admin import get_db, get_current_user
from fastapi import status
from ..models import Todos

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user  

def test_admin_read_all_authenticated(test_todo):
    response = client.get("/admin/todos")
    assert response.status_code == status.HTTP_200_OK
    expected = [{
        'complete': False,
        'title': "Learn to code!",
        'description': "Complete the FastAPI tutorial",
        'priority': 1,
        'archive': False,
        'owner_id': 1,
        'id': 1,
        'date_created': test_todo.date_created.isoformat(),
        'date_modified': test_todo.date_modified.isoformat()
    }]
    assert response.json() == expected

def test_admin_delete_todo(test_todo):
    response = client.delete("/admin/todo/1")
    assert response.status_code == status.HTTP_204_NO_CONTENT
       
    db = TestingSessionLocal()
    model = db.query(Todos).filter(Todos.id == 1).first()
    assert model is None  # Ensure the todo is deleted

def test_admin_delete_todo_not_found(test_todo):
    response = client.delete("/admin/todo/999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Todo not found"}