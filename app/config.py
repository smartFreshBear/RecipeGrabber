from dotenv import load_dotenv
import os

load_dotenv()

URL_TIMEOUT = 10
EXECUTOR_TYPE = 'thread'
EXECUTOR_MAX_WORKERS = 2
SQLALCHEMY_DATABASE_URI = os.getenv('DB_URI') or 'sqlite:///RecipeGrabber.db'
SQLALCHEMY_TRACK_MODIFICATIONS = False