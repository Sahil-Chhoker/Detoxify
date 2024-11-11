from fastapi import APIRouter, HTTPException
from fastapi import Depends
from fastapi import status
import supabase

router = APIRouter()


@router.post("/user/register", status_code=status.HTTP_201_CREATED)
def create_user():
    response = supabase.auth.sign_up(
        {"email": "email@example.com", "password": "password"}
    )
    return response.get("access_token")


@router.get("/user/profile", response_model=ShowUser)
def get_user_profile(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return current_user


@router.delete("/user/{user_id}")
def delete_current_user(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )
    if user_id != current_user.id:
        raise HTTPException(
            detail="Only the owner can delete the user.",
            status_code=status.HTTP_403_FORBIDDEN
        )
    message = delete_user(user_id=user_id, db=db)
    if message.get("error"):
        raise HTTPException(
            detail=message.get("error"), status_code=status.HTTP_400_BAD_REQUEST
        )
    return {"message": f"User deleted successfully with id {user_id}"}

