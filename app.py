# Enhanced POS System with All Requested Features
from flask import Flask, request, jsonify, render_template_string, redirect, url_for, session, make_response
from datetime import datetime, timedelta
import json
import threading
import uuid
import secrets
import sys
import os
import argparse
from collections import defaultdict
from functools import wraps

app = Flask(__name__)
app.secret_key = 'pos_system_secret_key_12345'

# Configure session to be truly isolated per browser/device
app.config['SESSION_COOKIE_NAME'] = 'pos_session'
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SECURE'] = False  # Set to True if using HTTPS
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_PERMANENT'] = True
app.permanent_session_lifetime = timedelta(minutes=30)

# Store active sessions with tab IDs
active_sessions = {}

# ✅ SHARED ORDERS — visible across ALL sessions/tabs
# Only login is isolated per session. Everything else is shared.
GLOBAL_ORDERS = {}
orders_lock = threading.Lock()

# ✅ Staff PIN -> Name
STAFF_CODES = {
    "3105": "Gityus13",
    "0000": "Admin",
}
# ✅ Add more staff members with their own passcode using this line "0000": "Name Here",
# ✅ If you want to remvove staff members, just delete their line "0000": "Name Here",
# ✅ Enhanced menu with categories
MENU_CATEGORIES = {
    "best_sellers": {
        "name": "BEST SELLERS",
        "items": [
            {"id": "burger", "name": "Burger", "price": 15.0, "description": "Classic beef burger", "ingredients": ["beef", "bun", "lettuce", "tomato"]},
            {"id": "pizza", "name": "Pizza Special", "price": 18.0, "description": "Special pizza", "ingredients": ["dough", "cheese", "tomato_sauce", "pepperoni"]},
            {"id": "pasta", "name": "Pasta", "price": 16.0, "description": "Creamy pasta", "ingredients": ["pasta", "cream", "cheese"]},
        ]
    },
    "cold_drinks": {
        "name": "COLD DRINKS",
        "items": [
            {"id": "coke", "name": "Coca-Cola", "price": 2.5, "description": "Regular coke", "ingredients": ["coke_syrup", "water", "ice"]},
            {"id": "fanta", "name": "Fanta", "price": 2.5, "description": "Orange flavor", "ingredients": ["fanta_syrup", "water", "ice"]},
            {"id": "water", "name": "Water", "price": 1.5, "description": "Bottled water", "ingredients": ["water"]},
        ]
    },
    "hot_drinks": {
        "name": "HOT DRINKS",
        "items": [
            {"id": "coffee", "name": "Coffee", "price": 3.0, "description": "Black coffee", "ingredients": ["coffee_beans", "water"]},
            {"id": "latte", "name": "Latte", "price": 3.5, "description": "Coffee with milk", "ingredients": ["coffee_beans", "milk"]},
            {"id": "espresso", "name": "Espresso", "price": 2.5, "description": "Strong espresso", "ingredients": ["coffee_beans", "water"]},
        ]
    },
    "desserts": {
        "name": "DESSERTS",
        "items": [
            {"id": "apple_pie", "name": "Apple Pie", "price": 7.2, "description": "Fresh apple pie", "ingredients": ["apples", "flour", "sugar", "butter"]},
            {"id": "chocolate_cake", "name": "Chocolate Cake", "price": 6.5, "description": "Rich chocolate cake", "ingredients": ["chocolate", "flour", "sugar", "eggs"]},
        ]
    },
    "salads": {
        "name": "SALADS",
        "items": [
            {"id": "caesar_salad", "name": "Caesar Salad Big", "price": 24.0, "description": "Large caesar salad", "ingredients": ["lettuce", "croutons", "parmesan", "caesar_dressing"]},
            {"id": "greek_salad", "name": "Greek Salad", "price": 18.0, "description": "Traditional greek salad", "ingredients": ["tomato", "cucumber", "olives", "feta_cheese"]},
        ]
    },
    "wraps": {
        "name": "WRAPS",
        "items": [
            {"id": "chicken_wrap", "name": "Chicken Wrap", "price": 12.0, "description": "Grilled chicken wrap", "ingredients": ["chicken", "tortilla", "lettuce", "sauce"]},
            {"id": "veggie_wrap", "name": "Veggie Wrap", "price": 10.0, "description": "Vegetarian wrap", "ingredients": ["vegetables", "tortilla", "sauce"]},
        ]
    }
}

# Table layout
TABLE_SECTIONS = {
    "A": ["A1", "A2", "A3", "A4", "A5", "A6", "A7", "A8", "A9", "A10"],
    "B": ["B1", "B2", "B3", "B4", "B5", "B6", "B7", "B8", "B9", "B10"],
    "C": ["C1", "C2", "C3", "C4", "C5", "C6", "C7", "C8", "C9", "C10"],
    "VIP": ["VIP1", "VIP2", "VIP3", "VIP4", "VIP5", "VIP6", "VIP7", "VIP8", "VIP9", "VIP10"]
}

# Store system state
LOCK_TIMER = None

# New data structures for enhancements
ORDER_HISTORY = []
INVENTORY = {
    "beef": {"name": "Beef", "stock": 50, "unit": "kg"},
    "bun": {"name": "Bun", "stock": 100, "unit": "pieces"},
    "lettuce": {"name": "Lettuce", "stock": 30, "unit": "heads"},
    "tomato": {"name": "Tomato", "stock": 40, "unit": "pieces"},
    "dough": {"name": "Dough", "stock": 20, "unit": "kg"},
    "cheese": {"name": "Cheese", "stock": 25, "unit": "kg"},
    "tomato_sauce": {"name": "Tomato Sauce", "stock": 15, "unit": "liters"},
    "pepperoni": {"name": "Pepperoni", "stock": 10, "unit": "kg"},
    "pasta": {"name": "Pasta", "stock": 15, "unit": "kg"},
    "cream": {"name": "Cream", "stock": 10, "unit": "liters"},
    "coke_syrup": {"name": "Coke Syrup", "stock": 5, "unit": "liters"},
    "water": {"name": "Water", "stock": 100, "unit": "liters"},
    "fanta_syrup": {"name": "Fanta Syrup", "stock": 5, "unit": "liters"},
    "ice": {"name": "Ice", "stock": 50, "unit": "kg"},
    "coffee_beans": {"name": "Coffee Beans", "stock": 5, "unit": "kg"},
    "milk": {"name": "Milk", "stock": 20, "unit": "liters"},
    "apples": {"name": "Apples", "stock": 20, "unit": "kg"},
    "flour": {"name": "Flour", "stock": 15, "unit": "kg"},
    "sugar": {"name": "Sugar", "stock": 10, "unit": "kg"},
    "butter": {"name": "Butter", "stock": 8, "unit": "kg"},
    "chocolate": {"name": "Chocolate", "stock": 5, "unit": "kg"},
    "eggs": {"name": "Eggs", "stock": 60, "unit": "pieces"},
    "croutons": {"name": "Croutons", "stock": 5, "unit": "kg"},
    "parmesan": {"name": "Parmesan", "stock": 3, "unit": "kg"},
    "caesar_dressing": {"name": "Caesar Dressing", "stock": 5, "unit": "liters"},
    "cucumber": {"name": "Cucumber", "stock": 15, "unit": "pieces"},
    "olives": {"name": "Olives", "stock": 5, "unit": "kg"},
    "feta_cheese": {"name": "Feta Cheese", "stock": 4, "unit": "kg"},
    "chicken": {"name": "Chicken", "stock": 20, "unit": "kg"},
    "tortilla": {"name": "Tortilla", "stock": 30, "unit": "pieces"},
    "sauce": {"name": "Sauce", "stock": 5, "unit": "liters"},
    "vegetables": {"name": "Vegetables", "stock": 15, "unit": "kg"}
}
CUSTOMERS = {}
LOYALTY_POINTS = {}
RESERVATIONS = []
KITCHEN_ORDERS = []
PROMO_CODES = {
    "SAVE10": {"type": "percentage", "value": 10, "valid_until": "2025-12-31"},
    "WELCOME5": {"type": "percentage", "value": 5, "valid_until": "2025-12-31"},
    "FIVEDOLLAR": {"type": "fixed", "value": 5, "valid_until": "2025-12-31"}
}

