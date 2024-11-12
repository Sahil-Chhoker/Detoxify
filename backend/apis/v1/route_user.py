from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime
from typing import Optional
from schema.user import UserRegister, UserResponse, UserProfile
from db.session import SUPABASE

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

async def get_current_user(token: str = Depends(oauth2_scheme)) -> Optional[dict]:
    try:
        user = SUPABASE.auth.get_user(token)
        return user.user
    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

@router.post("/register", response_model=UserResponse)
async def register(user_data: UserRegister):
    try:
        auth_response = await SUPABASE.auth.sign_up({
            "email": user_data.email,
            "password": user_data.password
        })
        
        user_insert = SUPABASE.table("users").insert({
            "id": auth_response.user.id,
            "name": user_data.name,
            "email": user_data.email,
            "created_at": datetime.utcnow().isoformat()
        }).execute()

        return UserResponse(
            access_token=auth_response.session.access_token,
            token_type="bearer",
            user={
                "id": auth_response.user.id,
                "name": user_data.name,
                "email": user_data.email,
                "created_at": datetime.utcnow().isoformat()
            },
            message="User registered successfully",
            created_at=datetime.utcnow().isoformat()
        )

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

@router.post("/login", response_model=UserResponse)
async def login(email: str, password: str):
    try:
        auth_response = SUPABASE.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        
        user_data = SUPABASE.table("users").select("*").eq("id", auth_response.user.id).single().execute()

        return UserResponse(
            access_token=auth_response.session.access_token,
            token_type="bearer",
            user=user_data.data,
            message="Login successful",
            created_at=datetime.utcnow().isoformat()
        )

    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )

@router.post("/logout")
async def logout(current_user: dict = Depends(get_current_user)):
    try:
        SUPABASE.auth.sign_out()
        return {"message": "Logged out successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

@router.get("/profile", response_model=UserProfile)
async def get_profile(current_user: dict = Depends(get_current_user)):
    try:
        user_data = SUPABASE.table("users").select("*").eq("id", current_user.id).single().execute()
        return UserProfile(**user_data.data)
    except Exception as e:
        raise HTTPException(
            status_code=404,
            detail="User profile not found"
        )