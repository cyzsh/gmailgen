import os
import json
import random
import string
import time
import uuid
from datetime import datetime
from pathlib import Path
from flask import Flask, request, jsonify
from fp.fp import FreeProxy
import unidecode
from playwright.sync_api import sync_playwright

def install_playwright_browsers():
    try:
        subprocess.run(["playwright", "install", "chromium"], check=True)
        subprocess.run(["playwright", "install-deps"], check=True)  # For Linux dependencies
        print("Playwright browsers installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"Failed to install Playwright browsers: {e}")

# Call the installation function when starting
install_playwright_browsers()

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
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36 Edg/106.0.1370.52",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36",
    ]
    FIRST_NAMES = [
        "Akira", "Li", "Mohammed", "James", "Maria", "Hiroshi", "Wang", "Ali", "John", "Ana",
        "Yuki", "Zhang", "Fatima", "Robert", "Liza", "Kenji", "Chen", "Aisha", "Michael", "Rosa",
    ]
    LAST_NAMES = [
        "Tanaka", "Li", "Al-Saud", "Smith", "Garcia", "Suzuki", "Wang", "Al-Mansour", "Johnson", "Rodriguez",
        "Yamamoto", "Zhang", "Al-Fahad", "Williams", "Lopez", "Nakamura", "Chen", "Al-Hussein", "Brown", "Martinez",
    ]
    PLAYWRIGHT_OPTIONS = {
        "headless": True,
        "slow_mo": 100,  # Adds delay between actions (more human-like)
        "proxy": None,   # Will be set dynamically
    }

# Helper functions
def generate_random_name(include_last=True):
    first = random.choice(Config.FIRST_NAMES)
    if include_last and random.random() > 0.2:
        last = random.choice(Config.LAST_NAMES)
        return {"first": first, "last": last}
    return {"first": first, "last": ""}

def generate_username(first, last=""):
    random_num = random.randint(1000, 9999)
    first_normalized = unidecode.unidecode(first).lower()
    if last:
        last_normalized = unidecode.unidecode(last).lower()
        return f"{first_normalized}.{last_normalized}{random_num}"
    return f"{first_normalized}{random_num}"

def generate_random_birthday():
    current_year = datetime.now().year
    birth_year = current_year - random.randint(Config.MIN_AGE, Config.MAX_AGE)
    birth_month = random.randint(1, 12)
    birth_day = random.randint(1, 28)
    return f"{birth_month} {birth_day} {birth_year}"

def parse_birthday(bd_param):
    if not bd_param:
        return generate_random_birthday()
    
    separators = ['-', '/', ' ']
    for sep in separators:
        if sep in bd_param:
            parts = bd_param.split(sep)
            if len(parts) == 3:
                try:
                    day, month, year = map(int, parts)
                    if 1 <= day <= 31 and 1 <= month <= 12 and 1900 < year < datetime.now().year - Config.MIN_AGE:
                        return f"{month} {day} {year}"
                except (ValueError, IndexError):
                    continue
    return generate_random_birthday()

def generate_strong_password(length=12):
    chars = string.ascii_letters + string.digits + "!@#$%^&*()"
    while True:
        password = ''.join(random.choice(chars) for _ in range(length))
        if (any(c.isupper() for c in password) and
            any(c.islower() for c in password) and
            any(c.isdigit() for c in password) and
            any(c in "!@#$%^&*()" for c in password)):
            return password

def get_working_proxy():
    try:
        proxy = FreeProxy(rand=True, timeout=1).get()
        if proxy.startswith('http://'):
            proxy = proxy[7:]
        elif proxy.startswith('https://'):
            proxy = proxy[8:]
        return proxy if len(proxy.split(':')) == 2 else None
    except Exception:
        return None

def save_account_to_file(account):
    file_path = Path(__file__).parent / 'accounts.json'
    accounts = []
    if file_path.exists():
        try:
            with open(file_path, 'r') as f:
                accounts = json.load(f)
        except Exception:
            pass
    accounts.append(account)
    with open(file_path, 'w') as f:
        json.dump(accounts, f, indent=2)

def init_playwright_browser():
    proxy = get_working_proxy()
    options = Config.PLAYWRIGHT_OPTIONS.copy()
    if proxy:
        options["proxy"] = {"server": f"http://{proxy}"}
    
    p = sync_playwright().start()
    browser = p.chromium.launch(**options)
    context = browser.new_context(
        user_agent=random.choice(Config.USER_AGENTS),
        viewport={"width": 1280, "height": 720},
        locale="en-US",
        timezone_id="America/New_York",
        # Reduce detection
        permissions=[],
        java_script_enabled=True,
        has_touch=False,
        is_mobile=False,
        # Block resources
        bypass_csp=False,
        no_viewport=False,
        ignore_https_errors=False,
        extra_http_headers={
            "Accept-Language": "en-US,en;q=0.9",
        }
    )
    # Block images/stylesheets to save bandwidth
    context.route("**/*.{png,jpg,jpeg,webp}", lambda route: route.abort())
    context.route("**/*.css", lambda route: route.abort())
    return p, browser, context