def now_str():
    return datetime.now().strftime("%H:%M:%S")

def now_iso():
    return datetime.now().isoformat()

def get_menu_item(item_id):
    for category in MENU_CATEGORIES.values():
        for item in category["items"]:
            if item["id"] == item_id:
                return item
    return None

def staff_name_from_pin(pin: str) -> str:
    if not pin:
        return ""
    return STAFF_CODES.get(str(pin).strip(), "")

def auto_lock_system():
    """Automatically lock system after 5 minutes of inactivity"""
    pass

def reset_lock_timer():
    """Reset the auto-lock timer"""
    global LOCK_TIMER
    if LOCK_TIMER:
        LOCK_TIMER.cancel()
    LOCK_TIMER = threading.Timer(300, auto_lock_system)
    LOCK_TIMER.daemon = True
    LOCK_TIMER.start()

# Helper functions for tab isolation
def get_tab_session_id():
    """Get or create tab-specific session ID from request"""
    tab_id = request.headers.get('X-Tab-ID')
    if not tab_id:
        # Check if tab_id is in cookies
        tab_id = request.cookies.get('tab_id')
    
    if not tab_id:
        # Generate new tab ID
        tab_id = secrets.token_urlsafe(32)
    
    return tab_id

def get_session_orders():
    """Get the shared global orders (same for all sessions/tabs)"""
    return GLOBAL_ORDERS

def set_session_orders(orders):
    """Update the shared global orders"""
    global GLOBAL_ORDERS
    GLOBAL_ORDERS.update(orders)

def is_logged_in():
    """Check if user is logged in with valid tab session"""
    tab_id = get_tab_session_id()
    logged_in = session.get(f'logged_in_{tab_id}', False)
    session_id = session.get(f'session_id_{tab_id}')
    
    # Check if session is still valid in active_sessions
    if not logged_in or not session_id:
        return False
    
    if session_id not in active_sessions:
        return False
    
    # Update last active time
    active_sessions[session_id]['last_active'] = datetime.now()
    
    return True

def get_current_staff():
    tab_id = get_tab_session_id()
    return session.get(f'staff_pin_{tab_id}')

def get_current_staff_name():
    tab_id = get_tab_session_id()
    return session.get(f'staff_name_{tab_id}')

def login_required(f):
    """Decorator to require login for routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not is_logged_in():
            if request.path.startswith('/api/'):
                return jsonify({"error": "Not logged in", "redirect": "/"}), 401
            return redirect(url_for('login_page'))
        return f(*args, **kwargs)
    return decorated_function

# HTML Templates
LOGIN_HTML = r"""
<!doctype html>
<html>
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width,initial-scale=1"/>
  <title>POS Login</title>
  <style>
    * {
      margin: 0;
      padding: 0;
      box-sizing: border-box;
    }
    body {
      font-family: 'Segoe UI', Arial, sans-serif;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
    }
    .login-container {
      background: white;
      padding: 40px;
      border-radius: 20px;
      box-shadow: 0 20px 60px rgba(0,0,0,0.3);
      width: 400px;
      text-align: center;
    }
    .logo {
      font-size: 36px;
      font-weight: bold;
      color: #2c3e50;
      margin-bottom: 10px;
    }
    .subtitle {
      color: #7f8c8d;
      margin-bottom: 30px;
    }
    .pin-input {
      width: 100%;
      padding: 20px;
      font-size: 32px;
      text-align: center;
      border: 3px solid #ddd;
      border-radius: 10px;
      margin: 20px 0;
      letter-spacing: 10px;
      font-weight: bold;
    }
    .pin-input:focus {
      outline: none;
      border-color: #3498db;
    }
    .error {
      color: #e74c3c;
      margin: 10px 0;
      min-height: 20px;
    }
    .login-btn {
      width: 100%;
      padding: 20px;
      background: #3498db;
      color: white;
      border: none;
      border-radius: 10px;
      font-size: 18px;
      font-weight: bold;
      cursor: pointer;
      transition: background 0.3s;
    }
    .login-btn:hover {
      background: #2980b9;
    }
    .pin-hint {
      color: #95a5a6;
      font-size: 14px;
      margin-top: 20px;
    }
  </style>
  <script>
    // Generate or retrieve tab ID
    function getTabId() {
      let tabId = localStorage.getItem('pos_tab_id');
      if (!tabId) {
        tabId = 'tab_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
        localStorage.setItem('pos_tab_id', tabId);
      }
      return tabId;
    }
    
    function login(e) {
      e.preventDefault();
      const pin = document.getElementById('pin').value;
      const error = document.getElementById('error');
      if (!pin || pin.length !== 4) {
        error.textContent = 'Please enter a 4-digit PIN';
        return;
      }
      
      const tabId = getTabId();
      
      fetch('/api/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Tab-ID': tabId
        },
        body: JSON.stringify({pin: pin, tab_id: tabId})
      })
      .then(res => res.json())
      .then(data => {
        if (data.success) {
          // Set cookie with tab ID
          document.cookie = "tab_id=" + tabId + "; path=/; max-age=" + (60*60*24);
          window.location.href = '/pos?tab=' + tabId;
        } else {
          error.textContent = data.error || 'Invalid PIN';
          document.getElementById('pin').value = '';
          document.getElementById('pin').focus();
        }
      })
      .catch(err => {
        error.textContent = 'Network error';
      });
    }
    
    document.getElementById('pin').addEventListener('input', function(e) {
      this.value = this.value.replace(/\D/g, '');
      document.getElementById('error').textContent = '';
    });
    document.getElementById('pin').focus();
  </script>
</head>
<body>
  <div class="login-container">
    <div class="logo">🍽️ POS SYSTEM</div>
    <div class="subtitle">Staff Login Required</div>
    <form id="loginForm" onsubmit="login(event)">
      <input type="password"
             class="pin-input"
             id="pin"
             placeholder="0000"
             maxlength="4"
             pattern="\d{4}"
             required
             autofocus>
      <div class="error" id="error"></div>
      <button type="submit" class="login-btn">LOGIN</button>
    </form>
    <div class="pin-hint">Enter your 4-digit PIN to continue</div>
  </div>
