import os
class Config:
    SECRET_KEY = "pclinfo"
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024
    UPLOAD_FOLDER= os.path.join(r'uploads')
    DB_NAME = "postgres"
    DB_USER = "postgres"
    DB_PASSWORD = "CDfW6x7AI2yIm7tb"
    DB_HOST = "db.nbchszbhkckcoyxguqvg.supabase.co"
    DB_PORT = "5432"
    # Optional Stripe configuration (set programmatically here or via environment variables)
    STRIPE_SECRET_KEY = None
    STRIPE_WEBHOOK_SECRET = None
