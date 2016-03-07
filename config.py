import os


class Config:
    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
    SQLALCHEMY_TRACK_MODIFICATIONS = True

if __name__ == '__main__':
    print(Config.SQLALCHEMY_DATABASE_URI)
