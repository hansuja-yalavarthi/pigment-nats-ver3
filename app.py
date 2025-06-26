from flask import Flask, render_template, request, redirect, url_for, session, flash, send_from_directory, jsonify, Response, send_file
from datetime import datetime, timedelta, timezone
import sqlite3
import csv
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_mail import Mail, Message
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadTimeSignature
import json
import re
import os
from cryptography.fernet import Fernet
from base64 import b64encode, b64decode
from ai_chatbot import AIChatbot

# Initialize Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Load email configuration from config file if it exists
try:
    from config import *
    app.config['MAIL_SERVER'] = MAIL_SERVER
    app.config['MAIL_PORT'] = MAIL_PORT
    app.config['MAIL_USE_TLS'] = MAIL_USE_TLS
    app.config['MAIL_USERNAME'] = MAIL_USERNAME
    app.config['MAIL_PASSWORD'] = MAIL_PASSWORD
    app.config['MAIL_DEFAULT_SENDER'] = MAIL_DEFAULT_SENDER
    print("Email configuration loaded from config.py")
except ImportError:
    # Default email configuration (for development)
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = 'your-email@gmail.com'  # Replace with your email
    app.config['MAIL_PASSWORD'] = 'your-app-password'     # Replace with your app password
    app.config['MAIL_DEFAULT_SENDER'] = 'your-email@gmail.com'
    print("Warning: No config.py found. Using default email configuration.")
    print("Please create config.py with your email settings (see config_template.py)")

# Initialize database, login manager, and mail
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"
mail = Mail(app)
serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])

# Create database tables
with app.app_context():
    db.create_all()

# User model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    email_verified = db.Column(db.Boolean, default=False)
    email_verification_token = db.Column(db.String(200), nullable=True)
    password_reset_token = db.Column(db.String(200), nullable=True)
    password_reset_expires = db.Column(db.DateTime, nullable=True)

    def __init__(self, username, email, password):
        self.username = encrypt_data(username).decode()
        self.email = email
        self.password = password

    def get_username(self):
        return decrypt_data(self.username.encode())

    @staticmethod
    def get_by_username(username):
        try:
            # First, try to find user with encrypted username (new method)
            encrypted_username = encrypt_data(username).decode()
            print(f"Looking for user with encrypted username: {encrypted_username}")
            
            user = User.query.filter_by(username=encrypted_username).first()
            if user:
                print(f"Found user with encrypted username")
                return user
            
            # If not found, try to find user with plain text username (backward compatibility)
            print(f"User not found with encrypted username, trying plain text")
            user = User.query.filter_by(username=username).first()
            if user:
                print(f"Found user with plain text username - migrating to encrypted")
                # Migrate the user to encrypted username
                try:
                    user.username = encrypted_username
                    db.session.commit()
                    print(f"Successfully migrated user {username} to encrypted username")
                except Exception as e:
                    print(f"Error migrating user: {e}")
                    db.session.rollback()
                return user
            
            # If still not found, check if there are any users with corrupted encryption
            # that might match this username by checking all users
            print(f"Checking for users with corrupted encryption...")
            all_users = User.query.all()
            for user in all_users:
                try:
                    # Try to decrypt the username
                    decrypted_username = decrypt_data(user.username.encode())
                    if decrypted_username == username:
                        print(f"Found user with corrupted encryption, user ID: {user.id}")
                        return user
                except:
                    # If decryption fails, this user has corrupted encryption
                    # We can't recover it automatically, but we can note it
                    continue
            
            print(f"User not found with any method")
            return None
            
        except Exception as e:
            print(f"Error in get_by_username: {e}")
            return None

    @staticmethod
    def get_by_email(email):
        return User.query.filter_by(email=email).first()

    @staticmethod
    def get_corrupted_users():
        """Get all users with corrupted encryption that can't be decrypted"""
        corrupted_users = []
        try:
            all_users = User.query.all()
            for user in all_users:
                try:
                    decrypt_data(user.username.encode())
                except:
                    corrupted_users.append(user)
            return corrupted_users
        except Exception as e:
            print(f"Error getting corrupted users: {e}")
            return []

    def fix_username(self, new_username):
        """Fix a corrupted username by setting it to a new encrypted value"""
        try:
            self.username = encrypt_data(new_username).decode()
            db.session.commit()
            return True
        except Exception as e:
            print(f"Error fixing username: {e}")
            db.session.rollback()
            return False

    def generate_email_verification_token(self):
        """Generate a token for email verification"""
        self.email_verification_token = serializer.dumps(self.email, salt='email-verification')
        db.session.commit()
        return self.email_verification_token

    def generate_password_reset_token(self):
        """Generate a token for password reset"""
        self.password_reset_token = serializer.dumps(self.email, salt='password-reset')
        self.password_reset_expires = datetime.now(timezone.utc) + timedelta(hours=1)
        db.session.commit()
        return self.password_reset_token

    def verify_email_token(self, token):
        """Verify email verification token"""
        try:
            email = serializer.loads(token, salt='email-verification', max_age=86400)  # 24 hours
            if email == self.email:
                self.email_verified = True
                self.email_verification_token = None
                db.session.commit()
                return True
        except (SignatureExpired, BadTimeSignature):
            pass
        return False

    def verify_password_reset_token(self, token):
        """Verify password reset token"""
        try:
            email = serializer.loads(token, salt='password-reset', max_age=3600)  # 1 hour
            if email == self.email and self.password_reset_expires and datetime.now(timezone.utc) < self.password_reset_expires:
                return True
        except (SignatureExpired, BadTimeSignature):
            pass
        return False

