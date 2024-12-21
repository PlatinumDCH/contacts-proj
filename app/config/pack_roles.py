import enum

class Role(enum.Enum):
    ADMIN: str     = "admin"
    MODERATOR: str = "moderator"
    USER: str      = "user"