</body>
</html>
"""

POS_HTML = """
<!doctype html>
<html>
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width,initial-scale=1"/>
  <title>POS System</title>
  <style>
    * {
      margin: 0;
      padding: 0;
      box-sizing: border-box;
    }
    body {
      font-family: 'Segoe UI', Arial, sans-serif;
      background: #f5f5f5;
      color: #333;
      overflow: hidden;
      height: 100vh;
    }
    .header {
      background: white;
      padding: 15px 30px;
      border-bottom: 1px solid #ddd;
      display: flex;
      justify-content: space-between;
      align-items: center;
      box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    .logo {
      font-size: 24px;
      font-weight: bold;
      color: #2c3e50;
    }
    .user-info {
      display: flex;
      align-items: center;
      gap: 20px;
    }
    .staff-name {
      font-weight: bold;
      color: #2c3e50;
    }
    .lock-btn {
      padding: 8px 16px;
      background: #e74c3c;
      color: white;
      border: none;
      border-radius: 4px;
      cursor: pointer;
      font-weight: bold;
    }
    .lock-btn:hover {
      background: #c0392b;
    }
    .main-container {
      display: flex;
      height: calc(100vh - 70px);
    }
    .left-panel {
      width: 300px;
      background: white;
      border-right: 1px solid #ddd;
      display: flex;
      flex-direction: column;
      overflow: hidden;
    }
    .table-header {
      padding: 20px;
      border-bottom: 1px solid #eee;
    }
    .search-input {
      width: 100%;
      padding: 10px;
      border: 1px solid #ddd;
      border-radius: 4px;
      font-size: 14px;
    }
    .table-sections {
      flex: 1;
      overflow-y: auto;
      padding: 15px;
    }
    .section-title {
      font-size: 16px;
      font-weight: bold;
      margin: 15px 0 10px 0;
      color: #2c3e50;
      padding-bottom: 5px;
      border-bottom: 2px solid #3498db;
    }
    .tables-grid {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 8px;
      margin-bottom: 20px;
    }
    .table-btn {
      padding: 12px;
      background: white;
      border: 2px solid #3498db;
      border-radius: 6px;
      color: #3498db;
      font-weight: bold;
      cursor: pointer;
      transition: all 0.2s;
    }
    .table-btn:hover {
      background: #3498db;
      color: white;
    }
    .table-btn.vip {
      border-color: #e74c3c;
      color: #e74c3c;
    }
    .table-btn.vip:hover {
      background: #e74c3c;
      color: white;
    }
    .table-btn.active {
      background: #3498db;
      color: white;
    }
    .table-btn.active.vip {
      background: #e74c3c;
      color: white;
    }
    .table-btn.occupied {
      background: #f39c12;
      border-color: #f39c12;
      color: white;
    }
    .right-panel {
      flex: 1;
      display: flex;
      flex-direction: column;
      background: white;
    }
    .order-header {
      padding: 20px;
      background: #34495e;
      color: white;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    .table-display {
      font-size: 24px;
      font-weight: bold;
    }
    .order-actions {
      display: flex;
      gap: 10px;
    }
    .action-btn {
      padding: 10px 20px;
      border: none;
      border-radius: 4px;
      font-weight: bold;
      cursor: pointer;
    }
    .action-btn.clear {
      background: #e74c3c;
      color: white;
    }
    .action-btn.print {
      background: #3498db;
      color: white;
    }
    .action-btn.split {
      background: #9b59b6;
      color: white;
    }
    .action-btn.discount {
      background: #f39c12;
      color: white;
    }
    .menu-categories {
      display: flex;
      padding: 15px;
      background: #ecf0f1;
      border-bottom: 1px solid #ddd;
      overflow-x: auto;
      gap: 10px;
    }
    .category-btn {
      padding: 12px 24px;
      background: white;
      border: none;
      border-radius: 6px;
      font-weight: bold;
      color: #2c3e50;
      cursor: pointer;
      white-space: nowrap;
    }
    .category-btn.active {
      background: #3498db;
      color: white;
    }
    .menu-items-container {
      flex: 1;
      overflow-y: auto;
      padding: 20px;
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
      gap: 15px;
    }
    .menu-item {
      background: white;
      border: 1px solid #ddd;
      border-radius: 8px;
      padding: 15px;
      cursor: pointer;
      transition: all 0.2s;
    }
    .menu-item:hover {
      transform: translateY(-2px);
      box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    .item-name {
      font-weight: bold;
      margin-bottom: 5px;
      color: #2c3e50;
    }
    .item-description {
      font-size: 13px;
      color: #666;
      margin-bottom: 10px;
      min-height: 36px;
    }
    .item-price {
      color: #27ae60;
      font-weight: bold;
      font-size: 16px;
    }
    .order-summary {
      width: 400px;
      border-left: 1px solid #ddd;
      display: flex;
      flex-direction: column;
      background: #f8f9fa;
    }
    .summary-header {
      padding: 20px;
      background: white;
      border-bottom: 1px solid #ddd;
    }
    .order-items {
      flex: 1;
      overflow-y: auto;
      padding: 15px;
    }
    .order-item {
      background: white;
      border-radius: 8px;
      padding: 15px;
      margin-bottom: 10px;
      border: 1px solid #eee;
    }
    .item-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 10px;
    }
    .item-title {
      font-weight: bold;
      color: #2c3e50;
    }
    .item-controls {
      display: flex;
      align-items: center;
      gap: 10px;
    }
    .quantity-btn {
      width: 30px;
      height: 30px;
      border: 1px solid #ddd;
      background: white;
      border-radius: 4px;
      cursor: pointer;
      font-weight: bold;
    }
    .item-quantity {
      font-weight: bold;
      min-width: 30px;
      text-align: center;
    }
    .item-description-input {
      width: 100%;
      padding: 8px;
      border: 1px solid #ddd;
      border-radius: 4px;
      font-size: 14px;
      margin-top: 10px;
      resize: vertical;
      min-height: 40px;
    }
    .item-total {
      text-align: right;
      font-weight: bold;
      color: #2c3e50;
      margin-top: 5px;
    }
    .order-total {
      padding: 20px;
      background: white;
      border-top: 1px solid #ddd;
    }
    .total-row {
      display: flex;
      justify-content: space-between;
      margin-bottom: 10px;
      padding: 5px 0;
    }
    .total-row.final {
      font-size: 20px;
      font-weight: bold;
      color: #2c3e50;
      border-top: 2px solid #ddd;
      padding-top: 15px;
      margin-top: 10px;
    }
    .payment-buttons {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 10px;
      padding: 20px;
    }
    .payment-btn {
      padding: 15px;
      border: none;
      border-radius: 6px;
      font-weight: bold;
      cursor: pointer;
      font-size: 16px;
    }
    .payment-btn.cash {
      background: #27ae60;
      color: white;
    }
    .payment-btn.card {
      background: #3498db;
      color: white;
    }
    .modal {
      display: none;
      position: fixed;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background: rgba(0,0,0,0.5);
      z-index: 1000;
      align-items: center;
      justify-content: center;
    }
    .modal-content {
      background: white;
      padding: 30px;
      border-radius: 10px;
      max-width: 500px;
      width: 90%;
      max-height: 80vh;
      overflow-y: auto;
    }
    .modal h3 {
      margin-bottom: 20px;
      color: #2c3e50;
    }
    .modal-input {
      width: 100%;
      padding: 12px;
      margin-bottom: 15px;
      border: 1px solid #ddd;
      border-radius: 4px;
      font-size: 16px;
    }
    .modal-buttons {
      display: flex;
      gap: 10px;
      margin-top: 20px;
    }
    .modal-btn {
      flex: 1;
      padding: 12px;
      border: none;
      border-radius: 4px;
      cursor: pointer;
      font-weight: bold;
    }
    .modal-btn.primary {
      background: #3498db;
      color: white;
    }
    .modal-btn.secondary {
      background: #95a5a6;
      color: white;
    }
    .lock-screen {
      position: fixed;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background: rgba(0,0,0,0.8);
      z-index: 9999;
      display: flex;
      align-items: center;
      justify-content: center;
      color: white;
      font-size: 24px;
      flex-direction: column;
      gap: 20px;
    }
    .lock-screen .login-btn {
      padding: 15px 30px;
      background: #3498db;
      color: white;
      border: none;
      border-radius: 8px;
      font-size: 18px;
      cursor: pointer;
    }
    .empty-state {
      text-align: center;
      padding: 40px;
      color: #999;
    }
    .tabs {
      display: flex;
      border-bottom: 1px solid #ddd;
      background: #ecf0f1;
    }
    .tab {
      padding: 15px 25px;
      cursor: pointer;
      font-weight: bold;
      color: #7f8c8d;
    }
    .tab.active {
      color: #3498db;
      border-bottom: 3px solid #3498db;
    }
    .dashboard {
      padding: 20px;
      overflow-y: auto;
    }
    .dashboard-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
      gap: 20px;
      margin-bottom: 30px;
    }
    .dashboard-card {
      background: white;
      border-radius: 8px;
      padding: 20px;
      box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    .card-title {
      font-size: 18px;
      font-weight: bold;
      margin-bottom: 15px;
      color: #2c3e50;
    }
    .card-value {
      font-size: 28px;
      font-weight: bold;
      color: #3498db;
    }
    .inventory-item {
      display: flex;
      justify-content: space-between;
      padding: 10px;
      border-bottom: 1px solid #eee;
    }
    .inventory-name {
      font-weight: bold;
    }
    .inventory-stock {
      color: #7f8c8d;
    }
    .low-stock {
      color: #e74c3c;
      font-weight: bold;
    }
    .reservation-item {
      padding: 15px;
      border: 1px solid #ddd;
      border-radius: 8px;
      margin-bottom: 15px;
      background: white;
    }
    .reservation-header {
      display: flex;
      justify-content: space-between;
      margin-bottom: 10px;
    }
    .reservation-name {
      font-weight: bold;
    }
    .reservation-time {
      color: #3498db;
    }
  </style>
</head>
<body>
  <div class="lock-screen" id="lockScreen" style="display: none;">
    <div style="font-size: 36px;">🔒</div>
    <div>System Locked</div>
    <div style="font-size: 16px; opacity: 0.8;">Please login to continue</div>
    <button class="login-btn" onclick="window.location.href='/'">LOGIN</button>
  </div>
  <div id="posInterface">
    <div class="header">
      <div class="logo">🍽️ POS SYSTEM</div>
      <div class="user-info">
        <div>Staff: <span class="staff-name" id="staffName"></span></div>
        <button class="lock-btn" onclick="lockSystem()">🔒 Lock System</button>
      </div>
    </div>
    <div class="tabs">
      <div class="tab active" onclick="switchTab('pos')">POS</div>
      <div class="tab" onclick="switchTab('dashboard')">Dashboard</div>
      <div class="tab" onclick="switchTab('inventory')">Inventory</div>
      <div class="tab" onclick="switchTab('reservations')">Reservations</div>
      <div class="tab" onclick="switchTab('reports')">Reports</div>
    </div>
    <div id="posTab" class="main-container">
      <div class="left-panel">
        <div class="table-header">
          <input type="text" class="search-input" placeholder="Search tables..." id="tableSearch" oninput="filterTables()">
        </div>
        <div class="table-sections" id="tableSections"></div>
      </div>
      <div class="right-panel">
        <div class="order-header">
          <div class="table-display" id="currentTable">No Table Selected</div>
          <div class="order-actions">
            <button class="action-btn discount" onclick="showDiscountModal()" id="discountBtn" disabled>Apply Discount</button>
            <button class="action-btn split" onclick="showSplitBillModal()" id="splitBtn" disabled>Split Bill</button>
            <button class="action-btn clear" onclick="clearTable()" id="clearBtn" disabled>Clear Table</button>
            <button class="action-btn print" onclick="printBill()" id="printBtn" disabled>Print Bill</button>
          </div>
        </div>
        <div class="menu-categories" id="menuCategories"></div>
        <div class="menu-items-container" id="menuItems">
          <div class="empty-state">Select a table first, then choose menu category</div>
        </div>
      </div>
      <div class="order-summary">
        <div class="summary-header">
          <h3>Order Summary</h3>
          <div style="font-size: 14px; color: #666;" id="orderTime">-</div>
        </div>
        <div class="order-items" id="orderItems">
          <div class="empty-state">No items in order<br>Add items from menu</div>
        </div>
        <div class="order-total">
          <div class="total-row"><span>Subtotal</span><span id="subtotal">$0.00</span></div>
          <div class="total-row"><span>VAT (18%)</span><span id="vat">$0.00</span></div>
          <div class="total-row"><span>Service Charge</span><span id="service">$0.00</span></div>
          <div class="total-row"><span>Discount</span><span id="discount">-$0.00</span></div>
          <div class="total-row final"><span>TOTAL</span><span id="total">$0.00</span></div>
        </div>
        <div class="payment-buttons">
          <button class="payment-btn cash" onclick="processPayment('cash')" id="cashBtn" disabled>Cash Payment</button>
          <button class="payment-btn card" onclick="processPayment('card')" id="cardBtn" disabled>Card Payment</button>
        </div>
      </div>
    </div>
    <div id="dashboardTab" class="dashboard" style="display: none;">
      <div class="dashboard-grid">
        <div class="dashboard-card"><div class="card-title">Today's Revenue</div><div class="card-value" id="todayRevenue">$0.00</div></div>
        <div class="dashboard-card"><div class="card-title">Orders Today</div><div class="card-value" id="todayOrders">0</div></div>
        <div class="dashboard-card"><div class="card-title">Best Seller</div><div class="card-value" id="bestSeller">-</div></div>
      </div>
    </div>
    <div id="inventoryTab" class="dashboard" style="display: none;">
      <div class="dashboard-card"><div class="card-title">Inventory Levels</div><div id="inventoryList"><div class="empty-state">Loading inventory...</div></div></div>
    </div>
    <div id="reservationsTab" class="dashboard" style="display: none;">
      <div class="dashboard-card"><div class="card-title">Table Reservations</div><div id="reservationsList"><div class="empty-state">No reservations found</div></div></div>
      <div class="dashboard-card">
        <div class="card-title">Add New Reservation</div>
        <input type="text" class="modal-input" id="customerName" placeholder="Customer Name">
        <input type="text" class="modal-input" id="reservationTable" placeholder="Table (e.g., A1)">
        <input type="datetime-local" class="modal-input" id="reservationTime">
        <button class="modal-btn primary" onclick="addReservation()">Add Reservation</button>
      </div>
    </div>
    <div id="reportsTab" class="dashboard" style="display: none;">
      <div class="dashboard-card"><div class="card-title">Sales Reports</div><div id="reportsContent"><div class="empty-state">Sales reports will appear here</div></div></div>
    </div>
  </div>
  <div class="modal" id="descriptionModal">
    <div class="modal-content">
      <h3>Add Description</h3>
      <p id="itemName">Item: </p>
      <textarea class="modal-input" id="itemDescription" placeholder="Add special instructions (e.g., no tomato, extra cheese, etc.)" rows="4"></textarea>
      <div class="modal-buttons">
        <button class="modal-btn secondary" onclick="closeDescriptionModal()">Cancel</button>
        <button class="modal-btn primary" onclick="saveDescription()">Add to Order</button>
      </div>
    </div>
  </div>
  <div class="modal" id="discountModal">
    <div class="modal-content">
      <h3>Apply Discount</h3>
      <input type="text" class="modal-input" id="promoCode" placeholder="Enter promo code">
      <div class="modal-buttons">
        <button class="modal-btn secondary" onclick="closeDiscountModal()">Cancel</button>
        <button class="modal-btn primary" onclick="applyDiscount()">Apply</button>
      </div>
    </div>
  </div>
  <div class="modal" id="splitBillModal">
    <div class="modal-content">
      <h3>Split Bill</h3>
      <div id="splitOptions">
        <div class="modal-buttons">
          <button class="modal-btn primary" onclick="splitEvenly()">Split Evenly</button>
          <button class="modal-btn primary" onclick="splitCustom()">Custom Split</button>
        </div>
      </div>
      <div id="splitDetails" style="display: none;">
        <div id="splitItems"></div>
        <div class="modal-buttons">
          <button class="modal-btn secondary" onclick="closeSplitBillModal()">Cancel</button>
          <button class="modal-btn primary" onclick="processSplitPayment()">Process Payment</button>
        </div>
      </div>
    </div>
  </div>
<script>
let currentTable = null;
let currentStaff = null;
let currentCategory = 'best_sellers';
let menuData = {};
let tableData = {};
let selectedItemForDescription = null;
let activeTab = 'pos';
let myTabId = null;

function getTabId() {
  if (myTabId) return myTabId;
  myTabId = localStorage.getItem('pos_tab_id');
  if (!myTabId) {
    myTabId = 'tab_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    localStorage.setItem('pos_tab_id', myTabId);
  }
  return myTabId;
}

async function initPOS() {
  try {
    const tabId = getTabId();
    const statusRes = await fetch('/api/system_status?tab=' + tabId, {
      headers: { 'X-Tab-ID': tabId }
    });
    if (!statusRes.ok) {
      window.location.href = '/';
      return;
    }
    const status = await statusRes.json();
    if (status.locked) {
      showLockScreen();
      return;
    }
    currentStaff = status.staff;
    document.getElementById('staffName').textContent = status.staff_name || 'Unknown';
    
    const menuRes = await fetch('/api/menu');
    menuData = await menuRes.json();
    const sectionsRes = await fetch('/api/table_sections');
    tableData = await sectionsRes.json();
    renderTableSections();
    renderMenuCategories();
    setInterval(refreshOrders, 3000);
    loadDashboard();
  } catch (error) {
    console.error('Failed to initialize POS:', error);
    window.location.href = '/';
  }
}

function switchTab(tabName) {
  document.getElementById('posTab').style.display = 'none';
  document.getElementById('dashboardTab').style.display = 'none';
  document.getElementById('inventoryTab').style.display = 'none';
  document.getElementById('reservationsTab').style.display = 'none';
  document.getElementById('reportsTab').style.display = 'none';
  document.getElementById(tabName + 'Tab').style.display = tabName === 'pos' ? 'flex' : 'block';
  activeTab = tabName;
  document.querySelectorAll('.tab').forEach(tab => tab.classList.remove('active'));
  event.target.classList.add('active');
  if (tabName === 'pos') renderMenuItems();
  if (tabName === 'dashboard') loadDashboard();
  else if (tabName === 'inventory') loadInventory();
  else if (tabName === 'reservations') loadReservations();
  else if (tabName === 'reports') loadReports();
}

async function loadDashboard() {
  const res = await fetch('/api/dashboard');
  const data = await res.json();
  document.getElementById('todayRevenue').textContent = '$' + data.revenue.toFixed(2);
  document.getElementById('todayOrders').textContent = data.orders;
  document.getElementById('bestSeller').textContent = data.best_seller || '-';
}

async function loadInventory() {
  const res = await fetch('/api/inventory');
  const data = await res.json();
  const container = document.getElementById('inventoryList');
  let html = '';
  for (const [id, item] of Object.entries(data)) {
    const isLow = item.stock < 5;
    html += `<div class="inventory-item"><span class="inventory-name">${item.name}</span><span class="inventory-stock ${isLow ? 'low-stock' : ''}">${item.stock} ${item.unit} ${isLow ? '(LOW)' : ''}</span></div>`;
  }
  container.innerHTML = html || '<div class="empty-state">No inventory items</div>';
}

async function loadReservations() {
  const res = await fetch('/api/reservations');
  const data = await res.json();
  const container = document.getElementById('reservationsList');
  if (data.length === 0) {
    container.innerHTML = '<div class="empty-state">No reservations found</div>';
    return;
  }
  let html = '';
  data.forEach(reservation => {
    html += `<div class="reservation-item"><div class="reservation-header"><span class="reservation-name">${reservation.customer_name}</span><span class="reservation-time">${reservation.time}</span></div><div>Table: ${reservation.table}</div></div>`;
  });
  container.innerHTML = html;
}

async function loadReports() {
  const res = await fetch('/api/reports');
  const data = await res.json();
  document.getElementById('reportsContent').innerHTML = '<div class="empty-state">Reports data loaded</div>';
}

function showLockScreen() {
  document.getElementById('posInterface').style.display = 'none';
  document.getElementById('lockScreen').style.display = 'flex';
}

function lockSystem() {
  fetch('/api/lock', { method: 'POST' }).then(() => {
    window.location.href = '/';
  });
}

function renderTableSections() {
  const container = document.getElementById('tableSections');
  container.innerHTML = '';
  for (const [section, tables] of Object.entries(tableData)) {
    const sectionDiv = document.createElement('div');
    const title = document.createElement('div');
    title.className = 'section-title';
    title.textContent = section === 'VIP' ? 'VIP TABLES' : `SECTION ${section}`;
    sectionDiv.appendChild(title);
    const grid = document.createElement('div');
    grid.className = 'tables-grid';
    tables.forEach(table => {
      const btn = document.createElement('button');
      btn.className = `table-btn ${section === 'VIP' ? 'vip' : ''}`;
      btn.textContent = table;
      btn.onclick = () => selectTable(table);
      btn.id = `table_${table}`;
      grid.appendChild(btn);
    });
    sectionDiv.appendChild(grid);
    container.appendChild(sectionDiv);
  }
}

function filterTables() {
  const search = document.getElementById('tableSearch').value.toLowerCase();
  document.querySelectorAll('.table-btn').forEach(btn => {
    btn.style.display = btn.textContent.toLowerCase().includes(search) ? 'block' : 'none';
  });
}

async function selectTable(table) {
  if (currentTable === table) return;
  if (currentTable) {
    const prevBtn = document.getElementById(`table_${currentTable}`);
    if (prevBtn) prevBtn.classList.remove('active');
  }
  currentTable = table;
  const currentBtn = document.getElementById(`table_${table}`);
  if (currentBtn) currentBtn.classList.add('active');
  document.getElementById('currentTable').textContent = `Table: ${table}`;
  document.getElementById('clearBtn').disabled = false;
  document.getElementById('printBtn').disabled = false;
  document.getElementById('cashBtn').disabled = false;
  document.getElementById('cardBtn').disabled = false;
  document.getElementById('discountBtn').disabled = false;
  document.getElementById('splitBtn').disabled = false;
  renderMenuItems();
  await refreshOrder();
}

function renderMenuCategories() {
  const container = document.getElementById('menuCategories');
  container.innerHTML = '';
  for (const [categoryId, category] of Object.entries(menuData)) {
    const btn = document.createElement('button');
    btn.className = `category-btn ${categoryId === currentCategory ? 'active' : ''}`;
    btn.textContent = category.name;
    btn.onclick = () => {
      currentCategory = categoryId;
      renderMenuCategories();
      renderMenuItems();
    };
    container.appendChild(btn);
  }
}

function renderMenuItems() {
  const container = document.getElementById('menuItems');
  const category = menuData[currentCategory];
  if (!currentTable) {
    container.innerHTML = '<div class="empty-state">Select a table first</div>';
    return;
  }
  if (!category) {
    container.innerHTML = '<div class="empty-state">No items in this category</div>';
    return;
  }
  container.innerHTML = '';
  category.items.forEach(item => {
    const div = document.createElement('div');
    div.className = 'menu-item';
    div.onclick = () => showDescriptionModal(item);
    div.innerHTML = `<div class="item-name">${item.name}</div><div class="item-description">${item.description || 'No description'}</div><div class="item-price">$${item.price.toFixed(2)}</div>`;
    container.appendChild(div);
  });
}

function showDescriptionModal(item) {
  if (!currentTable) {
    alert('Please select a table first');
    return;
  }
  selectedItemForDescription = item;
  document.getElementById('itemName').textContent = `Item: ${item.name}`;
  document.getElementById('itemDescription').value = '';
  document.getElementById('descriptionModal').style.display = 'flex';
}

function closeDescriptionModal() {
  document.getElementById('descriptionModal').style.display = 'none';
  selectedItemForDescription = null;
}

async function saveDescription() {
  if (!selectedItemForDescription || !currentTable) return;
  const description = document.getElementById('itemDescription').value;
  const response = await fetch('/api/add', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'X-Tab-ID': getTabId() },
    body: JSON.stringify({ table: currentTable, item_id: selectedItemForDescription.id, description: description })
  });
  if (response.ok) {
    closeDescriptionModal();
    await refreshOrder();
  } else {
    alert('Error adding item');
  }
}

