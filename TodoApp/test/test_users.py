from .utils import *
from ..routers.users import get_db, get_current_user
from fastapi import status


app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user

def test_return_user(test_user):
    response = client.get("/users")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()[0]['username'] == "mary" 
    assert response.json()[0]['first_name'] == "Mary" 
    assert response.json()[0]['last_name'] == "Smith" 
    assert response.json()[0]['email'] == "mary@gmail.com" 
    assert response.json()[0]['gender'] == "female" 
    assert response.json()[0]['role'] == "user" 
    assert response.json()[0]['country'] == "Philippines"
    assert response.json()[0]['birthdate'] == "1995-05-20" 
    

def test_change_password(test_user):
    response = client.put("/users/change-password", json={
        "password": "mary123",
        "new_password": "mary456"
    })
    
    assert response.status_code == status.HTTP_204_NO_CONTENT
    
    # Verify the password was changed
    db = TestingSessionLocal()
    user = db.query(Users).filter(Users.id == test_user.id).first()
    assert bcrypt_context.verify("mary456", user.hashed_password)  # Check if new password is hashed correctly
    
def test_change_password_incorrect_old_password(test_user):
    response = client.put("/users/change-password", json={
        "password": "wrong_password",
        "new_password": "mary456"
    })
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Incorrect password"}
    
def test_change_phone_number(test_user):
    response = client.put("/users/phonenumber/09123456789")
    assert response.status_code == status.HTTP_204_NO_CONTENT