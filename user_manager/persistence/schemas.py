from pydantic import BaseModel


class UserBase(BaseModel):
    email: str
    password: str


class UserRegister(UserBase):
    name: str


class UserLogin(UserBase):
    pass


class UserLoginResponse(BaseModel):
    access_token: str
    user_id: int


class UserRefreshToken(BaseModel):
    access_token: str


class UserResetLink(BaseModel):
    email: str


class UserResetPassword(UserBase):
    repeat_password: str
    reset_password_code: str


class User(UserBase):
    user_id: int

    class Config:
        orm_mode = True
