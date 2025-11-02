import os
class Config:
    SECRET_KEY = "pclinfo"
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024
    UPLOAD_FOLDER= os.path.join(r'uploads')
    DB_NAME = "ecom_bpdb"
    DB_USER = "ecom_bpdb_user"
    DB_PASSWORD = "Hz40FiLGSwYGYDL4JPbleUKXJB76hwEA"
    DB_HOST = "dpg-d42u7bur433s73e11lo0-a.oregon-postgres.render.com"
    DB_PORT = "5432"
    # Optional Stripe configuration (set programmatically here or via environment variables)
    STRIPE_SECRET_KEY = None
    STRIPE_WEBHOOK_SECRET = None
