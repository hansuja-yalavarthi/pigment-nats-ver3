# Email Configuration Template
# Copy this file to config.py and update with your actual email credentials

# Gmail Configuration (Recommended)
MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 587
MAIL_USE_TLS = True
MAIL_USERNAME = 'your-email@gmail.com'  # Replace with your Gmail address
MAIL_PASSWORD = 'your-app-password'     # Replace with your Gmail app password
MAIL_DEFAULT_SENDER = 'your-email@gmail.com'

# Alternative: Outlook/Hotmail Configuration
# MAIL_SERVER = 'smtp-mail.outlook.com'
# MAIL_PORT = 587
# MAIL_USE_TLS = True
# MAIL_USERNAME = 'your-email@outlook.com'
# MAIL_PASSWORD = 'your-password'
# MAIL_DEFAULT_SENDER = 'your-email@outlook.com'

# Alternative: Yahoo Configuration
# MAIL_SERVER = 'smtp.mail.yahoo.com'
# MAIL_PORT = 587
# MAIL_USE_TLS = True
# MAIL_USERNAME = 'your-email@yahoo.com'
# MAIL_PASSWORD = 'your-app-password'
# MAIL_DEFAULT_SENDER = 'your-email@yahoo.com'

# Instructions for Gmail:
# 1. Enable 2-factor authentication on your Gmail account
# 2. Generate an App Password:
#    - Go to Google Account settings
#    - Security > 2-Step Verification > App passwords
#    - Generate a new app password for "Mail"
#    - Use this password in MAIL_PASSWORD above
# 3. Replace 'your-email@gmail.com' with your actual Gmail address
# 4. Replace 'your-app-password' with the generated app password

# Instructions for Outlook/Hotmail:
# 1. Enable 2-factor authentication
# 2. Generate an app password in your Microsoft account settings
# 3. Use your regular password if 2FA is not enabled

# Instructions for Yahoo:
# 1. Enable 2-factor authentication
# 2. Generate an app password in your Yahoo account settings 