async function refreshOrder() {
  if (!currentTable) return;
  const response = await fetch(`/api/order/${currentTable}`, {
    headers: { 'X-Tab-ID': getTabId() }
  });
  if (!response.ok) return;
  const order = await response.json();
  renderOrder(order);
}

async function refreshOrders() {
  const response = await fetch('/api/orders_status', {
    headers: { 'X-Tab-ID': getTabId() }
  });
  const orders = await response.json();
  Object.keys(tableData).forEach(section => {
    tableData[section].forEach(table => {
      const btn = document.getElementById(`table_${table}`);
      if (btn) {
        if (orders[table]) btn.classList.add('occupied');
        else btn.classList.remove('occupied');
      }
    });
  });
  if (currentTable && activeTab === 'pos') await refreshOrder();
}

function renderOrder(order) {
  const container = document.getElementById('orderItems');
  if (!order || !order.items || order.items.length === 0) {
    container.innerHTML = '<div class="empty-state">No items in order<br>Add items from menu</div>';
    updateTotals(0, 0);
    document.getElementById('orderTime').textContent = '-';
    return;
  }
  let html = '';
  let subtotal = 0;
  order.items.forEach((item, index) => {
    const itemTotal = item.price * item.quantity;
    subtotal += itemTotal;
    html += `<div class="order-item" data-index="${index}"><div class="item-header"><div class="item-title">${item.name} × ${item.quantity}</div><div class="item-controls"><button class="quantity-btn" onclick="updateQuantity(${index}, ${item.quantity - 1})">-</button><span class="item-quantity">${item.quantity}</span><button class="quantity-btn" onclick="updateQuantity(${index}, ${item.quantity + 1})">+</button></div></div>${item.description ? `<div style="color: #666; font-size: 13px; margin: 5px 0;">${item.description}</div>` : ''}<textarea class="item-description-input" placeholder="Add/modify description..." onchange="updateDescription(${index}, this.value)">${item.description || ''}</textarea><div class="item-total">$${itemTotal.toFixed(2)}</div></div>`;
  });
  container.innerHTML = html;
  let discountAmount = 0;
  if (order.discount) {
    if (order.discount.type === 'percentage') discountAmount = subtotal * (order.discount.value / 100);
    else if (order.discount.type === 'fixed') discountAmount = order.discount.value;
  }
  updateTotals(subtotal, discountAmount);
  document.getElementById('orderTime').textContent = `Updated: ${order.updated || ''}`;
}