# Email sending functions
def send_email_verification(user):
    """Send email verification email"""
    try:
        print(f"Attempting to send verification email to: {user.email}")
        token = user.generate_email_verification_token()
        verification_url = url_for('verify_email', token=token, _external=True)
        
        msg = Message('Verify Your Email - Pigment',
                     recipients=[user.email])
        msg.html = render_template('email_verification.html', 
                                 username=user.get_username(),
                                 verification_url=verification_url)
        
        print(f"Sending email to {user.email} with verification URL: {verification_url}")
        mail.send(msg)
        print(f"Email verification sent successfully to {user.email}")
        return True
    except Exception as e:
        print(f"Error sending email verification to {user.email}: {e}")
        print(f"Error type: {type(e)}")
        import traceback
        traceback.print_exc()
        return False

def send_password_reset_email(user):
    """Send password reset email"""
    try:
        print(f"Attempting to send password reset email to: {user.email}")
        token = user.generate_password_reset_token()
        reset_url = url_for('reset_password', token=token, _external=True)
        
        msg = Message('Reset Your Password - Pigment',
                     recipients=[user.email])
        msg.html = render_template('password_reset_email.html', 
                                 username=user.get_username(),
                                 reset_url=reset_url)
        
        print(f"Sending password reset email to {user.email} with reset URL: {reset_url}")
        mail.send(msg)
        print(f"Password reset email sent successfully to {user.email}")
        return True
    except Exception as e:
        print(f"Error sending password reset email to {user.email}: {e}")
        print(f"Error type: {type(e)}")
        import traceback
        traceback.print_exc()
        return False

# Load user function for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    print(f"Loading user with ID: {user_id}")
    user = User.query.get(int(user_id))
    print(f"Loaded user: {user is not None}")
    return user

# Route for Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        print(f"Login attempt for username: {username}")
        
        if not username or not password:
            flash('Please enter both username and password', 'danger')
            return redirect(url_for('login'))
        
        try:
            user = User.get_by_username(username)
            print(f"User found: {user is not None}")
            
            if user:
                print("Checking password hash")
                if check_password_hash(user.password, password):
                    print("Password check passed")
                    
                    # Check if email is verified
                    if not user.email_verified:
                        flash('Please verify your email address before logging in. Check your inbox or request a new verification email.', 'warning')
                        return redirect(url_for('login'))
                    
                    login_user(user)
                    print(f"User {username} logged in successfully")
                    
                    # Ensure user's database has all required tables
                    ensure_user_db_integrity(username)
                    
                    return redirect(url_for('login_landing'))
                else:
                    print("Password check failed")
            else:
                print("User not found")
                
            flash('Invalid username or password', 'danger')
        except Exception as e:
            print(f"Login error: {e}")
            flash('An error occurred during login. Please try again.', 'danger')
            
    return render_template('login.html')

# Route for Login Landing Page
@app.route('/loginLanding')
@login_required
def login_landing():
    if not current_user.is_authenticated:
        print("User not authenticated, redirecting to login")
        return redirect(url_for('login'))
    print(f"User authenticated: {current_user.get_username()}")
    return render_template('loginLanding.html')

