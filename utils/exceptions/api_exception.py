from fastapi import HTTPException, status


class RateLimitException(Exception):
    def __str__(self):
        return "Rate limit errored out."


def credentials_exception():
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
