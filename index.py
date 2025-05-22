import os
import json
import random
import string
import time
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.select import Select
from fp.fp import FreeProxy
import unidecode

app = Flask(__name__)
PORT = int(os.getenv('PORT', 11000))

# Configuration
class Config:
    MAX_RANDOM_ACCOUNTS = 10
    DEFAULT_GENDER = "male"
    MIN_AGE = 18
    MAX_AGE = 60
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15",
        "Mozilla/5.0 (Linux; Android 10; SM-G975F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Mobile Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36 Edg/106.0.1370.52",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 YaBrowser/21.8.1.468 Yowser/2.5 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:106.0) Gecko/20100101 Firefox/106.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:105.0) Gecko/20100101 Firefox/105.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64; rv:105.0) Gecko/20100101 Firefox/105.0",
    ]
    FIRST_NAMES = [
        "Akira", "Li", "Mohammed", "James", "Maria", "Hiroshi", "Wang", "Ali", "John", "Ana",
        "Yuki", "Zhang", "Fatima", "Robert", "Liza", "Kenji", "Chen", "Aisha", "Michael", "Rosa",
        "Haruto", "Huang", "Zainab", "David", "Carla", "Sakura", "Lin", "Omar", "William", "Gloria",
        "Takeshi", "Cheng", "Salma", "Joseph", "Isabel", "Yoshio", "Deng", "Nadia", "Richard", "Sofia",
    ]
    LAST_NAMES = [
        "Tanaka", "Li", "Al-Saud", "Smith", "Garcia", "Suzuki", "Wang", "Al-Mansour", "Johnson", "Rodriguez",
        "Yamamoto", "Zhang", "Al-Fahad", "Williams", "Lopez", "Nakamura", "Chen", "Al-Hussein", "Brown", "Martinez",
        "Sato", "Huang", "Al-Ghamdi", "Jones", "Gonzalez", "Takahashi", "Lin", "Al-Jaber", "Davis", "Sanchez",
    ]

# Helper functions
def generate_random_name():
    first = random.choice(Config.FIRST_NAMES)
    last = random.choice(Config.LAST_NAMES)
    return {"first": first, "last": last}

def generate_username(first, last):
    random_num = random.randint(1000, 9999)
    first_normalized = unidecode.unidecode(first).lower()
    last_normalized = unidecode.unidecode(last).lower()
    return f"{first_normalized}.{last_normalized}{random_num}"

def generate_random_birthday():
    current_year = datetime.now().year
    birth_year = current_year - random.randint(Config.MIN_AGE, Config.MAX_AGE)
    birth_month = random.randint(1, 12)
    birth_day = random.randint(1, 28)  # Safe day for all months
    return f"{birth_day} {birth_month} {birth_year}"

def parse_birthday(bd_param):
    if not bd_param:
        return generate_random_birthday()
    
    # Handle various date formats: 15-5-1995, 15/5/1995, 15 5 1995
    separators = ['-', '/', ' ']
    for sep in separators:
        if sep in bd_param:
            parts = bd_param.split(sep)
            if len(parts) == 3:
                try:
                    day = int(parts[0])
                    month = int(parts[1])
                    year = int(parts[2])
                    
                    # Validate date
                    if 1 <= day <= 31 and 1 <= month <= 12 and 1900 < year < datetime.now().year - Config.MIN_AGE:
                        return f"{day} {month} {year}"
                except ValueError:
                    continue
    
    return generate_random_birthday()

def generate_strong_password(length=12):
    chars = string.ascii_letters + string.digits + "!@#$%^&*()"
    while True:
        password = ''.join(random.choice(chars) for _ in range(length))
        # Ensure password has at least one of each: uppercase, lowercase, digit, special
        if (any(c.isupper() for c in password)) and \
           (any(c.islower() for c in password)) and \
           (any(c.isdigit() for c in password)) and \
           (any(c in "!@#$%^&*()" for c in password)):
            return password

def get_working_proxy():
    try:
        proxy = FreeProxy(rand=True, timeout=1).get()
        print(f"Using proxy: {proxy}")
        return proxy
    except Exception as e:
        print("Failed to get proxy, continuing without proxy")
        return None