# Account creation endpoint
@app.route('/api/create', methods=['GET'])
def create_custom_account():
    start_time = time.time()
    try:
        firstname = request.args.get('firstname', '').strip()
        lastname = request.args.get('lastname', '').strip()
        
        if not firstname:
            name_data = generate_random_name(include_last=False)
            firstname = name_data['first']
            lastname = name_data['last']
        
        account_info = {
            "firstname": firstname,
            "lastname": lastname,
            "birthday": parse_birthday(request.args.get('birthday')),
            "gender": request.args.get('gender', Config.DEFAULT_GENDER).lower(),
            "username": request.args.get('username') or generate_username(firstname, lastname),
            "password": request.args.get('password', generate_strong_password()),
        }
        account_info["email"] = f"{account_info['username']}@gmail.com"
        account_info["name"] = f"{firstname} {lastname}".strip()

        result = create_account_with_playwright(account_info)
        save_account_to_file(result)

        return jsonify({
            "success": True,
            "data": {"account": result},
            "meta": {"duration": f"{(time.time() - start_time):.2f} seconds"}
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# Random account creation endpoint
@app.route('/api/create/random', methods=['GET'])
def create_random_accounts():
    start_time = time.time()
    try:
        limit = min(request.args.get('limit', default=1, type=int), Config.MAX_RANDOM_ACCOUNTS)
        accounts = []
        errors = []
        
        for i in range(limit):
            try:
                name_data = generate_random_name(include_last=True)
                account_info = {
                    "firstname": name_data['first'],
                    "lastname": name_data['last'],
                    "birthday": generate_random_birthday(),
                    "gender": random.choice(["male", "female"]),
                    "username": generate_username(name_data['first'], name_data['last']),
                    "password": generate_strong_password(),
                }
                account_info["email"] = f"{account_info['username']}@gmail.com"
                account_info["name"] = f"{name_data['first']} {name_data['last']}".strip()

                result = create_account_with_playwright(account_info)
                accounts.append(result)
                save_account_to_file(result)
            except Exception as e:
                errors.append({"attempt": i + 1, "error": str(e)})

        return jsonify({
            "success": True,
            "meta": {
                "requested": limit,
                "created": len(accounts),
                "failed": len(errors),
                "duration": f"{(time.time() - start_time):.2f} seconds"
            },
            "data": {"accounts": accounts},
            "errors": errors or None
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

def create_account_with_playwright(account_info):
    playwright, browser, context = None, None, None
    try:
        playwright, browser, context = init_playwright_browser()
        page = context.new_page()
        device_uuid = str(uuid.uuid4())

        # Step 1: Name entry
        page.goto("https://accounts.google.com/signup/v2/createaccount?flowName=GlifWebSignIn&flowEntry=SignUp")
        page.fill('input[name="firstName"]', account_info['firstname'])
        page.fill('input[name="lastName"]', account_info['lastname'])
        page.click('button:has-text("Next")')

        # Step 2: Birthday and gender
        month, day, year = account_info['birthday'].split()
        page.select_option('select#month', value=month)
        page.fill('input#day', day)
        page.fill('input#year', year)
        gender_value = "1" if account_info['gender'] == "male" else "2"
        page.select_option('select#gender', value=gender_value)
        page.click('button:has-text("Next")')

        # Step 3: Custom email
        try:
            page.click('div:has-text("Create your own Gmail address")', timeout=3000)
        except:
            pass
        page.fill('input[name="Username"]', account_info['username'])
        page.click('button:has-text("Next")')

        # Step 4: Password
        page.fill('input[name="Passwd"]', account_info['password'])
        page.fill('input[name="PasswdAgain"]', account_info['password'])
        page.click('button:has-text("Next")')

        # Step 5: Skip phone verification
        try:
            page.click('button:has-text("Skip")', timeout=3000)
        except:
            pass

        # Step 6: Agree to terms
        page.click('button:has-text("I agree")')

        # Verify completion
        page.wait_for_url("**/myaccount.google.com/**", timeout=30000)

        return {
            **account_info,
            "status": "created",
            "timestamp": datetime.now().isoformat(),
            "deviceId": device_uuid
        }
    except Exception as e:
        raise Exception(f"Account creation failed: {str(e)}")
    finally:
        if context:
            context.close()
        if browser:
            browser.close()
        if playwright:
            playwright.stop()

# Health check endpoint
@app.route('/', methods=['GET'])
def health_check():
    return jsonify({
        "status": "running",
        "service": "Gmail Account Creator API (Playwright)",
        "version": "2.0.0",
        "endpoints": {
            "/api/create": "Create custom account",
            "/api/create/random": f"Create random accounts (max {Config.MAX_RANDOM_ACCOUNTS})"
        }
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT)