# Route for Signup
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        print(f"Signup attempt for username: {username}")
        
        # Validate email format
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            flash('Please enter a valid email address', 'danger')
            return redirect(url_for('signup'))
        
        # Validate password requirements
        is_valid, message = validate_password(password)
        if not is_valid:
            print(f"Password validation failed: {message}")
            flash(message, 'danger')
            return redirect(url_for('signup'))
        
        hashed_password = generate_password_hash(password)

        if User.get_by_username(username):
            print(f"Username {username} already exists")
            flash('Username already exists. Please choose a different one.', 'danger')
            return redirect(url_for('signup'))

        if User.get_by_email(email):
            print(f"Email {email} already exists")
            flash('Email already exists. Please use a different email or login.', 'danger')
            return redirect(url_for('signup'))

        try:
            new_user = User(username=username, email=email, password=hashed_password)
            db.session.add(new_user)
            db.session.commit()
            
            print(f"User {username} created successfully with email {email}")
            
            # Send email verification
            print(f"Attempting to send verification email for user {username}")
            if send_email_verification(new_user):
                flash('Account created successfully! Please check your email to verify your account.', 'success')
                print(f"Verification email sent successfully for user {username}")
            else:
                flash('Account created successfully! However, there was an issue sending the verification email. Please contact support.', 'warning')
                print(f"Failed to send verification email for user {username}")
            
            print(f"User {username} created successfully")
            return redirect(url_for('signup_landing'))
            
        except Exception as e:
            print(f"Error creating user: {e}")
            db.session.rollback()
            flash('An error occurred during signup. Please try again.', 'danger')
            return redirect(url_for('signup'))
            
    return render_template('signup.html')

# Route for Email Verification
@app.route('/verify-email/<token>')
def verify_email(token):
    try:
        # Find user by verification token
        user = User.query.filter_by(email_verification_token=token).first()
        if user and user.verify_email_token(token):
            # Initialize user's database after email verification
            init_user_db(user.get_username())
            print(f"User database initialized for {user.get_username()}")
            flash('Email verified successfully! You can now login.', 'success')
            return redirect(url_for('login'))
        else:
            flash('Invalid or expired verification link. Please request a new one.', 'danger')
            return redirect(url_for('login'))
    except Exception as e:
        print(f"Email verification error: {e}")
        flash('An error occurred during email verification. Please try again.', 'danger')
        return redirect(url_for('login'))

# Route for Resend Email Verification
@app.route('/resend-verification', methods=['GET', 'POST'])
def resend_verification():
    if request.method == 'POST':
        email = request.form.get('email')
        if not email:
            flash('Please enter your email address', 'danger')
            return redirect(url_for('resend_verification'))
        
        user = User.get_by_email(email)
        if user and not user.email_verified:
            if send_email_verification(user):
                flash('Verification email sent! Please check your inbox.', 'success')
            else:
                flash('Failed to send verification email. Please try again later.', 'danger')
        else:
            flash('Email not found or already verified.', 'info')
        
        return redirect(url_for('login'))
    
    return render_template('resend_verification.html')

# Generate encryption key
def generate_key():
    return Fernet.generate_key()

# Initialize encryption
def init_encryption():
    key_file = 'encryption_key.key'
    try:
        if os.path.exists(key_file):
            with open(key_file, 'rb') as f:
                key = f.read()
        else:
            key = generate_key()
            with open(key_file, 'wb') as f:
                f.write(key)
        return Fernet(key)
    except Exception as e:
        print(f"Error initializing encryption: {e}")
        # Fallback: generate new key
        key = generate_key()
        with open(key_file, 'wb') as f:
            f.write(key)
        return Fernet(key)

# Initialize fernet globally
fernet = init_encryption()

# ------------------------------- Database Initialization -------------------------------
def get_user_db_path(username):
    """Get the path to a user's specific database file"""
    return f'finances_{username}.db'

