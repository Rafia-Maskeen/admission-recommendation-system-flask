# from flask import Flask, render_template, redirect, url_for, request, flash, jsonify
# from flask_bootstrap import Bootstrap
# from flask_wtf import FlaskForm
# from wtforms import StringField, PasswordField, BooleanField, FloatField
# from wtforms.validators import InputRequired, Length, Email
# from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
# import os
# import json
# import pickle
# import pandas as pd

# app = Flask(__name__)
# app.config['SECRET_KEY'] = os.urandom(24)
# Bootstrap(app)
# login_manager = LoginManager()
# login_manager.init_app(app)
# login_manager.login_view = 'login'

# # File path for the JSON database
# db_file = 'users.json'
# model_file_path = 'Knn_model.pkl'  # Updated path

# # Load the model
# model_loaded = False
# model_error = ""

# try:
#     if os.path.exists(model_file_path):
#         with open(model_file_path, 'rb') as model_file:
#             model = pickle.load(model_file)
#         model_loaded = True
#         print("Model loaded successfully.")
#     else:
#         model_error = f"Model file {model_file_path} not found."
# except Exception as e:
#     model_error = str(e)

# # Load users from JSON file
# def load_users():
#     if not os.path.exists(db_file):
#         return {}  # Return an empty dictionary if the file does not exist
#     with open(db_file, 'r') as file:
#         try:
#             return json.load(file)
#         except json.JSONDecodeError:
#             return {}  # Return an empty dictionary if JSON is invalid

# # Save users to JSON file
# def save_users(users):
#     with open(db_file, 'w') as file:
#         json.dump(users, file, indent=4)

# # User class to mimic UserMixin and database behavior
# class User(UserMixin):
#     def __init__(self, id, username, email, password):
#         self.id = id
#         self.username = username
#         self.email = email
#         self.password = password

#     def get_id(self):
#         return str(self.id)

# @login_manager.user_loader
# def load_user(user_id):
#     users = load_users()
#     user_data = users.get(user_id)  # Fetch user by id
#     if user_data and isinstance(user_data, dict):
#         return User(user_data['id'], user_data['username'], user_data['email'], user_data['password'])
#     return None

# class LoginForm(FlaskForm):
#     username = StringField('Username', validators=[InputRequired(), Length(min=4, max=20)])
#     password = PasswordField('Password', validators=[InputRequired(), Length(min=5, max=80)])
#     remember = BooleanField('Remember me')

# class RegisterForm(FlaskForm):
#     email = StringField('Email', validators=[InputRequired(), Email(), Length(min=6, max=30)])
#     username = StringField('Username', validators=[InputRequired(), Length(min=4, max=20)])
#     password = PasswordField('Password', validators=[InputRequired(), Length(min=5, max=80)])

# class PredictionForm(FlaskForm):
#     admission_marks = FloatField('Admission Marks', validators=[InputRequired()])
#     minimum_entry_mark = FloatField('Minimum Entry Mark', validators=[InputRequired()])
#     fees_structure = FloatField('Fees Structure', validators=[InputRequired()])
#     departments_offered = StringField('Departments Offered', validators=[InputRequired()])

# @app.route('/')
# def index():
#     return render_template('index.html')

# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     form = LoginForm()
#     if form.validate_on_submit():
#         users = load_users()
#         user_data = next((user for user in users.values() if isinstance(user, dict) and user['username'] == form.username.data), None)
#         if user_data and user_data['password'] == form.password.data:
#             user = User(user_data['id'], user_data['username'], user_data['email'], user_data['password'])
#             login_user(user, remember=form.remember.data)
#             return redirect(url_for('dashboard'))
#         flash('Invalid username or password', 'danger')
#     return render_template('login.html', form=form)