def save_account_to_file(account):
    file_path = Path(__file__).parent / 'accounts.json'
    accounts = []
    
    try:
        if file_path.exists():
            with open(file_path, 'r') as f:
                accounts = json.load(f)
    except Exception as e:
        print(f"Error reading accounts file: {e}")
    
    accounts.append(account)
    with open(file_path, 'w') as f:
        json.dump(accounts, f, indent=2)

# Custom account creation endpoint
@app.route('/api/create', methods=['GET'])
def create_custom_account():
    start_time = time.time()
    
    try:
        # Parse query parameters with fallbacks
        name = request.args.get('name')
        if not name:
            name_data = generate_random_name()
            name = f"{name_data['first']} {name_data['last']}"
        
        birthday = parse_birthday(request.args.get('birthday'))
        gender = request.args.get('gender', Config.DEFAULT_GENDER).lower()
        username = request.args.get('username')
        password = request.args.get('password', generate_strong_password())
        
        if not username:
            first, last = name.split(' ', 1) if ' ' in name else (name, '')
            username = f"{first.lower()}.{last.lower()}{random.randint(100, 999)}" if last else f"{first.lower()}{random.randint(1000, 9999)}"

        account_info = {
            "name": name,
            "birthday": birthday,
            "gender": gender if gender in ["male", "female"] else Config.DEFAULT_GENDER,
            "username": username,
            "email": f"{username}@gmail.com",
            "password": password
        }

        result = create_account(account_info)
        save_account_to_file(result)

        response = {
            "success": True,
            "data": {
                "account": result
            },
            "meta": {
                "duration": f"{(time.time() - start_time):.2f} seconds",
                "method": "custom"
            }
        }
        return jsonify(response)
    except Exception as e:
        print(f"API Error: {e}")
        return jsonify({
            "success": False,
            "error": "Internal server error",
            "details": str(e)
        }), 500

# Random account creation endpoint
@app.route('/api/create/random', methods=['GET'])
def create_random_accounts():
    start_time = time.time()
    
    try:
        limit = request.args.get('limit', default=1, type=int)
        limit = min(limit, Config.MAX_RANDOM_ACCOUNTS)
        
        accounts = []
        errors = []
        
        for i in range(limit):
            try:
                name_data = generate_random_name()
                username = generate_username(name_data['first'], name_data['last'])
                
                account_info = {
                    "name": f"{name_data['first']} {name_data['last']}",
                    "birthday": generate_random_birthday(),
                    "gender": random.choice(["male", "female"]),
                    "username": username,
                    "email": f"{username}@gmail.com",
                    "password": generate_strong_password()
                }

                result = create_account(account_info)
                accounts.append(result)
                save_account_to_file(result)
            except Exception as e:
                errors.append({
                    "attempt": i + 1,
                    "error": str(e)
                })

        response = {
            "success": True,
            "meta": {
                "requested": limit,
                "created": len(accounts),
                "failed": len(errors),
                "duration": f"{(time.time() - start_time):.2f} seconds",
                "method": "random"
            },
            "data": {
                "accounts": {i+1: acc for i, acc in enumerate(accounts)}
            },
            "errors": errors if errors else None
        }
        return jsonify(response)
    except Exception as e:
        print(f"API Error: {e}")
        return jsonify({
            "success": False,
            "error": "Internal server error",
            "details": str(e)
        }), 500

