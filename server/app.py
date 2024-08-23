# from flask import Flask, request, render_template
# from random import randint
# from uuid import uuid4
# from dataclasses import dataclass

# app = Flask(__name__)


# @dataclass
# class User:
#     id = str(uuid4())
#     name: str


# table_columns = ["id", "name"]
# users = [User("Benny")]


# @app.get("/")
# def index():
#     return render_template(
#         "index.jinja", table_columns=table_columns, users=users, n=randint(0, 1024)
#     )


# @app.post("/")
# def newUser():
#     form_data = request.form
#     name = form_data.get("name")

#     users.append(User(name))

#     return render_template(
#         "partials/users-rows.jinja",
#         table_columns=table_columns,
#         users=users,
#     ) + render_template("partials/n.jinja", n=randint(0, 1024))


# def dUser(users, id):
#     return [user for user in users if user.id != id]


# @app.delete("/<id>")
# def deleteUser(id):
#     if users:
#         user_to_remove = next((user for user in users if user.id == id), None)
#         if user_to_remove:
#             users.remove(user_to_remove)

#     return render_template(
#         "partials/users-rows.jinja",
#         table_columns=table_columns,
#         users=users,
#     )


# if __name__ == "__main__":
#     app.run(debug=True)

# from flask import Flask, request, redirect, url_for, session, jsonify, render_template
# import os
# import secrets
# from datetime import datetime, timedelta
# import bcrypt

# app = Flask(__name__)

# # Secret key for signing session cookies
# app.secret_key = secrets.token_hex(16)

# # Paths to flat file directories
# BASEDATA_DIR = "./data"
# USER_DATA_DIR = f'{BASEDATA_DIR}/users/'
# SESSION_DIR = f'{BASEDATA_DIR}/sessions/'

# # Create folders if they don't exist
# os.makedirs(USER_DATA_DIR, exist_ok=True)
# os.makedirs(SESSION_DIR, exist_ok=True)

# # Utility function to create a secure session ID


# def create_session_id():
#     # Generates a cryptographically secure session ID
#     return secrets.token_urlsafe(16)

# # Utility function to validate session


# def validate_session(session_id):
#     session_file = os.path.join(SESSION_DIR, f'{session_id}.txt')
#     if not os.path.exists(session_file):
#         return None  # Session not found

#     with open(session_file, 'r') as f:
#         user_id = f.readline().strip().split(': ')[1]
#         expires_at_str = f.readline().strip().split(': ')[1]
#         expires_at = datetime.fromisoformat(expires_at_str)

#     if datetime.now() > expires_at:
#         os.remove(session_file)  # Session expired, delete session file
#         return None

#     return user_id  # Session is valid

# # Utility function to hash passwords


# def hash_password(password):
#     salt = bcrypt.gensalt()
#     hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
#     return hashed_password

# # Utility function to verify password


# def verify_password(stored_password_hash, provided_password):
#     return bcrypt.checkpw(provided_password.encode('utf-8'), stored_password_hash)

# # Home route


# @app.route('/')
# def home():
#     if 'session_id' in session:
#         session_id = session['session_id']
#         user_id = validate_session(session_id)
#         if user_id:
#             return f'Welcome {user_id}! You have access to your data.'
#     return render_template('login.jinja')

# # Registration route


# @app.route('/register', methods=['GET', 'POST'])
# def register():
#     if request.method == 'POST':
#         username = request.form['username']
#         password = request.form['password']

#         user_dir = os.path.join(USER_DATA_DIR, username)

#         # Check if user already exists
#         if os.path.exists(user_dir):
#             error_message = 'Username already exists. Please choose another one.'
#             return render_template('register.jinja', error=error_message)

#         # Create user directory
#         os.makedirs(user_dir)

#         # Hash password and store it in profile.txt
#         hashed_password = hash_password(password)
#         profile_file = os.path.join(user_dir, 'profile.txt')

#         with open(profile_file, 'wb') as f:  # Save the hashed password as bytes
#             f.write(b'password: ')
#             f.write(hashed_password)

#         # Redirect to login after successful registration
#         return redirect(url_for('login'))

#     return render_template('register.jinja')

# # Login route


# @app.route('/login', methods=['POST'])
# def login():
#     username = request.form['username']
#     password = request.form['password']

#     user_profile_file = os.path.join(USER_DATA_DIR, username, 'profile.txt')

#     if os.path.exists(user_profile_file):
#         with open(user_profile_file, 'rb') as f:  # Read the hashed password as bytes
#             stored_password_hash = f.readline().strip().split(b': ')[1]

#         if verify_password(stored_password_hash, password):
#             # Create a session
#             session_id = create_session_id()
#             session_file = os.path.join(SESSION_DIR, f'{session_id}.txt')
#             expires_at = datetime.now() + timedelta(hours=1)  # 1-hour session expiry

#             # Save session info in flat file
#             with open(session_file, 'w') as f:
#                 f.write(f'user_id: {username}\n')
#                 f.write(f'expires_at: {expires_at.isoformat()}\n')

#             # Set the session ID in the user's cookie
#             session['session_id'] = session_id

#             return redirect(url_for('home'))

#     return 'Invalid credentials', 401

# # Route to access user data


