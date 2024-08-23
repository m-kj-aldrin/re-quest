from flask import (
    Flask,
    flash,
    request,
    redirect,
    url_for,
    session,
    jsonify,
    render_template,
)
import os
import secrets
from datetime import datetime, timedelta
import bcrypt

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired

# from server.document_printer import DocumentPrinter
from document_printer import DocumentPrinter

app = Flask(__name__)

# Secret key for signing session cookies
app.secret_key = secrets.token_hex(16)

# Base directory for storing user data and sessions
BASEDATA_DIR = "./data"
USER_DATA_DIR = os.path.join(BASEDATA_DIR, "users")
SESSION_DIR = os.path.join(BASEDATA_DIR, "sessions")

# Create folders if they don't exist
os.makedirs(USER_DATA_DIR, exist_ok=True)
os.makedirs(SESSION_DIR, exist_ok=True)


# Utility function to create a secure session ID
def create_session_id():
    return secrets.token_urlsafe(16)  # Generates a cryptographically secure session ID


# Utility function to validate session
def validate_session(session_id):
    session_file = os.path.join(SESSION_DIR, f"{session_id}.txt")
    if not os.path.exists(session_file):
        return None  # Session not found

    with open(session_file, "r") as f:
        user_id = f.readline().strip().split(": ")[1]
        expires_at_str = f.readline().strip().split(": ")[1]
        expires_at = datetime.fromisoformat(expires_at_str)

    if datetime.now() > expires_at:
        os.remove(session_file)  # Session expired, delete session file
        return None

    return user_id  # Session is valid


# Utility function to hash passwords
def hash_password(password):
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed_password


# Utility function to verify password
def verify_password(stored_password_hash, provided_password):
    return bcrypt.checkpw(provided_password.encode("utf-8"), stored_password_hash)


# Home route
@app.route("/")
def home():
    if "session_id" in session:
        session_id = session["session_id"]
        user_id = validate_session(session_id)
        if user_id:
            return f"Welcome {user_id}! You have access to your data."
    return render_template("index.jinja")


# Path to your templates folder where Word templates are stored
TEMPLATES_FOLDER = os.path.join(os.getcwd(), "server", "document_templates")

# Initialize the DocumentPrinter
printer = DocumentPrinter(TEMPLATES_FOLDER)


@app.route("/print-document/", methods=["GET"])
def choose_document():
    return render_template("choose_document.jinja")


class MedlemsInfoForm(FlaskForm):
    label = "Medlems uppgifter"
    person_nr = StringField("Personnummer")
    mmid = StringField("mmid")
    namn_medlem = StringField("namn")
    forening = StringField("Förening")
    # submit = SubmitField("skriv ut")


class PostMottagarForm(FlaskForm):
    label = "Post mottagare"
    namn_mottagare = StringField("Mottagare namn")
    c_o = StringField("c/o")
    gata = StringField("Gatuadress")
    post_nr = StringField("Postnummer")
    post_ort = StringField("Postort")


class UtbetalningForm(FlaskForm):
    label = "Utbetalnings motagare"
    behallning = StringField("Behållning")


# document_mapping = {
#     "avslut": {"forms": {"base": MedlemsInfoForm, "utbetalning": UtbetalningForm}},
#     "uttag": {"forms": {"base": MedlemsInfoForm, "utbetalning": UtbetalningForm}},
# }
document_mapping = {
    "avslut": {"forms": [PostMottagarForm, MedlemsInfoForm, UtbetalningForm]},
    "uttag": {"forms": [PostMottagarForm, MedlemsInfoForm, UtbetalningForm]},
}


@app.route("/print-document/<template_name>", methods=["GET", "POST"])
def print_document(template_name):

    if template_name not in document_mapping:
        return "Document type not found", 404

    # Dynamically get the form class and template file based on doc_type
    # forms = document_mapping[template_name]["forms"]
    # forms = {
    #     name: form_class()
    #     for name, form_class in document_mapping[template_name]["forms"].items()
    # }
    forms = [form_class() for form_class in document_mapping[template_name]["forms"]]

    print(forms)
    # template_file = document_mapping[template_name]["template"]
    # output_filename = document_mapping[template_name]["filename"]

    # form = form_class()

    # is_valid = all([form.validate_on_submit() for form in forms.values()])
    is_valid = all([form.validate_on_submit() for form in forms])

    if is_valid:
        # Collect form data dynamically based on form fields
        # data = {field.name: field.data for field in forms}
        # data = {field.name: field.data for form in forms.values() for field in form}
        data = {field.name: field.data for form in forms for field in form}

        # Load the correct template and populate it with form data
        # doc = DocxTemplate(template_file)
        # doc.render(form_data)

        # Save and send the document to the user
        # output_path = f"generated_documents/{output_filename}"
        # doc.save(output_path)

        # return send_file(output_path, as_attachment=True)

        # if request.method == "POST":
        # data = request.form.to_dict()

        if not template_name:
            flash("Template name is required", "error")
            return redirect(url_for("choose_document"))

        try:
            printer.process_template(template_name + ".docx", data=data)
            flash(f"Document {template_name} printed successfully", "success")
        except FileNotFoundError as e:
            flash(str(e), "error")
        except Exception as e:
            flash(f"An error occurred: {str(e)}", "error")

        return redirect(url_for("choose_document"))

    # Render the GET form for printing documents
    return render_template(
        "print_document.jinja", template_name=template_name, forms=forms
    )