# @app.route('/signup', methods=['GET', 'POST'])
# def signup():
#     form = RegisterForm()
#     if form.validate_on_submit():
#         users = load_users()
#         # Check for existing email
#         if any(isinstance(user, dict) and user['email'] == form.email.data for user in users.values()):
#             flash('Email address already exists', 'danger')
#             return render_template('signup.html', form=form)
#         # Check for existing username
#         if any(isinstance(user, dict) and user['username'] == form.username.data for user in users.values()):
#             flash('Username already exists', 'danger')
#             return render_template('signup.html', form=form)
#         new_id = str(max(map(int, users.keys()), default=0) + 1)
#         new_user = {
#             'id': int(new_id),
#             'username': form.username.data,
#             'email': form.email.data,
#             'password': form.password.data  # Store plain password
#         }
#         users[new_id] = new_user  # Ensure the key is a string
#         save_users(users)
#         flash('Signup successful! Please log in to access the dashboard.', 'success')
#         return redirect(url_for('login'))
#     return render_template('signup.html', form=form)

# @app.route('/dashboard', methods=['GET', 'POST'])
# @login_required
# def dashboard():
#     form = PredictionForm()
#     if form.validate_on_submit():
#         if not model_loaded:
#             flash('Model is not loaded', 'danger')
#         else:
#             try:
#                 # Extract data from form
#                 data = {
#                     "Admission_marks": form.admission_marks.data,
#                     "Minimum_entry_mark": form.minimum_entry_mark.data,
#                     "Fees_structure": form.fees_structure.data,
#                     "Departments_Offered": form.departments_offered.data
#                 }

#                 # Convert data to DataFrame
#                 df = pd.DataFrame([data])

#                 # Check if the DataFrame columns match the model's expected features
#                 expected_columns = ['Admission_marks', 'Minimum_entry_mark', 'Fees_structure', 'Departments_Offered']
#                 if not all(col in df.columns for col in expected_columns):
#                     flash('Data format mismatch', 'danger')
#                     return render_template('dashboard.html', name=current_user.username, form=form)

#                 # Make prediction
#                 prediction = model.predict(df)

#                 # Display prediction result
#                 flash(f'Prediction: {prediction[0]}', 'success')

#             except Exception as e:
#                 flash(f'Error: {str(e)}', 'danger')

#     return render_template('dashboard.html', name=current_user.username, form=form)

# @app.route('/check_model', methods=['GET'])
# def check_model():
#     if model_loaded:
#         return jsonify({'status': 'Model loaded successfully'})
#     else:
#         return jsonify({'error': f'Model failed to load: {model_error}'}), 500

# universities = {
#     'Quaid-i-Azam University': 0,
#     'COMSATS University Islamabad': 1,
#     'National University of Sciences and Technology': 2,
#     'University of the Punjab': 3,
#     'University of Engineering and Technology, Lahore': 4,
#     'University of Peshawar': 5,
#     'Government College University Faisalabad': 6,
#     'The University of Lahore': 7,
#     'Lahore university of Management Science (LUMS)': 8,
#     'University of Agriculture Faisalabad': 9,
#     'Bahauddin Zakariya University': 10,
#     'International Islamic University Islamabad': 11,
#     'The Aga Khan University': 12,
#     'Abdul Wali Khan University Mardan': 13,
#     'University of Azad Jammu & Kashmir': 14,
#     'Mohi-ud-din Islamic University, Mir Pur (ajk)': 15
# }

# # Reverse the mapping to get university names by index
# universities_reverse = {v: k for k, v in universities.items()}

# @app.route('/predict', methods=['POST'])
# def predict():
#     if not model_loaded:
#         return jsonify({'error': 'Model is not loaded'}), 500

#     try:
#         data = request.get_json()
        
#         df = pd.DataFrame([data])

#         print("DataFrame:\n", df)

#         prediction = model.predict(df)
#         # Assuming the model prediction is a single integer value
#         predicted_index = int(prediction[0])  # Convert to integer
#         university_name = universities_reverse.get(predicted_index, 'Unknown University')

#         return jsonify({'university': university_name})

#     except Exception as e:
#         print("Error:", str(e))
#         return jsonify({'error': str(e)}), 400

# @app.route('/logout')
# @login_required
# def logout():
#     logout_user()
#     return redirect(url_for('index'))

# if __name__ == '__main__':
#     # Ensure the JSON file exists
#     if not os.path.exists(db_file):
#         with open(db_file, 'w') as file:
#             json.dump({}, file)
#     app.run(debug=True)




from flask import Flask, render_template, redirect, url_for, request, flash, jsonify, session
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, FloatField
from wtforms.validators import InputRequired, Length, Email
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy
import os
import json
import pickle
import pandas as pd
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash  # Import hashing functions

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'  # Use SQLite for simplicity
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