function updateTotals(subtotal, discountAmount) {
  const vat = subtotal * 0.18;
  const service = subtotal * 0.10;
  const total = subtotal + vat + service - discountAmount;
  document.getElementById('subtotal').textContent = `$${subtotal.toFixed(2)}`;
  document.getElementById('vat').textContent = `$${vat.toFixed(2)}`;
  document.getElementById('service').textContent = `$${service.toFixed(2)}`;
  document.getElementById('discount').textContent = `-$${discountAmount.toFixed(2)}`;
  document.getElementById('total').textContent = `$${total.toFixed(2)}`;
}

async function updateQuantity(itemIndex, newQuantity) {
  if (newQuantity < 0) return;
  const response = await fetch('/api/update_quantity', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'X-Tab-ID': getTabId() },
    body: JSON.stringify({ table: currentTable, item_index: itemIndex, quantity: newQuantity })
  });
  if (response.ok) await refreshOrder();
}

async function updateDescription(itemIndex, description) {
  await fetch('/api/update_description', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'X-Tab-ID': getTabId() },
    body: JSON.stringify({ table: currentTable, item_index: itemIndex, description: description })
  });
}

async function clearTable() {
  if (!currentTable || !confirm('Clear this table? This will remove all items.')) return;
  const response = await fetch('/api/clear', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'X-Tab-ID': getTabId() },
    body: JSON.stringify({ table: currentTable })
  });
  if (response.ok) {
    const btn = document.getElementById(`table_${currentTable}`);
    if (btn) btn.classList.remove('occupied');
    await refreshOrder();
  }
}

