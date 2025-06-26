# Email Integration Setup for Pigment Flask App

This document explains how to set up email functionality for the Pigment Flask application, including email verification and password reset features.

## Features Added

1. **Email Verification**: New users must verify their email address before logging in
2. **Password Reset**: Users can reset their password via email
3. **Resend Verification**: Users can request a new verification email
4. **Secure Tokens**: Time-limited tokens for email verification and password reset

## Setup Instructions

### 1. Install Dependencies

First, install the required packages:

```bash
pip install -r requirements.txt
```

### 2. Configure Email Settings

#### Option A: Using Gmail (Recommended)

1. **Enable 2-Factor Authentication** on your Gmail account
2. **Generate an App Password**:
   - Go to [Google Account Settings](https://myaccount.google.com/)
   - Navigate to Security > 2-Step Verification > App passwords
   - Select "Mail" and generate a new app password
3. **Create config.py**:
   ```bash
   cp config_template.py config.py
   ```
4. **Edit config.py** with your Gmail credentials:
   ```python
   MAIL_USERNAME = 'your-email@gmail.com'
   MAIL_PASSWORD = 'your-16-character-app-password'
   MAIL_DEFAULT_SENDER = 'your-email@gmail.com'
   ```

#### Option B: Using Outlook/Hotmail

1. Enable 2-factor authentication on your Microsoft account
2. Generate an app password in your Microsoft account settings
3. Update config.py with Outlook settings:
   ```python
   MAIL_SERVER = 'smtp-mail.outlook.com'
   MAIL_USERNAME = 'your-email@outlook.com'
   MAIL_PASSWORD = 'your-app-password'
   MAIL_DEFAULT_SENDER = 'your-email@outlook.com'
   ```

#### Option C: Using Yahoo

1. Enable 2-factor authentication on your Yahoo account
2. Generate an app password in your Yahoo account settings
3. Update config.py with Yahoo settings:
   ```python
   MAIL_SERVER = 'smtp.mail.yahoo.com'
   MAIL_USERNAME = 'your-email@yahoo.com'
   MAIL_PASSWORD = 'your-app-password'
   MAIL_DEFAULT_SENDER = 'your-email@yahoo.com'
   ```

### 3. Migrate Existing Database

If you have existing users in your database, run the migration script:

```bash
python migrate_database.py
```

This will:
- Add email fields to existing users
- Set a placeholder email for existing users
- Mark existing users as verified (so they can still login)

### 4. Test the Application

1. **Start the application**:
   ```bash
   python app.py
   ```

2. **Test email verification**:
   - Sign up with a new account
   - Check your email for the verification link
   - Click the link to verify your account
   - Try logging in

3. **Test password reset**:
   - Go to login page
   - Click "Reset Password"
   - Enter your email address
   - Check your email for the reset link
   - Follow the link to reset your password

## How It Works

### Email Verification Flow

1. User signs up with username, email, and password
2. System sends verification email with secure token
3. User clicks verification link in email
4. System verifies token and marks email as verified
5. User can now login

### Password Reset Flow

1. User clicks "Forgot Password" on login page
2. User enters email address
3. System sends password reset email with secure token
4. User clicks reset link in email
5. User enters new password
6. System updates password and invalidates token

### Security Features

- **Time-limited tokens**: Email verification tokens expire in 24 hours, password reset tokens expire in 1 hour
- **Secure token generation**: Uses Flask's `itsdangerous` library for secure token generation
- **Email validation**: Validates email format during signup
- **Password requirements**: Enforces strong password requirements
- **Token invalidation**: Tokens are invalidated after use

## Troubleshooting

### Email Not Sending

1. **Check your email configuration** in config.py
2. **Verify your app password** is correct
3. **Check your email provider's settings**:
   - Gmail: Make sure "Less secure app access" is enabled or use app passwords
   - Outlook: Check if 2FA is properly configured
   - Yahoo: Verify app password generation

### Users Can't Login

1. **Check if email verification is required**: New users must verify their email
2. **Run the migration script** if you have existing users
3. **Check the database** for user records

### Database Issues

1. **Run the migration script**: `python migrate_database.py`
2. **Check database file**: Ensure `instance/users.db` exists
3. **Reset database**: Delete `instance/users.db` and restart the app (this will delete all users)

## File Structure

```
pigment-nats-ver1/
├── app.py                          # Main Flask application
├── config_template.py              # Email configuration template
├── config.py                       # Your email configuration (create this)
├── migrate_database.py             # Database migration script
├── requirements.txt                # Python dependencies
├── templates/
│   ├── email_verification.html     # Email verification template
│   ├── password_reset_email.html   # Password reset email template
│   ├── forgot_password.html        # Forgot password page
│   ├── reset_password.html         # Reset password page
│   ├── resend_verification.html    # Resend verification page
│   ├── signup.html                 # Updated signup form
│   └── login.html                  # Updated login form
└── README_EMAIL_SETUP.md           # This file
```

## Security Notes

- **Never commit config.py** to version control (it contains sensitive credentials)
- **Use app passwords** instead of regular passwords for email
- **Enable 2-factor authentication** on your email account
- **Keep your secret key secure** and change it in production
- **Use HTTPS in production** to secure email tokens

## Production Deployment

For production deployment:

1. **Use environment variables** for sensitive configuration
2. **Set up proper email service** (SendGrid, Mailgun, etc.)
3. **Use HTTPS** to secure email tokens
4. **Configure proper logging** for email sending
5. **Set up monitoring** for email delivery rates 