#!/usr/bin/env python3
"""
Database repair utility for the finance application.
This script ensures all user databases have the required tables.
"""

import sqlite3
import os
from app import User, db, init_user_db, decrypt_data

def repair_user_database(username):
    """Repair a specific user's database by creating missing tables"""
    try:
        print(f"Repairing database for user: {username}")
        init_user_db(username)
        print(f"✓ Successfully repaired database for user: {username}")
        return True
    except Exception as e:
        print(f"✗ Error repairing database for user {username}: {e}")
        return False

def repair_all_databases():
    """Repair all user databases"""
    print("Starting database repair process...")
    
    # Get all users from the main database
    try:
        with db.app.app_context():
            users = User.query.all()
            print(f"Found {len(users)} users in the database")
            
            success_count = 0
            for user in users:
                try:
                    username = decrypt_data(user.username.encode())
                    if repair_user_database(username):
                        success_count += 1
                except Exception as e:
                    print(f"✗ Error processing user ID {user.id}: {e}")
            
            print(f"\nRepair completed: {success_count}/{len(users)} databases repaired successfully")
            
    except Exception as e:
        print(f"Error accessing user database: {e}")

if __name__ == "__main__":
    repair_all_databases() 