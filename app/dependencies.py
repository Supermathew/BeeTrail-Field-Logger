from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from app.db.database import get_database
from app.utils.security import verify_token
import logging
from jose import JWTError

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_db(request: Request):
    return request.app.state.db

async def get_current_user(token: str = Depends(oauth2_scheme), db=Depends(get_db)):
    try:
        logger.info(f"Verifying token: {token}")
        user = await verify_token(token, db)

        if not user:
            logger.warning("User not found for token.")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )

        if user.get("role") != "admin":
            logger.warning(f"Access denied for user with role: {user.get('role')}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are a beekeeper, you are not allowed"
            )

        logger.info(f"User retrieved: {user}")
        return user

    except HTTPException as http_ex:
        raise http_ex

    except Exception as e:
        logger.error(f"Unexpected error: {repr(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error"
        )
