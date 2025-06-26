#!/usr/bin/env python3
"""
Database migration script to add email fields to existing users
"""

import sqlite3
import os
from datetime import datetime

def migrate_database():
    """Migrate the existing database to include email fields"""
    
    # Check if the database exists
    if not os.path.exists('instance/users.db'):
        print("Database not found. Creating new database...")
        return
    
    # Connect to the database
    conn = sqlite3.connect('instance/users.db')
    cursor = conn.cursor()
    
    try:
        # Check if email column already exists
        cursor.execute("PRAGMA table_info(user)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'email' not in columns:
            print("Adding email column to user table...")
            cursor.execute("ALTER TABLE user ADD COLUMN email TEXT")
            
            # Add other new columns
            if 'email_verified' not in columns:
                cursor.execute("ALTER TABLE user ADD COLUMN email_verified BOOLEAN DEFAULT 0")
            
            if 'email_verification_token' not in columns:
                cursor.execute("ALTER TABLE user ADD COLUMN email_verification_token TEXT")
            
            if 'password_reset_token' not in columns:
                cursor.execute("ALTER TABLE user ADD COLUMN password_reset_token TEXT")
            
            if 'password_reset_expires' not in columns:
                cursor.execute("ALTER TABLE user ADD COLUMN password_reset_expires DATETIME")
            
            # For existing users, set a placeholder email and mark as verified
            # This allows existing users to continue using the system
            cursor.execute("UPDATE user SET email = 'migrated@example.com', email_verified = 1 WHERE email IS NULL")
            
            conn.commit()
            print("Database migration completed successfully!")
            print("Note: Existing users have been given a placeholder email and marked as verified.")
            print("They should update their email address in their profile.")
        else:
            print("Database already has email fields. No migration needed.")
            
    except Exception as e:
        print(f"Error during migration: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_database() 