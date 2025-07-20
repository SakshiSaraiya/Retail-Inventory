import bcrypt
from db import fetch_data, execute_query

# Register a new user with hashed password
def register_user(username, email, password):
    # Check if username or email already exists
    existing = fetch_data(
        "SELECT * FROM Users WHERE username = %s OR email = %s",
        (username, email)
    )
    if existing:
        return False, "Username or email already exists."

    # Hash the password
    hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    # Insert new user
    success = execute_query(
        "INSERT INTO Users (username, email, password_hash) VALUES (%s, %s, %s)",
        (username, email, hashed_pw)
    )
    if success:
        return True, "User registered successfully."
    else:
        return False, "Registration failed."

# Verify login credentials
def login_user(username_or_email, password):
    user = fetch_data(
        "SELECT * FROM Users WHERE username = %s OR email = %s",
        (username_or_email, username_or_email)
    )
    if user:
        stored_hash = user[0]['password_hash'].encode('utf-8')
        if bcrypt.checkpw(password.encode('utf-8'), stored_hash):
            return True, user[0]['user_id']
    return False, None

# Get user_id by username or email
def get_user_id(username_or_email):
    user = fetch_data(
        "SELECT user_id FROM Users WHERE username = %s OR email = %s",
        (username_or_email, username_or_email)
    )
    if user:
        return user[0]['user_id']
    return None


def check_login():
    if "user_id" not in st.session_state or not st.session_state.user_id:
        st.warning("🚫 You must log in to access this page.")
        st.stop()