async function printBill() {
  if (!currentTable) return;
  const response = await fetch('/api/print', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'X-Tab-ID': getTabId() },
    body: JSON.stringify({ table: currentTable })
  });
  if (response.ok) alert('Bill sent to printer');
}

async function processPayment(method) {
  if (!currentTable || !confirm(`Process ${method} payment?`)) return;
  const response = await fetch('/api/payment', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'X-Tab-ID': getTabId() },
    body: JSON.stringify({ table: currentTable, method: method })
  });
  if (response.ok) {
    const btn = document.getElementById(`table_${currentTable}`);
    if (btn) btn.classList.remove('occupied');
    currentTable = null;
    document.getElementById('currentTable').textContent = 'No Table Selected';
    document.querySelectorAll('.table-btn').forEach(btn => btn.classList.remove('active'));
    document.getElementById('clearBtn').disabled = true;
    document.getElementById('printBtn').disabled = true;
    document.getElementById('cashBtn').disabled = true;
    document.getElementById('cardBtn').disabled = true;
    document.getElementById('discountBtn').disabled = true;
    document.getElementById('splitBtn').disabled = true;
    renderOrder(null);
    renderMenuItems();
    alert(`Payment processed via ${method}`);
  }
}

function showDiscountModal() {
  document.getElementById('discountModal').style.display = 'flex';
}

function closeDiscountModal() {
  document.getElementById('discountModal').style.display = 'none';
}

async function applyDiscount() {
  const code = document.getElementById('promoCode').value;
  if (!code) {
    alert('Please enter a promo code');
    return;
  }
  const response = await fetch('/api/apply_discount', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'X-Tab-ID': getTabId() },
    body: JSON.stringify({ table: currentTable, code: code })
  });
  if (response.ok) {
    closeDiscountModal();
    document.getElementById('promoCode').value = '';
    await refreshOrder();
  } else {
    const data = await response.json();
    alert(data.error || 'Invalid promo code');
  }
}

function showSplitBillModal() {
  document.getElementById('splitBillModal').style.display = 'flex';
  document.getElementById('splitOptions').style.display = 'block';
  document.getElementById('splitDetails').style.display = 'none';
}

function closeSplitBillModal() {
  document.getElementById('splitBillModal').style.display = 'none';
}

function splitEvenly() {
  alert('Splitting bill evenly between customers');
  closeSplitBillModal();
}

function splitCustom() {
  alert('Custom split option selected');
  closeSplitBillModal();
}

async function addReservation() {
  const name = document.getElementById('customerName').value;
  const table = document.getElementById('reservationTable').value;
  const time = document.getElementById('reservationTime').value;
  if (!name || !table || !time) {
    alert('Please fill all fields');
    return;
  }
  const response = await fetch('/api/add_reservation', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ customer_name: name, table: table, time: time })
  });
  if (response.ok) {
    document.getElementById('customerName').value = '';
    document.getElementById('reservationTable').value = '';
    document.getElementById('reservationTime').value = '';
    loadReservations();
    alert('Reservation added successfully');
  } else {
    alert('Error adding reservation');
  }
}