Bootstrap(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# File path for the model
model_file_path = 'Knn_model.pkl'  # Updated path

# Load the model
model_loaded = False
model_error = ""

try:
    if os.path.exists(model_file_path):
        with open(model_file_path, 'rb') as model_file:
            model = pickle.load(model_file)
        model_loaded = True
        print("Model loaded successfully.")
    else:
        model_error = f"Model file {model_file_path} not found."
except Exception as e:
    print(f"An Error Occured: {e}")
    model_error = str(e)

# Define User model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), Length(min=4, max=20)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=5, max=80)])
    remember = BooleanField('Remember me')

class RegisterForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired(), Email(), Length(min=6, max=30)])
    username = StringField('Username', validators=[InputRequired(), Length(min=4, max=20)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=5, max=80)])

class PredictionForm(FlaskForm):
    admission_marks = FloatField('Admission Marks', id='admission_marks', validators=[InputRequired()])
    minimum_entry_mark = FloatField('Minimum Entry Mark', id='minimum_entry_mark', validators=[InputRequired()])
    fees_structure = FloatField('Fees Structure', id='fees_structure', validators=[InputRequired()])
    departments_offered = StringField('Departments Offered', id='departments_offered', validators=[InputRequired()])

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == "POST":
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        new_user = User(username=username, email=email)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        return redirect('/login')
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            session['email'] = user.email
            login_user(user)
            return redirect('/dashboard')
        else:
            return render_template('login.html', error='Invalid user')
    return render_template('login.html')

@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    form = PredictionForm()
    if form.validate_on_submit():
        if not model_loaded:
            flash('Model is not loaded', 'danger')
        else:
            try:
                data = {
                    "Admission_marks": form.admission_marks.data,
                    "Minimum_entry_mark": form.minimum_entry_mark.data,
                    "Fees_structure": form.fees_structure.data,
                    "Departments_Offered": form.departments_offered.data
                }

                df = pd.DataFrame([data])
                expected_columns = ['Admission_marks', 'Minimum_entry_mark', 'Fees_structure', 'Departments_Offered']
                if not all(col in df.columns for col in expected_columns):
                    flash('Data format mismatch', 'danger')
                    return render_template('dashboard.html', name=current_user.username, form=form)

                prediction = model.predict(df)
                flash(f'Prediction: {prediction[0]}', 'success')

            except Exception as e:
                flash(f'Error: {str(e)}', 'danger')

    return render_template('dashboard.html', name=current_user.username, form=form)

@app.route('/check_model', methods=['GET'])
def check_model():
    if model_loaded:
        return jsonify({'status': 'Model loaded successfully'})
    else:
        return jsonify({'error': f'Model failed to load: {model_error}'}), 500

universities = {
    'Quaid-i-Azam University': 0,
    'COMSATS University Islamabad': 1,
    'National University of Sciences and Technology': 2,
    'University of the Punjab': 3,
    'University of Engineering and Technology, Lahore': 4,
    'University of Peshawar': 5,
    'Government College University Faisalabad': 6,
    'The University of Lahore': 7,
    'Lahore university of Management Science (LUMS)': 8,
    'University of Agriculture Faisalabad': 9,
    'Bahauddin Zakariya University': 10,
    'International Islamic University Islamabad': 11,
    'The Aga Khan University': 12,
    'Abdul Wali Khan University Mardan': 13,
    'University of Azad Jammu & Kashmir': 14,
    'Mohi-ud-din Islamic University, Mir Pur (ajk)': 15
}

universities_reverse = {v: k for k, v in universities.items()}

@app.route('/predict', methods=['POST'])
def predict():
    if not model_loaded:
        return jsonify({'error': 'Model is not loaded'}), 500

    try:
        data = request.get_json()
        df = pd.DataFrame([data])
        print("DataFrame:\n", df)

        prediction = model.predict(df)
        predicted_index = int(prediction[0])
        university_name = universities_reverse.get(predicted_index, 'Unknown University')

        return jsonify({'university': university_name})

    except Exception as e:
        print("Error:", str(e))
        return jsonify({'error': str(e)}), 400

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