def init_user_db(username):
    """Initialize a new database for a specific user"""
    db_path = get_user_db_path(username)
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # Transactions table: Logs income and expenses with details.
    c.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT NOT NULL,
            category TEXT NOT NULL,
            amount REAL NOT NULL,
            date TEXT NOT NULL,
            description TEXT
        )
    ''')

    # Budget table: Stores budget limits for specific categories.
    c.execute('''
        CREATE TABLE IF NOT EXISTS budgets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            budget_limit REAL NOT NULL
        )
    ''')

    # Savings Goals table: tracks savings goals with target amounts and progress.
    c.execute('''
        CREATE TABLE IF NOT EXISTS savings_goals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            goal_name TEXT NOT NULL,
            target_amount REAL NOT NULL,
            current_savings REAL NOT NULL,
            due_date TEXT
        )
    ''')

    conn.commit()
    conn.close()

def get_db_connection(username):
    """Get a database connection for the current user"""
    if not username:
        return None
    db_path = get_user_db_path(username)
    return sqlite3.connect(db_path)

def ensure_user_db_integrity(username):
    """Ensure all required tables exist in user's database"""
    try:
        init_user_db(username)  # This will create any missing tables
        print(f"Ensured database integrity for user: {username}")
        return True
    except Exception as e:
        print(f"Error ensuring database integrity for user {username}: {e}")
        return False

# Helper functions for encryption/decryption
def encrypt_data(data):
    if isinstance(data, (int, float)):
        data = str(data)
    return fernet.encrypt(data.encode())

def decrypt_data(encrypted_data):
    if encrypted_data is None:
        return None
    return fernet.decrypt(encrypted_data).decode()

# ------------------------------- Routes -------------------------------
@app.route('/')
def index():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    
    username = current_user.get_username()
    # Ensure user database has all required tables
    init_user_db(username)
    
    conn = get_db_connection(username)
    if not conn:
        return redirect(url_for('login'))
        
    c = conn.cursor()
    
    try:
        # Fetch all transactions
        c.execute("SELECT * FROM transactions")
        transactions = c.fetchall()

        # Calculate total income and expenses
        c.execute("SELECT SUM(amount) FROM transactions WHERE type='income'")
        total_income = c.fetchone()[0] or 0
        c.execute("SELECT SUM(amount) FROM transactions WHERE type='expense'")
        total_expense = c.fetchone()[0] or 0
        current_balance = total_income - total_expense
    except sqlite3.OperationalError:
        # If transactions table doesn't exist, create it and return empty data
        c.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type TEXT NOT NULL,
                category TEXT NOT NULL,
                amount REAL NOT NULL,
                date TEXT NOT NULL,
                description TEXT
            )
        ''')
        conn.commit()
        transactions = []
        total_income = 0
        total_expense = 0
        current_balance = 0

    conn.close()

    budgets = {
        'food': 500,
        'salary': 0,  # No limit for income
        'gifts': 200,
        'rent': 1000,
    }
    return render_template('index.html', transactions=transactions, balance=current_balance, income=total_income, expense=total_expense, budgets_json=json.dumps(budgets))

@app.route('/add', methods=['GET', 'POST'])
@login_required
def add_transaction():
    if request.method == 'POST':
        # Retrieve form data
        transaction_type = request.form['type']
        category = request.form['category']
        amount = float(request.form['amount'])
        date = request.form['date']
        description = request.form['description']

        # Insert the new transaction into the database
        conn = get_db_connection(current_user.get_username())
        c = conn.cursor()
        c.execute('''INSERT INTO transactions (type, category, amount, date, description) 
                     VALUES (?, ?, ?, ?, ?)''', 
                  (transaction_type, category, amount, date, description))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))

    return render_template('add.html')

@app.route('/edit_transaction', methods=['POST'])
@login_required
def edit_transaction():
    transaction_id = request.form['transaction_id']
    transaction_type = request.form['type']
    category = request.form['category']
    amount = request.form['amount']
    date = request.form['date']
    description = request.form['description']

    conn = get_db_connection(current_user.get_username())
    c = conn.cursor()

    c.execute('''UPDATE transactions
                 SET type = ?, category = ?, amount = ?, date = ?, description = ?
                 WHERE id = ?''', 
              (transaction_type, category, amount, date, description, transaction_id))
    
    conn.commit()

    if c.rowcount > 0:
        conn.close()
        return jsonify({'success': True})
    else:
        conn.close()
        return jsonify({'success': False, 'message': 'Transaction not found'})

@app.route('/delete/<int:transaction_id>', methods=['DELETE'])
@login_required
def delete_transaction(transaction_id):
    conn = get_db_connection(current_user.get_username())
    c = conn.cursor()
    c.execute("DELETE FROM transactions WHERE id=?", (transaction_id,))
    conn.commit()

    if c.rowcount > 0:
        conn.close()
        return jsonify({'success': True})
    else:
        conn.close()
        return jsonify({'success': False, 'error': 'Transaction not found'}), 404

