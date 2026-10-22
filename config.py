import os
import platform


class Config:
    SECRET_KEY = (
        os.environ.get("SECRET_KEY")
        or "you-will-never-guess:6d667eac81ee0897e67cecbaf10a801ee789f06a2e9849e46cd28728"
    )
    DEBUG = False
    HOST = "127.0.0.1"
    PORT = 80
    SCANNER_OUT_DIR = "output"
    OUTPUT_DIR_VAR_NAME = "SCANNER_OUT_DIR"

    CELERY_BROKER_URL = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND = "redis://localhost:6379/0"
    # email config
    SMTP_SERVER = "smtp.gmail.com"
    SMTP_PORT = 465
    MAX_ATTACHMENT_MB = 25
    DOWNLOAD_BASE_URL = "http://ec2-3-96-154-236.ca-central-1.compute.amazonaws.com/output"

    # TODO: add ENV variables
    sender_email = os.getenv("SCRAPER_EMAIL_SENDER","connect.bankinglabs@gmail.com")
    receiver_email = os.getenv("SCRAPER_EMAIL_RECEIVER","vedanthicloud@gmail.com")
    email_password = os.getenv("SCRAPER_EMAIL_PASSWORD","acve ynep wrui tuvd")
 
    
    #Redis
    REDIS_HOST = "localhost"
    REDIS_PORT = 6379
    REDIS_DB = 0
    CELERY_BROKER_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"
    CELERY_RESULT_BACKEND = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"
    REDIS_TIMEOUT_TASK_ID = 60 * 3000

    # frontend password
    USERNAME = os.getenv("APP_USERNAME", "scraper")
    PASSWORD = os.getenv("APP_PASSWORD", "banking_labs@123")

    if platform.system() == "Darwin" or platform.system() == "Windows":  # MacOS coz i work on
        ENV = "development"
    elif platform.system() == "Linux":
        ENV = "production"
    else:
        ENV = "testing"


class DevelopmentConfig(Config):
    DEBUG = True
    PORT = 8080
    LOGIN_REQUIRED = True
    USERNAME = "p"
    PASSWORD = "p"


class ProductionConfig(Config):
    DEBUG = False
    LOGIN_REQUIRED = True
    PORT = 8009
    USERNAME = "girish_pvl"
    PASSWORD = "HelloML"


class TestingConfig(Config):
    DEBUG = True
    LOGIN_REQUIRED = False
    PORT = 8080
    USERNAME = "p"
    PASSWORD = "p"


def get_config(env=None):
    env = env or os.getenv("FLASK_ENV", "production").lower()
    if env == "development":
        return DevelopmentConfig()
    elif env == "testing":
        return TestingConfig()
    else:
        return ProductionConfig()