# Registration route
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user_dir = os.path.join(USER_DATA_DIR, username)

        # Check if user already exists
        if os.path.exists(user_dir):
            error_message = "Username already exists. Please choose another one."
            return render_template("register.jinja", error=error_message)

        # Create user directory
        os.makedirs(user_dir)

        # Hash password and store it in profile.txt
        hashed_password = hash_password(password)
        profile_file = os.path.join(user_dir, "profile.txt")

        with open(profile_file, "wb") as f:  # Save the hashed password as bytes
            f.write(b"password: ")
            f.write(hashed_password)

        return redirect(
            url_for("login")
        )  # Redirect to login after successful registration

    return render_template("register.jinja")


# Login route - Handles both GET and POST
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # Handle login on POST request
        username = request.form["username"]
        password = request.form["password"]

        user_profile_file = os.path.join(USER_DATA_DIR, username, "profile.txt")

        if os.path.exists(user_profile_file):
            with open(
                user_profile_file, "rb"
            ) as f:  # Read the hashed password as bytes
                stored_password_hash = f.readline().strip().split(b": ")[1]

            if verify_password(stored_password_hash, password):
                # Create a session
                session_id = create_session_id()
                session_file = os.path.join(SESSION_DIR, f"{session_id}.txt")
                expires_at = datetime.now() + timedelta(
                    hours=1
                )  # 1-hour session expiry

                # Save session info in flat file
                with open(session_file, "w") as f:
                    f.write(f"user_id: {username}\n")
                    f.write(f"expires_at: {expires_at.isoformat()}\n")

                # Set the session ID in the user's cookie
                session["session_id"] = session_id

                return redirect(url_for("home"))

        return "Invalid credentials", 401

    # Handle GET request to show the login form
    return render_template("login.jinja")


# Route to access and update the profile
@app.route("/profile", methods=["GET", "POST"])
def profile():
    if "session_id" not in session:
        return redirect(url_for("login"))  # Redirect to login if user is not logged in

    session_id = session["session_id"]
    user_id = validate_session(session_id)

    if not user_id:
        return redirect(url_for("login"))  # Redirect if session is invalid

    user_data_file = os.path.join(USER_DATA_DIR, user_id, "data.txt")

    if request.method == "POST":
        # Save the submitted profile data (from textarea)
        profile_data = request.form["profile_data"]

        with open(user_data_file, "w") as f:
            f.write(profile_data)

        return redirect(url_for("profile"))  # Redirect to the same page after saving

    # Read the existing data from the user's profile (if it exists)
    existing_data = ""
    if os.path.exists(user_data_file):
        with open(user_data_file, "r") as f:
            existing_data = f.read()

    return render_template("profile.jinja", user_id=user_id, profile_data=existing_data)


# Route to access user data
@app.route("/data")
def access_user_data():
    if "session_id" in session:
        session_id = session["session_id"]
        user_id = validate_session(session_id)

        if user_id:
            # Fetch user data from their directory
            user_data_file = os.path.join(USER_DATA_DIR, user_id, "data.txt")

            if os.path.exists(user_data_file):
                with open(user_data_file, "r") as f:
                    data = f.read()
                return jsonify({"user_id": user_id, "data": data})

            return "No data found for this user.", 404

    return "Unauthorized, please log in.", 401


# Logout route
@app.route("/logout")
def logout():
    if "session_id" in session:
        session_id = session.pop(
            "session_id", None
        )  # Remove the session ID from the session cookie

        # Delete the corresponding session file
        session_file = os.path.join(SESSION_DIR, f"{session_id}.txt")
        if os.path.exists(session_file):
            os.remove(session_file)

    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050, debug=True)
