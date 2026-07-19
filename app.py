import os
from dotenv import load_dotenv  # <-- Add this
load_dotenv()      
from flask import Flask
from flask_login import LoginManager
from extensions import db, bcrypt
import cloudinary
import cloudinary.uploader

app = Flask(__name__)
# Use environment variables for security in production
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', '5791628bb0b13ce0c676dfde280ba245')

# Vercel needs a cloud DB (like Neon or Supabase). This falls back to sqlite locally.
# 1. Fetch the Neon Database URL injected by Vercel
database_url = os.environ.get('DATABASE_URL')

# 2. Fix the prefix: Neon provides 'postgres://', but SQLAlchemy strictly requires 'postgresql://'
if database_url and database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

# 3. Apply the modified URL to your Flask app
app.config['SQLALCHEMY_DATABASE_URI'] = database_url

# IMPORTANT: Ensure any hardcoded SQLite fallback is COMPLETELY REMOVED.
# Make sure lines like these are deleted:
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
# app.instance_path = ...
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Configure Cloudinary safely 
cloudinary.config(
    cloud_name = os.environ.get("CLOUDINARY_CLOUD_NAME", "dwtbh8y3t"),
    api_key = os.environ.get("CLOUDINARY_API_KEY", "193639451971529"),
    api_secret = os.environ.get("CLOUDINARY_API_SECRET", "x5AyvDv5n07dUCj0d2gXKd0ynaE"),
    secure = True
)

# Removed the local UPLOAD_FOLDER os.makedirs() logic here because 
# Vercel is a read-only environment and we are uploading straight to Cloudinary.

db.init_app(app)
bcrypt.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

from models import User
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

from routes import *

with app.app_context():
    db.create_all()
    
    # AUTOMATIC ADMIN CREATOR
    admin_exists = User.query.filter_by(email='admin@portal.com').first()
    if not admin_exists:
        hashed_pw = bcrypt.generate_password_hash('admin123').decode('utf-8')
        admin_user = User(
            username='Admin',
            email='admin@portal.com',
            password=hashed_pw,
            is_admin=True 
        )
        db.session.add(admin_user)
        db.session.commit()
        print("System Notice: Fresh Admin account seeded successfully!")

# Required for Vercel Serverless execution
if __name__ == '__main__':
    app.run(debug=True)
