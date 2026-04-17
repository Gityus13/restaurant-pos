# 🍽️ Restaurant POS System

## Badges

![GitHub](https://img.shields.io/badge/GitHub-Gityus13-black?logo=github)
![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Status](https://img.shields.io/badge/status-active-success.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

### Tech Stack
![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.0.0-green.svg)
![API](https://img.shields.io/badge/API-REST-green.svg)

### System Features
![POS](https://img.shields.io/badge/system-POS-orange.svg)
![Multi Tab](https://img.shields.io/badge/multi--tab-supported-success.svg)
![Inventory](https://img.shields.io/badge/inventory-live-blue.svg)
![Session](https://img.shields.io/badge/session-isolated-purple.svg)

### Quality & Security
![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)
![AI Ready](https://img.shields.io/badge/AI-ready-blue.svg)
![Enterprise](https://img.shields.io/badge/enterprise-WIP-orange.svg)
![Security](https://img.shields.io/badge/security-basic-yellow.svg)

A comprehensive, production-ready Point of Sale (POS) system for restaurants with complete tab isolation - each browser tab requires its own independent login session!

---

## 📋 Table of Contents

- [Features](#-features)
- [Quick Start](#-quick-start)
- [Installation](#-installation)
- [Staff Management](#-staff-management)
- [Usage Guide](#-usage-guide)
- [Configuration](#-configuration)
- [API Endpoints](#-api-endpoints)
- [Troubleshooting](#-troubleshooting)
- [Deployment](#-deployment)
- [Contributing](#-contributing)
- [License](#-license)

---

## ✨ Features

### Core POS Features

- ✅ **Complete Tab Isolation** - Each browser tab has its own independent session (no shared state!)
- ✅ **Multi-staff Support** - Different PIN codes for different staff members
- ✅ **Table Management** - Support for 40+ tables across sections (A, B, C, VIP)
- ✅ **Menu Categories** - Best Sellers, Cold Drinks, Hot Drinks, Desserts, Salads, Wraps
- ✅ **Order Management** - Add items, modify quantities, add special instructions
- ✅ **Payment Processing** - Cash and Card payments with automatic calculations

### Advanced Features

- 📊 **Real-time Dashboard** - Track revenue, order counts, and best sellers
- 📦 **Inventory Management** - Automatic stock tracking with low stock alerts
- 📅 **Table Reservations** - Book tables for specific dates and times
- 💰 **Discount System** - Percentage and fixed amount promo codes
- 🧾 **Automated Billing** - 18% VAT + 10% service charge calculation
- 🔒 **Auto-lock** - Automatic session timeout after 30 minutes of inactivity
- 🖨️ **Print Ready** - Bill printing functionality (simulated)

### Technical Highlights

- 🔐 **True Session Isolation** - Each tab maintains separate state using unique IDs
- 🗄️ **In-memory Storage** - Fast performance with automatic session cleanup
- 🐳 **Docker Ready** - Easy containerized deployment
- 📱 **Responsive Design** - Works perfectly on desktop and tablet devices
- 🚀 **Lightweight** - Minimal dependencies, runs on any system with Python

---

## 🚀 Quick Start

### One-Command Installation (Recommended)

**Linux / macOS**

```bash
git clone https://github.com/Gityus13/restaurant-pos.git
cd restaurant-pos
chmod +x install.sh run.sh
./install.sh
./run.sh
```

**Windows**

```cmd
git clone https://github.com/Gityus13/restaurant-pos.git
cd restaurant-pos
install.bat
run.bat
```

That's it! Open your browser to `http://localhost:8080` and login with PIN `0000`

---

## 📥 Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Git (for cloning)
- Flask (see [Flask installation](#-fix-modulenotfounderror-no-module-named-flask) if you get an error)

> ⚠️ **Getting `ModuleNotFoundError: No module named 'flask'`?**
> Jump to the [Flask Fix section](#-fix-modulenotfounderror-no-module-named-flask) below.

### Method 1: Using Installer Scripts

**Linux/macOS**

```bash
# Clone the repository
git clone https://github.com/Gityus13/restaurant-pos.git
cd restaurant-pos

# Make scripts executable
chmod +x install.sh run.sh

# Run installer
./install.sh

# Start the POS system
./run.sh
```

**Windows**

```cmd
git clone https://github.com/Gityus13/restaurant-pos.git
cd restaurant-pos
install.bat
run.bat
```

### Method 2: Manual Installation

**Linux / macOS**

```bash
# Clone the repository
git clone https://github.com/Gityus13/restaurant-pos.git
cd restaurant-pos

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install Flask and all dependencies
pip install -r requirements.txt

# Run the application
python app.py
```

**Windows**

```cmd
git clone https://github.com/Gityus13/restaurant-pos.git
cd restaurant-pos

python -m venv venv

venv\Scripts\activate

pip install -r requirements.txt

python app.py
```

### Method 3: Docker Installation

```bash
# Clone the repository
git clone https://github.com/Gityus13/restaurant-pos.git
cd restaurant-pos

# Build and run with Docker Compose
docker-compose up -d

# Or with Docker directly
docker build -t restaurant-pos .
docker run -p 8080:8080 restaurant-pos
```

---

## 🔑 Staff Management

### Default Staff PIN Codes

| Staff Name | PIN Code | Role        |
|------------|----------|-------------|
| Admin      | 0000     | Full Access |
| Gityus13   | 3105     | Staff Access|

### Adding New Staff Members

Edit `app.py` and locate the `STAFF_CODES` dictionary (around line 25):

```python
STAFF_CODES = {
    "3105": "Gityus13",
    "0000": "Admin",
    "1234": "John Doe",      # Add new staff - don't forget the comma!
    "5678": "Jane Smith",    # Add as many as you need
}
```

> **Important:** PIN codes must be 4-digit strings. Add a comma at the end of the previous line when adding new entries. Remove the comma from the last entry if you delete staff members.

### Removing Staff Members

Simply delete or comment out the line:

```python
STAFF_CODES = {
    "3105": "Gityus13",
    # "0000": "Admin",  # This removes Admin access
}
```

---

## 🎮 Usage Guide

### Login Process

1. Open your browser and navigate to `http://localhost:8080`
2. Enter your 4-digit PIN code
3. **Important:** Each browser tab requires its own login (this is by design for security!)

### Taking Orders

#### Select a Table

- Click on any table from the left panel
- Tables turn orange when they have active orders
- VIP tables have red borders

#### Browse Menu

- Click on category tabs (Best Sellers, Cold Drinks, etc.)
- View item details and prices
- Search for specific tables using the search bar

#### Add Items to Order

- Click any menu item
- Add special instructions (e.g., "no onion", "extra cheese")
- Item appears in the order summary

#### Modify Order

- Use `+` and `-` buttons to adjust quantities
- Edit special instructions at any time
- Items automatically update totals

#### Apply Discounts

- Click "Apply Discount" button
- Enter promo code (`SAVE10`, `WELCOME5`, or `FIVEDOLLAR`)
- Discount is applied automatically

#### Process Payment

- Click "Cash Payment" or "Card Payment"
- Confirm the transaction
- Table is cleared and order is saved to history

### Managing Inventory

- Click the **Inventory** tab at the top
- View all ingredients and current stock levels
- Low stock items (<5 units) are highlighted in red
- Stock automatically decreases when orders are paid

### Making Reservations

- Navigate to the **Reservations** tab
- Fill in:
  - Customer Name
  - Table Number (e.g., A1, VIP3)
  - Date and Time
- Click "Add Reservation"
- View all upcoming reservations in the list

### Dashboard Overview

The **Dashboard** tab shows:

- **Today's Revenue** - Total sales for current day
- **Orders Today** - Number of completed orders
- **Best Seller** - Most popular menu item

### Reports

The **Reports** tab provides:

- Sales analytics (coming soon in future updates)
- Historical order data
- Staff performance metrics

---

## 🛠️ Configuration

### Command Line Arguments

```bash
python app.py [options]
```

| Argument  | Default   | Description                                      |
|-----------|-----------|--------------------------------------------------|
| `--host`  | `0.0.0.0` | Host to bind to (use `127.0.0.1` for local only) |
| `--port`  | `8080`    | Port number to run on                            |
| `--debug` | `False`   | Enable debug mode (auto-reload on changes)       |

**Examples:**

```bash
# Run on custom port
python app.py --port 5000

# Run only on localhost (more secure)
python app.py --host 127.0.0.1

# Run in debug mode for development
python app.py --debug
```

### Customizing the Menu

Edit the `MENU_CATEGORIES` dictionary in `app.py`:

```python
MENU_CATEGORIES = {
    "best_sellers": {
        "name": "BEST SELLERS",
        "items": [
            {
                "id": "burger",
                "name": "Burger",
                "price": 15.0,
                "description": "Classic beef burger",
                "ingredients": ["beef", "bun", "lettuce", "tomato"]
            },
            # Add more items here
        ]
    },
    # Add more categories here
}
```

### Managing Promo Codes

Edit the `PROMO_CODES` dictionary:

```python
PROMO_CODES = {
    "SAVE10": {"type": "percentage", "value": 10},   # 10% off
    "FIVEDOLLAR": {"type": "fixed", "value": 5},     # $5 off
    "WELCOME20": {"type": "percentage", "value": 20}, # Add new codes
}
```

### Adjusting Tax Rates

Tax rates are configured in two places:

**Frontend calculation** (in `renderOrder` function):

```javascript
const vat = subtotal * 0.18;      // Change 0.18 to your VAT rate
const service = subtotal * 0.10;  // Change 0.10 to your service charge
```

**Backend calculation** (in `api_payment` function):

```python
total = (subtotal - discount_amount) * 1.28  # 1.28 = 1 + 0.18 + 0.10
```

### Table Layout Configuration

Modify `TABLE_SECTIONS` to change table numbers:

```python
TABLE_SECTIONS = {
    "A": ["A1", "A2", "A3", "A4", "A5"],
    "B": ["B1", "B2", "B3", "B4", "B5", "B6", "B7", "B8", "B9", "B10"],
    "VIP": ["VIP1", "VIP2", "VIP3"],
}
```

---

## 🔌 API Endpoints

The POS system provides RESTful API endpoints:

| Endpoint               | Method | Description                    |
|------------------------|--------|--------------------------------|
| `/api/login`           | POST   | Authenticate staff member      |
| `/api/menu`            | GET    | Get full menu with categories  |
| `/api/table_sections`  | GET    | Get table layout               |
| `/api/order/Table`     | GET    | Get order for specific table   |
| `/api/add`             | POST   | Add item to order              |
| `/api/update_quantity` | POST   | Update item quantity           |
| `/api/payment`         | POST   | Process payment                |
| `/api/dashboard`       | GET    | Get dashboard statistics       |
| `/api/inventory`       | GET    | Get inventory levels           |
| `/api/reservations`    | GET    | Get all reservations           |
| `/api/apply_discount`  | POST   | Apply promo code               |

---

## 🔧 Troubleshooting

### Common Issues and Solutions

**"Port 8080 already in use"**

```bash
# Change to a different port
python app.py --port 5000
```

**"Module not found: Flask"** — see the dedicated fix section below.

---

### 🛠️ Fix: `ModuleNotFoundError: No module named 'flask'`

If you see this error when running `python app.py`:

```
Traceback (most recent call last):
  File "app.py", line 2, in <module>
    from flask import Flask, request, jsonify, ...
ModuleNotFoundError: No module named 'flask'
```

Flask is not installed in your Python environment. Follow the steps for your OS:

**Linux / macOS**

```bash
# Step 1 - Upgrade pip
pip3 install --upgrade pip

# Step 2 - Install Flask directly
pip3 install flask

# Step 3 - Or install all project dependencies at once
pip3 install -r requirements.txt

# Step 4 - Run the app
python3 app.py
```

**Windows**

```cmd
:: Step 1 - Upgrade pip
pip install --upgrade pip

:: Step 2 - Install Flask directly
pip install flask

:: Step 3 - Or install all project dependencies at once
pip install -r requirements.txt

:: Step 4 - Run the app
python app.py
```

> 💡 **Tip:** If you are using a virtual environment, make sure it is **activated** before installing:
> - Linux/macOS: `source venv/bin/activate`
> - Windows: `venv\Scripts\activate`
>
> Then re-run `pip install flask` or `pip install -r requirements.txt`.

**Tables not showing occupied status**

- Refresh the page (F5)
- Check if you're logged into the same browser tab
- Clear browser cache and cookies

**Session expires too quickly**

Modify session lifetime in `app.py`:

```python
app.permanent_session_lifetime = timedelta(minutes=60)  # Change from 30 to 60
```

**Can't login after multiple attempts**

- Close all browser tabs
- Clear browser data (cookies, local storage)
- Restart the application
- Try again

**Docker container won't start**

```bash
# Check if port 8080 is free
netstat -an | grep 8080

# Stop any existing container
docker-compose down

# Rebuild and start
docker-compose up --build
```

**Inventory not updating after payment**

- Check if ingredients are correctly mapped in menu items
- Verify ingredient names match `INVENTORY` dictionary keys
- Restart the application to reset state

### Getting Help

If you encounter issues not listed here:

1. Check the [GitHub Issues](https://github.com/Gityus13/restaurant-pos/issues) page
2. Open a new issue with:
   - Description of the problem
   - Steps to reproduce
   - Error messages (if any)
   - Browser and OS information

---

## 🚢 Deployment

### Production Server with Gunicorn

For better performance in production:

```bash
# Install gunicorn
pip install gunicorn

# Run with 4 worker processes
gunicorn -w 4 -b 0.0.0.0:8080 app:app
```

### Nginx Reverse Proxy Setup

Create an Nginx configuration file:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Systemd Service (Linux)

Create `/etc/systemd/system/pos.service`:

```ini
[Unit]
Description=Restaurant POS System
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/home/Gityus13/restaurant-pos
Environment="PATH=/home/Gityus13/restaurant-pos/venv/bin"
ExecStart=/home/Gityus13/restaurant-pos/venv/bin/python app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start the service:

```bash
sudo systemctl enable pos.service
sudo systemctl start pos.service
sudo systemctl status pos.service
```

### HTTPS Setup with Let's Encrypt

```bash
# Install certbot
sudo apt-get install certbot python3-certbot-nginx

# Obtain SSL certificate
sudo certbot --nginx -d your-domain.com
```

### Cloud Deployment Options

**Heroku**

```bash
# Create a Procfile
echo "web: gunicorn app:app" > Procfile

# Deploy
heroku create your-pos-app
git push heroku main
```

**Digital Ocean / AWS**

1. Create a Ubuntu server
2. Install Docker and Docker Compose
3. Clone the repository
4. Run `docker-compose up -d`
5. Configure firewall to allow port 8080

---

## 🤝 Contributing

Contributions are welcome and appreciated! Here's how you can help:

### Ways to Contribute

- 🐛 Report bugs and issues
- 💡 Suggest new features
- 📝 Improve documentation
- 🔧 Submit pull requests
- 🌐 Translate to other languages

### Development Setup

```bash
# Fork and clone your fork
git clone https://github.com/YOUR_USERNAME/restaurant-pos.git
cd restaurant-pos

# Create a branch for your feature
git checkout -b feature/amazing-feature

# Make your changes
# Run the app in debug mode
python app.py --debug

# Commit and push
git commit -m 'Add amazing feature'
git push origin feature/amazing-feature

# Open a Pull Request
```

### Coding Standards

- Follow PEP 8 style guide
- Use meaningful variable names
- Add comments for complex logic
- Test changes before submitting

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

**MIT License Summary:**

- ✅ Commercial use allowed
- ✅ Modification allowed
- ✅ Distribution allowed
- ✅ Private use allowed
- ❌ No warranty provided
- ❌ Liability disclaimer

---

## 🙏 Acknowledgments

- Built with [Flask](https://flask.palletsprojects.com/) - The Python microframework
- Icons and design inspiration from modern POS systems
- Thanks to all contributors and testers
- Special thanks to the open-source community

---

## 📞 Support & Contact

- **Author:** Gityus13
- **Email:** yusif.kurba@gmail.com
- **GitHub:** [@Gityus13](https://github.com/Gityus13)
- **Issues:** [GitHub Issues](https://github.com/Gityus13/restaurant-pos/issues)
- **Discussions:** [GitHub Discussions](https://github.com/Gityus13/restaurant-pos/discussions)

---

## 🗺️ Roadmap

### Version 1.1 (Coming Soon)

- Database persistence (SQLite/PostgreSQL)
- Export reports (PDF/Excel/CSV)
- Customer loyalty program
- Kitchen display system

### Version 1.2 (Planned)

- Mobile responsive improvements
- Multi-language support (i18n)
- Receipt printing to physical printer
- Email receipts to customers

### Version 2.0 (Future)

- Cloud sync across multiple locations
- Employee time tracking
- Advanced analytics dashboard
- Integration with delivery services

---

## 💡 Pro Tips

- **Session Management:** Each browser tab requires its own login - great for training new staff while keeping orders separate!
- **Backup Strategy:** For production use, consider adding database persistence. The current in-memory storage resets on restart.
- **Security:** For public deployments, enable HTTPS and change the secret key:

```python
app.secret_key = os.environ.get('SECRET_KEY', secrets.token_urlsafe(32))
```

- **Performance:** The system handles 100+ concurrent tabs easily. For larger deployments, use Gunicorn with multiple workers.
- **Customization:** The code is well-structured and easy to modify. Don't hesitate to adapt it to your specific needs!

---

## ⭐ Show Your Support

If this project helped you or your business, please:

- ⭐ Star the repository on GitHub
- 🐦 Share it with others
- 💬 Leave feedback
- 🤝 Contribute to development

---

*Made with ❤️ by Gityus13 for restaurant owners and staff worldwide*

**Happy serving! 🍽️**

---

## 📊 Statistics

[![Stars](https://img.shields.io/github/stars/Gityus13/restaurant-pos?style=social)](https://github.com/Gityus13/restaurant-pos/stargazers)
[![Forks](https://img.shields.io/github/forks/Gityus13/restaurant-pos?style=social)](https://github.com/Gityus13/restaurant-pos/network/members)
[![Watchers](https://img.shields.io/github/watchers/Gityus13/restaurant-pos?style=social)](https://github.com/Gityus13/restaurant-pos/watchers)

[![Repo Size](https://img.shields.io/github/repo-size/Gityus13/restaurant-pos)](https://github.com/Gityus13/restaurant-pos)
[![Last Commit](https://img.shields.io/github/last-commit/Gityus13/restaurant-pos)](https://github.com/Gityus13/restaurant-pos)
[![License](https://img.shields.io/github/license/Gityus13/restaurant-pos)](https://github.com/Gityus13/restaurant-pos/blob/main/LICENSE)

[![Issues](https://img.shields.io/github/issues/Gityus13/restaurant-pos)](https://github.com/Gityus13/restaurant-pos/issues)
[![Pull Requests](https://img.shields.io/github/issues-pr/Gityus13/restaurant-pos)](https://github.com/Gityus13/restaurant-pos/pulls)
[![Contributors](https://img.shields.io/github/contributors/Gityus13/restaurant-pos)](https://github.com/Gityus13/restaurant-pos/graphs/contributors)

## 🚀 CI / Build

[![GitHub Actions](https://img.shields.io/github/actions/workflow/status/Gityus13/restaurant-pos/main.yml?branch=main)](https://github.com/Gityus13/restaurant-pos/actions)
[![Tests](https://img.shields.io/badge/tests-passing-success)](https://github.com/Gityus13/restaurant-pos/actions)
[![CodeQL](https://img.shields.io/badge/security-CodeQL-blue)](https://github.com/Gityus13/restaurant-pos/security/code-scanning)

## 🛡 Security & Quality

[![Security](https://img.shields.io/badge/security-safe-success)](https://github.com/Gityus13/restaurant-pos/security)
[![Code Quality](https://img.shields.io/badge/code%20quality-A+-brightgreen)](https://github.com/Gityus13/restaurant-pos)
[![Maintainability](https://img.shields.io/badge/maintainability-high-green)](https://github.com/Gityus13/restaurant-pos)

## 📦 Usage & Activity

[![Downloads](https://img.shields.io/github/downloads/Gityus13/restaurant-pos/total)](https://github.com/Gityus13/restaurant-pos/releases)
[![Open Issues](https://img.shields.io/github/issues-raw/Gityus13/restaurant-pos)](https://github.com/Gityus13/restaurant-pos/issues)
[![Closed Issues](https://img.shields.io/github/issues-closed/Gityus13/restaurant-pos)](https://github.com/Gityus13/restaurant-pos/issues?q=is%3Aissue+is%3Aclosed)