@app.route('/transaction/<int:transaction_id>')
@login_required
def get_transaction_details(transaction_id):
    conn = get_db_connection(current_user.get_username())
    c = conn.cursor()
    c.execute("SELECT * FROM transactions WHERE id=?", (transaction_id,))
    transaction = c.fetchone()
    conn.close()

    if transaction:
        return jsonify({
            'id': transaction[0],
            'type': transaction[1],
            'category': transaction[2],
            'amount': transaction[3],
            'date': transaction[4],
            'description': transaction[5]
        })
    else:
        return jsonify({'error': 'Transaction not found'}), 404

@app.route('/export/csv')
@login_required
def export_csv():
    conn = get_db_connection(current_user.get_username())
    c = conn.cursor()
    c.execute("SELECT * FROM transactions")
    transactions = c.fetchall()
    conn.close()

    csv_data = [['ID', 'Type', 'Category', 'Amount', 'Date', 'Description']]
    csv_data += [[t[0], t[1], t[2], t[3], t[4], t[5]] for t in transactions]

    def generate():
        for row in csv_data:
            yield ','.join(map(str, row)) + '\n'

    return Response(generate(), mimetype='text/csv', headers={
        'Content-Disposition': 'attachment;filename=transactions.csv'
    })

@app.route('/export/pdf')
@login_required
def export_pdf():
    conn = get_db_connection(current_user.get_username())
    c = conn.cursor()
    c.execute("SELECT * FROM transactions")
    transactions = c.fetchall()
    conn.close()

    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    c.drawString(100, 750, "Transactions Report")
    c.drawString(50, 730, "ID    Type    Category    Amount    Date    Description")

    y = 710
    for t in transactions:
        c.drawString(50, y, f"{t[0]}  {t[1]}  {t[2]}  ${t[3]}  {t[4]}  {t[5]}")
        y -= 20
        if y < 50:
            c.showPage()
            y = 750

    c.save()
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name="transactions.pdf", mimetype='application/pdf')

