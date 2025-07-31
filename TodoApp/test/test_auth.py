from .utils import * 
from ..routers.auth import get_db, authenticate_user, SECRET_KEY, ALGORITHM, create_access_token, get_current_user
from jose import jwt
from datetime import timedelta
import pytest
from fastapi import HTTPException

app.dependency_overrides[get_db] = override_get_db

def test_authenticate_user(test_user):
    db = TestingSessionLocal()
    
    authenticated_user = authenticate_user(test_user.username, "mary123", db)
    assert authenticated_user is not None
    assert authenticated_user.username == test_user.username
    
    non_existent_user = authenticate_user("Hera", "wrong_password", db)
    assert non_existent_user is None
    
    wrong_password_user = authenticate_user(test_user.username, "wrong_password", db)
    assert wrong_password_user is None
    
def test_create_access_token(test_user):
    username = 'harold'
    password = 'haroldidol'
    role = 'user'
    user_id = 1
    expires_delta = timedelta(days=1)
    
    token = create_access_token(username, user_id, role, expires_delta)
    
    decoded_token = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM], options={"verify_signature": False})
    
    assert decoded_token['sub'] == username
    assert decoded_token['id'] == user_id
    assert decoded_token['role'] == role
    
@pytest.mark.asyncio    
async def test_get_current_user_valid_token():
    encode = {'sub': 'harvey', 'id': 2, 'role': 'user'}
    token = jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM) 
    
    user = await get_current_user(token=token)
    assert user == {'username': 'harvey',  'role': 'user', 'id': 2 }
    
@pytest.mark.asyncio
async def test_current_user_invalid_payload():
    encode = {'role': 'user'}
    token = jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)
    
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(token=token)
        
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Could not validate user"