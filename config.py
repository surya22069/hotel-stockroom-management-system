class Config:
    SQLALCHEMY_DATABASE_URI = "postgresql://postgres:goli00@localhost/stockroom_db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = "stockroom_secret"