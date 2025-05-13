import hashlib

def hash_password(password):
    """Hash a password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

# User credentials with hashed passwords
USERS = {
    "aaditya": {
        "password": hash_password("aaditya"),  # Simple password for demo
        "name": "Aaditya Patil",
        "user_id": "Aaditya Patil"  # Matches transaction data
    },
    "kavi": {
        "password": hash_password("kavi"),  # Simple password for demo
        "name": "Kavi Shah",
        "user_id": "Kavi Shah"  # Matches transaction data
    },
    "virnit": {
        "password": hash_password("virnit"),  # Simple password for demo
        "name": "Virnit Gavali",
        "user_id": "Virnit Gavali"  # Special case for Virnit
    },
    "padam": {
        "password": hash_password("padam"),  # Simple password for demo
        "name": "Padam Khandelwal",
        "user_id": "Padam Khandelwal"  # Matches transaction data
    },
    "tappu": {
        "password": hash_password("tappu"),  # Simple password for demo
        "name": "Tapoprasad Tripathy",
        "user_id": "Tapoprasad Tripathy"  # Matches transaction data
    }
}

def verify_credentials(username, password):
    """Verify username and password"""
    if username in USERS and USERS[username]["password"] == hash_password(password):
        return True
    return False 