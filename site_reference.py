# Site Reference Sheet for AI Chatbot
# This file contains information about the Pigment app that the AI can reference

SITE_REFERENCE = {
    "app_name": "Pigment",
    "app_description": "A personal finance management application that helps users track expenses, set budgets, and achieve savings goals.",
    
    "core_features": {
        "transaction_tracking": {
            "description": "Track all your income and expenses with detailed categorization",
            "how_to": "Go to the main dashboard and click 'Add Transaction' to log new income or expenses",
            "categories": ["Food", "Transportation", "Entertainment", "Utilities", "Rent", "Salary", "Gifts", "Healthcare", "Education", "Shopping"],
            "details": "Each transaction includes type (income/expense), category, amount, date, and description"
        },
        
        "budget_management": {
            "description": "Set spending limits for different categories and track your progress",
            "how_to": "Navigate to the Budgeting page to set and monitor budget limits",
            "features": [
                "Set monthly budget limits per category",
                "Real-time spending tracking against budgets",
                "Visual progress indicators",
                "Over-budget alerts"
            ]
        },
        
        "savings_goals": {
            "description": "Create and track multiple savings goals with target amounts and deadlines",
            "how_to": "Use the savings goals feature to set targets for emergency funds, vacations, or major purchases",
            "features": [
                "Set target amounts and due dates",
                "Track current progress",
                "Multiple concurrent goals",
                "Progress visualization"
            ]
        },
        
        "financial_reports": {
            "description": "Generate detailed reports and export your financial data",
            "formats": ["CSV export", "PDF reports"],
            "data_included": [
                "Transaction history",
                "Spending summaries",
                "Budget vs actual spending",
                "Savings goal progress"
            ]
        },
        
        "data_export": {
            "description": "Export your financial data for external analysis or backup",
            "formats": {
                "csv": "Comma-separated values format for spreadsheet analysis",
                "pdf": "Formatted reports suitable for printing or sharing"
            },
            "how_to": "Use the export buttons on the main dashboard"
        }
    },
    
    "user_management": {
        "registration": {
            "description": "Secure user registration with email verification",
            "requirements": [
                "Unique username",
                "Valid email address",
                "Strong password (8+ characters, mix of letters/numbers/symbols)"
            ],
            "verification": "Email verification required before full access"
        },
        
        "security": {
            "features": [
                "Password hashing and encryption",
                "Email verification system",
                "Password reset functionality",
                "Secure session management"
            ]
        },
        
        "data_privacy": {
            "description": "Each user has their own isolated database",
            "storage": "Individual SQLite databases per user (finances_username.db)",
            "isolation": "Complete data separation between users"
        }
    },
    
    "navigation": {
        "main_dashboard": "Primary view showing transactions, balance, and quick actions",
        "add_transaction": "Form to log new income or expenses",
        "budgeting_page": "Budget management and monitoring",
        "export_options": "Data export functionality",
        "chatbot": "AI assistant for financial guidance"
    },
    
    "common_questions": {
        "how_to_add_transaction": {
            "question": "How do I add a new transaction?",
            "answer": "Click 'Add Transaction' on the main dashboard, fill in the type (income/expense), category, amount, date, and description, then submit."
        },
        
        "how_to_set_budget": {
            "question": "How do I set up a budget?",
            "answer": "Go to the Budgeting page, enter spending limits for different categories like food, entertainment, or utilities, and save your budget."
        },
        
        "how_to_export_data": {
            "question": "How can I export my financial data?",
            "answer": "Use the export buttons on the main dashboard to download your data as CSV (for spreadsheets) or PDF (for reports)."
        },
        
        "how_to_track_savings": {
            "question": "How do I track my savings goals?",
            "answer": "Create savings goals with target amounts and due dates. The app will track your progress and show you how close you are to each goal."
        },
        
        "what_categories_available": {
            "question": "What spending categories are available?",
            "answer": "Categories include Food, Transportation, Entertainment, Utilities, Rent, Gifts, Healthcare, Education, and Shopping. You can also add custom descriptions."
        }
    },
    
    "troubleshooting": {
        "login_issues": {
            "email_not_verified": "Check your email for verification link or use 'Resend Verification'",
            "forgot_password": "Use 'Forgot Password' to reset via email",
            "account_locked": "Contact support if account access issues persist"
        },
        
        "data_issues": {
            "missing_transactions": "Ensure you're logged in and check if transaction was saved",
            "budget_not_updating": "Refresh the page or check if budget was properly saved",
            "export_failed": "Try again or contact support if persistent"
        }
    },
    
    "best_practices": {
        "tracking": [
            "Log transactions regularly (daily or weekly)",
            "Use consistent categories for better analysis",
            "Add descriptions for better record keeping"
        ],
        "budgeting": [
            "Start with realistic budget amounts",
            "Review and adjust budgets monthly",
            "Set aside money for unexpected expenses"
        ],
        "savings": [
            "Set specific, achievable savings goals",
            "Automate savings when possible",
            "Prioritize emergency fund before other goals"
        ]
    },
    
    "contact_support": {
        "description": "For technical issues or questions not covered by the chatbot",
        "methods": [
            "Use the Contact page on the website",
            "Check the FAQ section",
            "Email support directly"
        ]
    }
}

def get_site_info(category=None, subcategory=None):
    """Get specific information from the site reference"""
    if category is None:
        return SITE_REFERENCE
    
    if subcategory is None:
        return SITE_REFERENCE.get(category, {})
    
    return SITE_REFERENCE.get(category, {}).get(subcategory, {})

def search_site_reference(query):
    """Search the site reference for relevant information"""
    query_lower = query.lower()
    results = []
    
    for category, data in SITE_REFERENCE.items():
        if isinstance(data, dict):
            for subcategory, subdata in data.items():
                if isinstance(subdata, dict):
                    # Search in descriptions and other text fields
                    for key, value in subdata.items():
                        if isinstance(value, str) and query_lower in value.lower():
                            results.append({
                                'category': category,
                                'subcategory': subcategory,
                                'key': key,
                                'value': value
                            })
                        elif isinstance(value, list):
                            for item in value:
                                if isinstance(item, str) and query_lower in item.lower():
                                    results.append({
                                        'category': category,
                                        'subcategory': subcategory,
                                        'key': key,
                                        'value': item
                                    })
    
    return results 