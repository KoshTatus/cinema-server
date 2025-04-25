from fastapi import HTTPException
from fastapi import status

class AuthErrors:
    @staticmethod
    def email_occupied() -> HTTPException:
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email is occupied!")

    @staticmethod
    def cookie_not_found() -> HTTPException:
        return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Cookie not found")

    @staticmethod
    def invalid_token() -> HTTPException:
        return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    @staticmethod
    def token_not_found() -> HTTPException:
        return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token not found in cookies")

    @staticmethod
    def email_not_found() -> HTTPException:
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect email!")

    @staticmethod
    def password_not_found() -> HTTPException:
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect password!")