@app.route('/budgeting', methods=['GET', 'POST'])
@login_required
def budgeting():
    # Ensure user database has all required tables
    username = current_user.get_username()
    init_user_db(username)  # This will create missing tables if they don't exist
    
    if request.method == 'POST':
        conn = get_db_connection(username)
        c = conn.cursor()
        
        if 'category' in request.form and 'budget_limit' in request.form:
            category = request.form['category']
            budget_limit = float(request.form['budget_limit'])

            c.execute('''INSERT INTO budgets (category, budget_limit) VALUES (?, ?)''', 
                      (category, budget_limit))
            conn.commit()
        
        if 'goal_name' in request.form and 'target_amount' in request.form and 'current_savings' in request.form:
            goal_name = request.form['goal_name']
            target_amount = float(request.form['target_amount'])
            current_savings = float(request.form['current_savings'])
            due_date = request.form['due_date']

            c.execute('''INSERT INTO savings_goals (goal_name, target_amount, current_savings, due_date)
                         VALUES (?, ?, ?, ?)''', 
                      (goal_name, target_amount, current_savings, due_date))
            conn.commit()

        conn.close()
        return redirect(url_for('budgeting'))

    conn = get_db_connection(username)
    c = conn.cursor()

    try:
        c.execute("SELECT * FROM budgets")
        budgets = c.fetchall()
    except sqlite3.OperationalError:
        # If budgets table doesn't exist, create it and return empty list
        c.execute('''
            CREATE TABLE IF NOT EXISTS budgets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                budget_limit REAL NOT NULL
            )
        ''')
        conn.commit()
        budgets = []

    try:
        c.execute("SELECT * FROM savings_goals")
        goals = c.fetchall()
    except sqlite3.OperationalError:
        # If savings_goals table doesn't exist, create it and return empty list
        c.execute('''
            CREATE TABLE IF NOT EXISTS savings_goals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                goal_name TEXT NOT NULL,
                target_amount REAL NOT NULL,
                current_savings REAL NOT NULL,
                due_date TEXT
            )
        ''')
        conn.commit()
        goals = []

    # Fetch transaction data for charts
    try:
        # Pie Chart Data: Spending by category (expenses only)
        c.execute("""
            SELECT category, SUM(amount) as total_amount 
            FROM transactions 
            WHERE type = 'expense' 
            GROUP BY category 
            ORDER BY total_amount DESC
        """)
        category_spending = c.fetchall()
        
        # Bar Chart Data: Weekly spending
        c.execute("""
            SELECT 
                strftime('%Y-%W', date) as week,
                SUM(amount) as total_amount
            FROM transactions 
            WHERE type = 'expense'
            GROUP BY strftime('%Y-%W', date)
            ORDER BY week DESC
            LIMIT 8
        """)
        weekly_spending = c.fetchall()
        
        # Bar Chart Data: Monthly spending
        c.execute("""
            SELECT 
                strftime('%Y-%m', date) as month,
                SUM(amount) as total_amount
            FROM transactions 
            WHERE type = 'expense'
            GROUP BY strftime('%Y-%m', date)
            ORDER BY month DESC
            LIMIT 12
        """)
        monthly_spending = c.fetchall()
        
    except sqlite3.OperationalError:
        # If transactions table doesn't exist, create it and return empty data
        c.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type TEXT NOT NULL,
                category TEXT NOT NULL,
                amount REAL NOT NULL,
                date TEXT NOT NULL,
                description TEXT
            )
        ''')
        conn.commit()
        category_spending = []
        weekly_spending = []
        monthly_spending = []

    conn.close()

    # Prepare data for charts
    pie_chart_data = {
        'labels': [item[0] for item in category_spending] if category_spending else ['No Data'],
        'data': [float(item[1]) for item in category_spending] if category_spending else [0]
    }
    
    # Format weekly data with readable labels
    weekly_chart_data = {
        'labels': [],
        'data': []
    }
    
    if weekly_spending:
        for week, amount in reversed(weekly_spending):  # Reverse to show chronologically
            # Convert week format (YYYY-WW) to readable format
            year, week_num = week.split('-')
            weekly_chart_data['labels'].append(f"Week {week_num}, {year}")
            weekly_chart_data['data'].append(float(amount))
    else:
        weekly_chart_data = {'labels': ['No Data'], 'data': [0]}
    
    # Format monthly data with readable labels
    monthly_chart_data = {
        'labels': [],
        'data': []
    }
    
    if monthly_spending:
        month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                      'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        for month, amount in reversed(monthly_spending):  # Reverse to show chronologically
            # Convert month format (YYYY-MM) to readable format
            year, month_num = month.split('-')
            month_name = month_names[int(month_num) - 1]
            monthly_chart_data['labels'].append(f"{month_name} {year}")
            monthly_chart_data['data'].append(float(amount))
    else:
        monthly_chart_data = {'labels': ['No Data'], 'data': [0]}

    return render_template('budgeting.html', 
                         budgets=budgets, 
                         goals=goals,
                         pie_chart_data=json.dumps(pie_chart_data),
                         weekly_chart_data=json.dumps(weekly_chart_data),
                         monthly_chart_data=json.dumps(monthly_chart_data))

@app.route('/signupLanding')
def signup_landing():
    return render_template('signupLanding.html')

@app.route('/contact')
def contact_page():
    return render_template('contact.html')

@app.route('/home')
def home_page():
    return render_template('home.html')

def validate_password(password):
    """
    Validates password requirements:
    - Minimum 7 characters
    - At least one special character
    - At least one number
    """
    if len(password) < 7:
        return False, "Password must be at least 7 characters long"
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Password must contain at least one special character"
    
    if not re.search(r'\d', password):
        return False, "Password must contain at least one number"
    
    return True, "Password is valid"

# Route for Logout
@app.route('/logout')
@login_required
def logout():
    print(f"Logging out user: {current_user.get_username()}")
    logout_user()
    return redirect(url_for('login'))

# Debug route to check database contents
@app.route('/debug')
def debug_database():
    try:
        all_users = User.query.all()
        debug_info = {
            'total_users': len(all_users),
            'users': []
        }
        
        for user in all_users:
            try:
                decrypted_username = decrypt_data(user.username.encode())
                debug_info['users'].append({
                    'id': user.id,
                    'encrypted_username': user.username,
                    'decrypted_username': decrypted_username,
                    'password_hash': user.password[:20] + '...' if user.password else 'None'
                })
            except Exception as e:
                debug_info['users'].append({
                    'id': user.id,
                    'encrypted_username': user.username,
                    'error': str(e),
                    'password_hash': user.password[:20] + '...' if user.password else 'None'
                })
        
        return jsonify(debug_info)
    except Exception as e:
        return jsonify({'error': str(e)})

# Forgot Password route
@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        if not email:
            flash('Please enter your email address', 'danger')
            return redirect(url_for('forgot_password'))
        
        user = User.get_by_email(email)
        if user:
            if send_password_reset_email(user):
                flash('Password reset email sent! Please check your inbox.', 'success')
            else:
                flash('Failed to send password reset email. Please try again later.', 'danger')
        else:
            # Don't reveal if email exists or not for security
            flash('If an account with that email exists, a password reset link has been sent.', 'info')
        
        return redirect(url_for('login'))
    
    return render_template('forgot_password.html')

# Reset Password route
@app.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    try:
        # Find user by reset token
        user = User.query.filter_by(password_reset_token=token).first()
        if not user or not user.verify_password_reset_token(token):
            flash('Invalid or expired password reset link. Please request a new one.', 'danger')
            return redirect(url_for('forgot_password'))
        
        if request.method == 'POST':
            password = request.form.get('password')
            confirm_password = request.form.get('confirm_password')
            
            if not password or not confirm_password:
                flash('Please fill in all fields', 'danger')
                return render_template('reset_password.html')
            
            if password != confirm_password:
                flash('Passwords do not match', 'danger')
                return render_template('reset_password.html')
            
            # Validate password requirements
            is_valid, message = validate_password(password)
            if not is_valid:
                flash(message, 'danger')
                return render_template('reset_password.html')
            
            # Update password
            user.password = generate_password_hash(password)
            user.password_reset_token = None
            user.password_reset_expires = None
            db.session.commit()
            
            flash('Password reset successfully! You can now login with your new password.', 'success')
            return redirect(url_for('login'))
        
        return render_template('reset_password.html')
        
    except Exception as e:
        print(f"Password reset error: {e}")
        flash('An error occurred during password reset. Please try again.', 'danger')
        return redirect(url_for('forgot_password'))

# User recovery route for corrupted accounts (keeping for backward compatibility)
@app.route('/recover', methods=['GET', 'POST'])
def recover_account():
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        new_username = request.form.get('new_username')
        password = request.form.get('password')
        
        if not user_id or not new_username or not password:
            flash('Please fill in all fields', 'danger')
            return redirect(url_for('recover_account'))
        
        try:
            user = User.query.get(int(user_id))
            if not user:
                flash('User not found', 'danger')
                return redirect(url_for('recover_account'))
            
            # Verify password
            if not check_password_hash(user.password, password):
                flash('Invalid password', 'danger')
                return redirect(url_for('recover_account'))
            
            # Check if new username already exists
            if User.get_by_username(new_username):
                flash('Username already exists', 'danger')
                return redirect(url_for('recover_account'))
            
            # Fix the username
            if user.fix_username(new_username):
                flash(f'Account recovered! You can now login with username: {new_username}', 'success')
                return redirect(url_for('login'))
            else:
                flash('Error recovering account', 'danger')
                
        except Exception as e:
            flash(f'Error: {str(e)}', 'danger')
    
    # Get corrupted users for display
    corrupted_users = User.get_corrupted_users()
    return render_template('recover.html', corrupted_users=corrupted_users)

# AI Chatbot route
@app.route('/chatbot', methods=['POST'])
@login_required
def chatbot():
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({'error': 'No message provided'}), 400
        
        # Initialize chatbot
        chatbot = AIChatbot()
        
        # Get user context
        username = current_user.get_username()
        user_context = chatbot.get_user_financial_context(username)
        
        # Get AI response
        bot_response = chatbot.get_ai_response(user_message, user_context)
        
        # Add to conversation history
        chatbot.add_to_history(user_message, bot_response)
        
        return jsonify({
            'response': bot_response,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        print(f"Chatbot error: {e}")
        return jsonify({
            'response': "I'm sorry, I'm having trouble processing your request right now. Please try again later.",
            'error': str(e)
        }), 500

# Chatbot history route
@app.route('/chatbot/history')
@login_required
def chatbot_history():
    try:
        chatbot = AIChatbot()
        history = chatbot.get_conversation_history()
        return jsonify({'history': history})
    except Exception as e:
        print(f"Error getting chatbot history: {e}")
        return jsonify({'history': []})

if __name__ == '__main__':
    app.run(debug=True)