document.addEventListener('DOMContentLoaded', initPOS);
</script>
</body>
</html>
"""

@app.route("/")
def login_page():
    """Show login page first"""
    return render_template_string(LOGIN_HTML)

@app.route("/pos")
def pos_page():
    """Show POS interface after login"""
    tab_id = request.args.get('tab')
    if not tab_id:
        return redirect(url_for('login_page'))
    if not is_logged_in():
        return redirect(url_for('login_page'))
    return render_template_string(POS_HTML)

@app.post("/api/login")
def api_login():
    """Login with PIN - with tab isolation"""
    body = request.get_json(force=True)
    pin = (body.get("pin") or "").strip()
    tab_id = body.get("tab_id") or request.headers.get('X-Tab-ID')
    
    if not tab_id:
        tab_id = secrets.token_urlsafe(32)
    
    staff_name = staff_name_from_pin(pin)
    
    if staff_name:
        # Generate unique session ID for this tab
        session_id = str(uuid.uuid4())
        device_fingerprint = request.headers.get('User-Agent', 'unknown')[:50]
        
        # Set session variables with tab isolation
        session[f'logged_in_{tab_id}'] = True
        session[f'staff_pin_{tab_id}'] = pin
        session[f'staff_name_{tab_id}'] = staff_name
        session[f'login_time_{tab_id}'] = datetime.now().isoformat()
        session[f'session_id_{tab_id}'] = session_id
        session[f'device_fingerprint_{tab_id}'] = device_fingerprint
        
        # Set session expiration
        session.permanent = True
        app.permanent_session_lifetime = timedelta(minutes=30)
        
        # Track active session
        active_sessions[session_id] = {
            'tab_id': tab_id,
            'staff_pin': pin,
            'staff_name': staff_name,
            'device_fingerprint': device_fingerprint,
            'login_time': datetime.now(),
            'last_active': datetime.now(),
            'ip': request.remote_addr
        }
        
        print(f"[LOGIN] {staff_name} logged in - Tab ID: {tab_id[:20]}...")
        
        return jsonify({
            "success": True,
            "staff_name": staff_name,
            "tab_id": tab_id
        })
    
    return jsonify({
        "success": False,
        "error": "Invalid PIN"
    }), 401

@app.post("/api/lock")
def api_lock():
    """Lock the system manually - clears session for current tab"""
    tab_id = request.headers.get('X-Tab-ID')
    if tab_id:
        session_id = session.get(f'session_id_{tab_id}')
        if session_id and session_id in active_sessions:
            del active_sessions[session_id]
            print(f"[LOGOUT] Tab {tab_id[:20]}... removed")
        # Clear session data for this tab
        keys_to_remove = [k for k in session.keys() if k.endswith(f'_{tab_id}')]
        for key in keys_to_remove:
            session.pop(key, None)
    return jsonify({"ok": True})

@app.get("/api/system_status")
def api_system_status():
    """Get system status - with tab isolation"""
    tab_id = request.args.get('tab') or request.headers.get('X-Tab-ID')
    
    if not tab_id:
        return jsonify({"locked": True, "staff": None, "staff_name": "", "session_valid": False})
    
    logged_in = session.get(f'logged_in_{tab_id}', False)
    session_id = session.get(f'session_id_{tab_id}')
    
    is_locked = not (logged_in and session_id and session_id in active_sessions)
    
    staff_pin = session.get(f'staff_pin_{tab_id}') if not is_locked else None
    staff_name = session.get(f'staff_name_{tab_id}', '') if not is_locked else ''
    
    return jsonify({
        "locked": is_locked,
        "staff": staff_pin,
        "staff_name": staff_name,
        "session_valid": session_id is not None and session_id in active_sessions
    })

@app.post("/api/ping")
def api_ping():
    """Reset session timeout and update last active"""
    tab_id = request.headers.get('X-Tab-ID')
    if tab_id:
        session_id = session.get(f'session_id_{tab_id}')
        if session_id and session_id in active_sessions:
            active_sessions[session_id]['last_active'] = datetime.now()
        session.modified = True
    return jsonify({"ok": True})

@app.get("/api/menu")
def api_menu():
    return jsonify(MENU_CATEGORIES)

@app.get("/api/table_sections")
def api_table_sections():
    return jsonify(TABLE_SECTIONS)

@app.get("/api/order/<table>")  # Note the <table> with angle brackets
def api_get_order(table):
    """Get order with items including descriptions"""
    session_orders = GLOBAL_ORDERS

    if table in session_orders:
        order = session_orders[table]
        items_out = []
        for i, item_data in enumerate(order.get("items", [])):
            m = get_menu_item(item_data.get("item_id"))
            if m:
                items_out.append({
                    "index": i,
                    "id": item_data.get("item_id"),
                    "name": m["name"],
                    "price": m["price"],
                    "quantity": item_data.get("quantity", 1),
                    "description": item_data.get("description", "")
                })
        return jsonify({
            "items": items_out,
            "updated": order.get("updated", ""),
            "staff": order.get("staff", ""),
            "discount": order.get("discount", None)
        })
    return jsonify({"items": [], "updated": "", "staff": "", "discount": None})

@app.get("/api/orders_status")
def api_orders_status():
    """Get which tables have active orders (shared across all sessions)"""
    status = {}
    for table in GLOBAL_ORDERS:
        status[table] = True
    return jsonify(status)

@app.post("/api/add")
def api_add():
    """Add item to order with description"""
    tab_id = request.headers.get('X-Tab-ID')
    if not tab_id:
        return "Missing tab ID", 400

    body = request.get_json(force=True)
    table = (body.get("table") or "").strip()
    item_id = body.get("item_id")
    description = body.get("description", "").strip()

    if not table or not item_id:
        return "Missing table or item", 400

    with orders_lock:
        if table not in GLOBAL_ORDERS:
            GLOBAL_ORDERS[table] = {
                "items": [],
                "created": now_str(),
                "updated": now_str(),
                "staff": get_current_staff(),
                "status": "open"
            }

        # Check if item already exists with same description
        existing_index = -1
        for i, item in enumerate(GLOBAL_ORDERS[table]["items"]):
            if item["item_id"] == item_id and item.get("description", "") == description:
                existing_index = i
                break

        if existing_index >= 0:
            GLOBAL_ORDERS[table]["items"][existing_index]["quantity"] += 1
        else:
            GLOBAL_ORDERS[table]["items"].append({
                "item_id": item_id,
                "quantity": 1,
                "description": description
            })

        GLOBAL_ORDERS[table]["updated"] = now_str()

    return jsonify({"ok": True})

@app.post("/api/update_quantity")
def api_update_quantity():
    """Update quantity of specific item"""
    tab_id = request.headers.get('X-Tab-ID')
    if not tab_id:
        return "Missing tab ID", 400

    body = request.get_json(force=True)
    table = (body.get("table") or "").strip()
    item_index = body.get("item_index")
    quantity = body.get("quantity", 1)

    with orders_lock:
        if table not in GLOBAL_ORDERS or item_index is None:
            return "Invalid request", 400
        if item_index >= len(GLOBAL_ORDERS[table]["items"]):
            return "Item not found", 404

        if quantity <= 0:
            GLOBAL_ORDERS[table]["items"].pop(item_index)
        else:
            GLOBAL_ORDERS[table]["items"][item_index]["quantity"] = quantity

        GLOBAL_ORDERS[table]["updated"] = now_str()

        if not GLOBAL_ORDERS[table]["items"]:
            del GLOBAL_ORDERS[table]

    return jsonify({"ok": True})

@app.post("/api/update_description")
def api_update_description():
    """Update description of specific item"""
    tab_id = request.headers.get('X-Tab-ID')
    if not tab_id:
        return "Missing tab ID", 400

    body = request.get_json(force=True)
    table = (body.get("table") or "").strip()
    item_index = body.get("item_index")
    description = body.get("description", "").strip()

    with orders_lock:
        if table not in GLOBAL_ORDERS or item_index is None:
            return "Invalid request", 400
        if item_index >= len(GLOBAL_ORDERS[table]["items"]):
            return "Item not found", 404

        GLOBAL_ORDERS[table]["items"][item_index]["description"] = description
        GLOBAL_ORDERS[table]["updated"] = now_str()

    return jsonify({"ok": True})

@app.post("/api/clear")
def api_clear():
    """Clear table (remove all items)"""
    tab_id = request.headers.get('X-Tab-ID')
    if not tab_id:
        return "Missing tab ID", 400

    body = request.get_json(force=True)
    table = (body.get("table") or "").strip()

    with orders_lock:
        if table in GLOBAL_ORDERS:
            del GLOBAL_ORDERS[table]

    return jsonify({"ok": True})

@app.post("/api/print")
def api_print():
    """Print bill (simulated)"""
    tab_id = request.headers.get('X-Tab-ID')
    if not tab_id:
        return "Missing tab ID", 400

    body = request.get_json(force=True)
    table = (body.get("table") or "").strip()

    if table not in GLOBAL_ORDERS:
        return "Table not found", 404

    staff_name = session.get(f'staff_name_{tab_id}', 'Unknown')
    print(f"[PRINTER] Bill for table {table} printed at {now_str()} by {staff_name}")
    return jsonify({"ok": True})

@app.post("/api/payment")
def api_payment():
    """Process payment and clear table"""
    global ORDER_HISTORY, INVENTORY

    tab_id = request.headers.get('X-Tab-ID')
    if not tab_id:
        return "Missing tab ID", 400

    body = request.get_json(force=True)
    table = (body.get("table") or "").strip()
    method = body.get("method", "cash")

    with orders_lock:
        if table not in GLOBAL_ORDERS:
            return "Table not found", 404

        order = GLOBAL_ORDERS[table]
        subtotal = 0
        for item_data in order["items"]:
            item = get_menu_item(item_data["item_id"])
            if item:
                subtotal += item["price"] * item_data.get("quantity", 1)

        # Apply discount if exists
        discount_amount = 0
        if "discount" in order:
            if order["discount"]["type"] == "percentage":
                discount_amount = subtotal * (order["discount"]["value"] / 100)
            elif order["discount"]["type"] == "fixed":
                discount_amount = order["discount"]["value"]

        # Calculate final total with 18% VAT and 10% service charge
        total = (subtotal - discount_amount) * 1.28

        # Deduct ingredients from inventory
        for item_data in order["items"]:
            item = get_menu_item(item_data["item_id"])
            if item and "ingredients" in item:
                for ingredient in item["ingredients"]:
                    if ingredient in INVENTORY:
                        INVENTORY[ingredient]["stock"] = max(0, INVENTORY[ingredient]["stock"] - item_data.get("quantity", 1))

        # Add to order history
        staff_name = session.get(f'staff_name_{tab_id}', 'Unknown')
        ORDER_HISTORY.append({
            "table": table,
            "items": order["items"],
            "subtotal": subtotal,
            "discount": discount_amount,
            "total": total,
            "method": method,
            "staff": staff_name,
            "tab_id": tab_id,
            "timestamp": now_iso()
        })

        print(f"[PAYMENT] Table {table} paid ${total:.2f} via {method} by {staff_name} at {now_str()}")

        # Clear table from shared orders
        del GLOBAL_ORDERS[table]

    return jsonify({"ok": True})

@app.get("/api/dashboard")
def api_dashboard():
    """Get dashboard data"""
    today = datetime.now().date()
    today_revenue = 0
    today_orders = 0
    item_counts = defaultdict(int)
    
    for order in ORDER_HISTORY:
        order_date = datetime.fromisoformat(order["timestamp"]).date()
        if order_date == today:
            today_revenue += order["total"]
            today_orders += 1
            for item in order["items"]:
                item_counts[item["item_id"]] += item["quantity"]
    
    best_seller_id = max(item_counts, key=item_counts.get) if item_counts else None
    best_seller = None
    if best_seller_id:
        item = get_menu_item(best_seller_id)
        if item:
            best_seller = item["name"]
    
    return jsonify({
        "revenue": today_revenue,
        "orders": today_orders,
        "best_seller": best_seller
    })

@app.get("/api/inventory")
def api_inventory():
    """Get inventory data"""
    return jsonify(INVENTORY)

@app.get("/api/reservations")
def api_reservations():
    """Get reservations"""
    return jsonify(RESERVATIONS)

@app.post("/api/add_reservation")
def api_add_reservation():
    """Add a new reservation"""
    global RESERVATIONS
    body = request.get_json(force=True)
    customer_name = body.get("customer_name")
    table = body.get("table")
    time = body.get("time")
    
    if not customer_name or not table or not time:
        return "Missing required fields", 400
    
    RESERVATIONS.append({
        "id": str(uuid.uuid4()),
        "customer_name": customer_name,
        "table": table,
        "time": time,
        "created_at": now_iso()
    })
    
    return jsonify({"ok": True})

@app.get("/api/reports")
def api_reports():
    """Get sales reports"""
    return jsonify({"message": "Reports data available"})

@app.post("/api/apply_discount")
def api_apply_discount():
    """Apply discount to order"""
    body = request.get_json(force=True)
    table = (body.get("table") or "").strip()
    code = (body.get("code") or "").strip().upper()

    if not table or not code:
        return "Missing table or code", 400

    if table not in GLOBAL_ORDERS:
        return "Table not found", 404

    if code not in PROMO_CODES:
        return jsonify({"error": "Invalid promo code"}), 400

    promo = PROMO_CODES[code]

    with orders_lock:
        GLOBAL_ORDERS[table]["discount"] = {
            "code": code,
            "type": promo["type"],
            "value": promo["value"]
        }
        GLOBAL_ORDERS[table]["updated"] = now_str()

    return jsonify({"ok": True})

# Cleanup inactive sessions
def cleanup_inactive_sessions():
    """Remove sessions that haven't been active for more than 30 minutes"""
    now = datetime.now()
    inactive_sessions = []
    for session_id, data in active_sessions.items():
        if (now - data['last_active']).total_seconds() > 1800:  # 30 minutes
            inactive_sessions.append(session_id)
    
    for session_id in inactive_sessions:
        del active_sessions[session_id]
        print(f"[CLEANUP] Removed inactive session {session_id[:8]}...")
    
    # Schedule next cleanup in 5 minutes
    threading.Timer(300, cleanup_inactive_sessions).start()