# @app.route('/data')
# def access_user_data():
#     if 'session_id' in session:
#         session_id = session['session_id']
#         user_id = validate_session(session_id)

#         if user_id:
#             # Fetch user data from their directory
#             user_data_file = os.path.join(USER_DATA_DIR, user_id, 'data.txt')

#             if os.path.exists(user_data_file):
#                 with open(user_data_file, 'r') as f:
#                     data = f.read()
#                 return jsonify({'user_id': user_id, 'data': data})

#             return 'No data found for this user.', 404

#     return 'Unauthorized, please log in.', 401

# # Logout route


# @app.route('/logout')
# def logout():
#     # Remove the session ID from the session cookie
#     session.pop('session_id', None)
#     return redirect(url_for('home'))


# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=5000, debug=True)


from flask import Flask, request, redirect, url_for, session, jsonify, render_template
import os
import secrets
from datetime import datetime, timedelta
import bcrypt

app = Flask(__name__)

# Secret key for signing session cookies
app.secret_key = secrets.token_hex(16)

# Paths to flat file directories
BASEDATA_DIR = './data'
USER_DATA_DIR = f'{BASEDATA_DIR}/users/'
SESSION_DIR = f'{BASEDATA_DIR}/sessions/'

# Create folders if they don't exist
os.makedirs(USER_DATA_DIR, exist_ok=True)
os.makedirs(SESSION_DIR, exist_ok=True)

# Utility function to create a secure session ID


def create_session_id():
    # Generates a cryptographically secure session ID
    return secrets.token_urlsafe(16)

# Utility function to validate session


def validate_session(session_id):
    session_file = os.path.join(SESSION_DIR, f'{session_id}.txt')
    if not os.path.exists(session_file):
        return None  # Session not found

    with open(session_file, 'r') as f:
        user_id = f.readline().strip().split(': ')[1]
        expires_at_str = f.readline().strip().split(': ')[1]
        expires_at = datetime.fromisoformat(expires_at_str)

    if datetime.now() > expires_at:
        os.remove(session_file)  # Session expired, delete session file
        return None

    return user_id  # Session is valid

# Utility function to hash passwords


def hash_password(password):
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password

# Utility function to verify password


def verify_password(stored_password_hash, provided_password):
    return bcrypt.checkpw(provided_password.encode('utf-8'), stored_password_hash)

# Home route


@app.route('/')
def home():
    if 'session_id' in session:
        session_id = session['session_id']
        user_id = validate_session(session_id)
        if user_id:
            return f'Welcome {user_id}! You have access to your data.'
    return render_template('login.jinja')

# Registration route


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user_dir = os.path.join(USER_DATA_DIR, username)

        # Check if user already exists
        if os.path.exists(user_dir):
            error_message = 'Username already exists. Please choose another one.'
            return render_template('register.jinja', error=error_message)

        # Create user directory
        os.makedirs(user_dir)

        # Hash password and store it in profile.txt
        hashed_password = hash_password(password)
        profile_file = os.path.join(user_dir, 'profile.txt')

        with open(profile_file, 'wb') as f:  # Save the hashed password as bytes
            f.write(b'password: ')
            f.write(hashed_password)

        # Redirect to login after successful registration
        return redirect(url_for('login'))

    return render_template('register.jinja')

# Login route - Handles both GET and POST


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Handle login on POST request
        username = request.form['username']
        password = request.form['password']

        user_profile_file = os.path.join(
            USER_DATA_DIR, username, 'profile.txt')

        if os.path.exists(user_profile_file):
            with open(user_profile_file, 'rb') as f:  # Read the hashed password as bytes
                stored_password_hash = f.readline().strip().split(b': ')[1]

            if verify_password(stored_password_hash, password):
                # Create a session
                session_id = create_session_id()
                session_file = os.path.join(SESSION_DIR, f'{session_id}.txt')
                expires_at = datetime.now() + timedelta(hours=1)  # 1-hour session expiry

                # Save session info in flat file
                with open(session_file, 'w') as f:
                    f.write(f'user_id: {username}\n')
                    f.write(f'expires_at: {expires_at.isoformat()}\n')

                # Set the session ID in the user's cookie
                session['session_id'] = session_id

                return redirect(url_for('home'))

        return 'Invalid credentials', 401

    # Handle GET request to show the login form
    return render_template('login.jinja')

# Route to access user data


@app.route('/data')
def access_user_data():
    if 'session_id' in session:
        session_id = session['session_id']
        user_id = validate_session(session_id)

        if user_id:
            # Fetch user data from their directory
            user_data_file = os.path.join(USER_DATA_DIR, user_id, 'data.txt')

            if os.path.exists(user_data_file):
                with open(user_data_file, 'r') as f:
                    data = f.read()
                return jsonify({'user_id': user_id, 'data': data})

            return 'No data found for this user.', 404

    return 'Unauthorized, please log in.', 401

# Updated Logout route to delete session file


@app.route('/logout')
def logout():
    if 'session_id' in session:
        # Remove the session ID from the session cookie
        session_id = session.pop('session_id', None)

        # Delete the corresponding session file
        session_file = os.path.join(SESSION_DIR, f'{session_id}.txt')
        if os.path.exists(session_file):
            os.remove(session_file)

    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
