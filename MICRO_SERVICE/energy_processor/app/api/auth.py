from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

class LoginRequest(BaseModel):
    username: str
    password: str

@router.post("/login")
def login(request: LoginRequest):
    # Mock authentication for testing
    if request.username == "admin" and request.password == "0823":
        return {
            "status": "success",
            "message": "Login successful",
            "access_token": "mock_token_12345",
            "token_type": "bearer"
        }
    raise HTTPException(status_code=401, detail="Invalid credentials")