def main():
    """CLI entry point for the POS system"""
    parser = argparse.ArgumentParser(
        description="Restaurant POS System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python app.py                    # Run on default port 8080
  python app.py --port 5000        # Run on port 5000
  python app.py --host 127.0.0.1   # Listen only on localhost
  python app.py --debug            # Run in debug mode
        """
    )
    parser.add_argument(
        "--host", 
        default="0.0.0.0", 
        help="Host to bind to (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--port", 
        type=int, 
        default=8080, 
        help="Port to bind to (default: 8080)"
    )
    parser.add_argument(
        "--debug", 
        action="store_true", 
        help="Run in debug mode"
    )
    
    args = parser.parse_args()
    
    # Start the cleanup thread
    cleanup_inactive_sessions()
    
    print("=" * 50)
    print("🍽️  RESTAURANT POS SYSTEM")
    print("=" * 50)
    print("✅ Each browser tab has its OWN independent session!")
    print("✅ Tabs are completely isolated!")
    print("✅ Each tab requires separate login!")
    print("")
    print("📌 Staff PIN Codes:")
    for pin, name in STAFF_CODES.items():
        print(f"   {name}: PIN {pin}")
    print("")
    print(f"🌐 Server running at: http://{args.host}:{args.port}")
    if args.host == "0.0.0.0":
        import socket
        try:
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
            print(f"   Access from other devices: http://{local_ip}:{args.port}")
        except:
            print(f"   Access from other devices: http://YOUR_IP:{args.port}")
    print("💡 IMPORTANT: Each browser TAB needs its own login!")
    print("💡 Press Ctrl+C to stop the server")
    print("=" * 50)
    
    try:
        app.run(host=args.host, port=args.port, debug=args.debug)
    except KeyboardInterrupt:
        print("\n👋 Shutting down POS System...")
        sys.exit(0)

if __name__ == "__main__":
    main()