# Function to create a single account
def create_account(account_info):
    driver = None
    try:
        options = Options()
        options.headless = True
        user_agent = random.choice(Config.USER_AGENTS)
        options.set_preference("general.useragent.override", user_agent)

        # Configure proxy if available
        proxy = get_working_proxy()
        if proxy:
            host, port = proxy.split(':')
            options.set_preference('network.proxy.type', 1)
            options.set_preference('network.proxy.http', host)
            options.set_preference('network.proxy.http_port', int(port))
            options.set_preference('network.proxy.ssl', host)
            options.set_preference('network.proxy.ssl_port', int(port))

        driver = webdriver.Firefox(options=options)
        device_uuid = str(uuid.uuid4())
        print(f"Creating account for {account_info['email']} with UUID: {device_uuid}")

        driver.get("https://accounts.google.com/signup/v2/createaccount?flowName=GlifWebSignIn&flowEntry=SignUp")

        # Fill in the name fields
        first_name = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "firstName")))
        last_name = driver.find_element(By.NAME, "lastName")
        
        name_parts = account_info['name'].split(' ', 1)
        first_name.clear()
        first_name.send_keys(name_parts[0])
        last_name.clear()
        last_name.send_keys(name_parts[1] if len(name_parts) > 1 else "")

        next_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//span[text()='Next']")))
        next_button.click()

        # Fill birthday and gender
        day, month, year = account_info['birthday'].split()
        month_dropdown = Select(driver.find_element(By.ID, "month"))
        month_dropdown.select_by_value(month)
        
        day_field = driver.find_element(By.ID, "day")
        day_field.clear()
        day_field.send_keys(day)
        
        year_field = driver.find_element(By.ID, "year")
        year_field.clear()
        year_field.send_keys(year)
        
        gender_dropdown = Select(driver.find_element(By.ID, "gender"))
        gender_value = "1" if account_info['gender'].lower() == "male" else "2"
        gender_dropdown.select_by_value(gender_value)
        
        next_button2 = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//span[text()='Next']")))
        next_button2.click()

        # Create custom email
        time.sleep(2)
        try:
            create_own_option = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//div[contains(text(), 'Create your own Gmail address')]")))
            create_own_option.click()
        except:
            print("No 'Create your own' option found")

        username_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "Username")))
        username_field.clear()
        username_field.send_keys(account_info['username'])
        
        next_button3 = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//span[text()='Next']")))
        next_button3.click()

        # Enter and confirm password
        password_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "Passwd")))
        password_field.clear()
        password_field.send_keys(account_info['password'])
        
        confirm_passwd = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "PasswdAgain")))
        confirm_passwd.clear()
        confirm_passwd.send_keys(account_info['password'])
        
        next_button4 = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//span[text()='Next']")))
        next_button4.click()

        # Skip phone number and recovery email
        try:
            skip_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//span[contains(text(),'Skip')]")))
            skip_button.click()
        except:
            print("No phone number verification step")

        # Agree to terms
        agree_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//span[text()='I agree']")))
        agree_button.click()

        # Wait for account creation to complete
        WebDriverWait(driver, 30).until(
            lambda d: "myaccount.google.com" in d.current_url)

        return {
            **account_info,
            "status": "created",
            "timestamp": datetime.now().isoformat(),
            "deviceId": device_uuid
        }
    except Exception as e:
        print(f"Account creation failed: {e}")
        raise Exception(f"Failed to create account {account_info['email']}: {str(e)}")
    finally:
        if driver:
            try:
                driver.quit()
            except Exception as e:
                print(f"Error closing driver: {e}")
                
# Health check endpoint
@app.route('/', methods=['GET'])
def health_check():
    return jsonify({
        "status": "running",
        "service": "Gmail Account Creator API",
        "version": "1.1.0",
        "endpoints": {
            "createCustom": {
                "method": "GET",
                "path": "/api/create",
                "description": "Create custom Gmail account",
                "parameters": {
                    "name": "Full name (optional)",
                    "birthday": 'Birthday in format "DD-MM-YYYY", "DD/MM/YYYY", or "DD MM YYYY" (optional)',
                    "gender": "Gender ('male' or 'female') (optional)",
                    "username": "Desired username (optional)",
                    "password": "Password for the account (optional)"
                },
                "example": "/api/create?name=John+Doe&birthday=15-5-1995&gender=male&username=johndoe.alpha&password=Str0ngP@ss"
            },
            "createRandom": {
                "method": "GET",
                "path": "/api/create/random",
                "description": f"Create random Gmail accounts (max {Config.MAX_RANDOM_ACCOUNTS})",
                "parameters": {
                    "limit": "Number of accounts to create (optional, default 1)"
                },
                "example": "/api/create/random?limit=3"
            }
        }
    })

if __name__ == '__main__':
    print(f"Server running on port {PORT}")
    print("Available endpoints:")
    print("- Custom account: GET /api/create?name=John&birthday=15-5-1995&gender=male&username=john123&password=pass123")
    print("- Random accounts: GET /api/create/random?limit=3")
    app.run(host='0.0.0.0', port=PORT)
