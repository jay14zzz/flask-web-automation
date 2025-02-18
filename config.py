# config.py



class Config:
    # Common config settings...
    SECRET_KEY = 'supersecretkey'
    RESTRICT_SIGNUP = False
    

class DevelopmentConfig(Config):
    DEBUG = True
    PERMANENT_SESSION_LIFETIME = 365 * 24 * 60 * 60  # Sessions never expire in development

class ProductionConfig(Config):
    DEBUG = False
    PERMANENT_SESSION_LIFETIME = 3600  # 1 hour timeout for production