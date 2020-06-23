import os

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'DEV'
    DATABASE_URL = os.environ.get('DATABASE_URL')
    SMTP_HOST = 'smtp.sparkpostmail.com' # Placeholder
    SMTP_PORT = 587 # Placeholder
    SMTP_USERNAME = '' # Placeholder
    SMTP_LOGIN = 'SMTP_Injection'
    #SMTP_PASSWORD = ''
    SMTP_PASSWORD = '' # Placeholder
    SCHEMA_FOLDER = 'schemas'
    UPLOAD_FOLDER = 'uploads'
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}