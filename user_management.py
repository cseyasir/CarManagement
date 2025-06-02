import json
import os
import re
from datetime import datetime

# File to store user data
USERS_FILE = "users.json"

# Admin credentials
ADMIN_USERNAME = "Admin"
ADMIN_PASSWORD = "Cseeng123#"  # You should change this in production

def load_users():
    """Load users from JSON file"""
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_users(users):
    """Save users to JSON file"""
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=4)

def validate_vehicle_number(vehicle_number):
    """Validate vehicle number format (e.g., JK03L2315, JK03LA2315)"""
    # Check if the string contains only alphanumeric characters
    if not vehicle_number.isalnum():
        return False
    
    # Check if the string length is between 8 and 12 characters
    if not (8 <= len(vehicle_number) <= 12):
        return False
    
    # Check if the first two characters are letters
    if not vehicle_number[:2].isalpha():
        return False
    
    # Check if there are at least 2 digits after the first two letters
    if not any(c.isdigit() for c in vehicle_number[2:4]):
        return False
    
    # Check if the last 4 characters are digits
    if not vehicle_number[-4:].isdigit():
        return False
    
    return True

def register_user(vehicle_number, vehicle_model, owner_name, password=None):
    """Register a new user"""
    users = load_users()
    
    # Check if vehicle number already exists
    if vehicle_number in users:
        return False, "Vehicle number already registered"
    
    # Validate vehicle number format
    if not validate_vehicle_number(vehicle_number):
        return False, "Invalid vehicle number format. Use format like JK03L2315 or JK03LA2315"
    
    # If no password provided, use last 4 digits of vehicle number
    if password is None:
        password = vehicle_number[-4:]
    
    # Create user record
    users[vehicle_number] = {
        "vehicle_model": vehicle_model,
        "owner_name": owner_name,
        "password": password,
        "registration_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "last_active": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    # Save to file
    save_users(users)
    return True, "Registration successful"

def authenticate_user(username, password):
    """Authenticate a user or admin"""
    # Check for admin login
    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        return True, {"is_admin": True, "username": "admin"}
    
    # Check for regular user login
    users = load_users()
    if username not in users:
        return False, "Vehicle number not registered"
    
    user = users[username]
    if user["password"] == password:
        # Update last active time
        user["last_active"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        save_users(users)
        return True, user
    return False, "Incorrect password"

def get_user_info(vehicle_number):
    """Get user information"""
    users = load_users()
    return users.get(vehicle_number)

def get_all_users():
    """Get all registered users"""
    return load_users()

def delete_user(vehicle_number):
    """Delete a user account"""
    users = load_users()
    if vehicle_number in users:
        del users[vehicle_number]
        save_users(users)
        return True, "User deleted successfully"
    return False, "User not found"

def update_last_active(vehicle_number):
    """Update user's last active timestamp"""
    users = load_users()
    if vehicle_number in users:
        users[vehicle_number]["last_active"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        save_users(users)
        return True
    return False 