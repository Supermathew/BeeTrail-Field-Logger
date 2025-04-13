from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.schemas.user import UserCreate, UserResponse,LoginRequest,TokenResponse,RefreshTokenRequest
from app.db.crud import create_user, get_user_by_email
from app.utils.security import verify_password, create_access_token,verify_refresh_token,create_refresh_token
from app.dependencies import get_db
from fastapi import Request
from datetime import timedelta
from app.config import ACCESS_TOKEN_EXPIRE_MINUTES,ALGORITHM,SECRET_KEY
from fastapi import Body
from fastapi import APIRouter, Body, Depends, HTTPException, status
from jose import jwt, JWTError

router = APIRouter(tags=["auth"])
templates = Jinja2Templates(directory="templates")

@router.post("/api/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user: UserCreate, db=Depends(get_db)):
    print("mathewwww")
    db_user = await get_user_by_email(db, user.email,user.role)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    db_user = await create_user(db, user)
    return db_user

@router.post("/api/login", response_model=dict)
async def login(login_data: LoginRequest, db=Depends(get_db)):
    user = await get_user_by_email(db, login_data.username,"admin")
    if not user or not verify_password(login_data.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Incorrect email or password")

    if user.get("role") != "admin":
        # logger.warning(f"Access denied for user with role: {user.get('role')}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are a beekeeper, you are not allowed to enter admin site"
        )
    access_token = create_access_token(data={"sub": user["email"], "role": user["role"]})
    refresh_token = create_refresh_token(data={"sub": user["email"], "role": user["role"]})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "role": user["role"]
    }


@router.get("/admin", response_class=HTMLResponse)
async def get_admin_page(request: Request):
    return templates.TemplateResponse("admin.html", {"request": request})

@router.get("/login", response_class=HTMLResponse)
async def get_login_page(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@router.post("/token", summary="Generate a token for the user")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(),db=Depends(get_db)):
    user = await get_user_by_email(db, form_data.username,"admin")
    if not user or not verify_password(form_data.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user["email"]})
    return {"access_token": access_token, "token_type": "bearer"}



@router.post("/api/token/refresh", response_model=dict)
async def refresh_token(refresh_token: str = Body(... ,embed=True), db=Depends(get_db)):
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        role = payload.get("role")

        if email is None or role is None:
            raise HTTPException(status_code=401, detail="Invalid refresh token")

        user = await db["users"].find_one({"email": email})
        if not user:
            raise HTTPException(status_code=401, detail="User not found")

        new_access_token = create_access_token(data={"sub": user["email"], "role": role})
        return {
            "access_token": new_access_token,
            "token_type": "bearer",
            "role": role
        }
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
