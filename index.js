require('geckodriver');
const express = require('express');
const { Builder, By, until } = require('selenium-webdriver');
const firefox = require('selenium-webdriver/firefox');
const { Select } = require('selenium-webdriver/lib/select');
const unidecode = require('unidecode');
const { v4: uuidv4 } = require('uuid');
const FreeProxy = require('fp-free-proxy');
const cors = require('cors');
const bodyParser = require('body-parser');
const fs = require('fs');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 11000;

// Middleware
app.use(cors());
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));

// Configuration
const CONFIG = {
    MAX_RANDOM_ACCOUNTS: 10,
    DEFAULT_BIRTHDAY: "17 10 2000",
    DEFAULT_GENDER: "1",
    DEFAULT_PASSWORD: "SecurePass123!",
    USER_AGENTS: [
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
    "Mozilla/5.0 (X11; CrOS x86_64 14440.0.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4807.0 Safari/537.36",
    "Mozilla/5.0 (X11; CrOS x86_64 14467.0.2022) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4838.0 Safari/537.36",
    "Mozilla/5.0 (X11; CrOS x86_64 14469.7.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.13 Safari/537.36",
    "Mozilla/5.0 (X11; CrOS x86_64 14455.0.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4827.0 Safari/537.36",
    "Mozilla/5.0 (X11; CrOS x86_64 14469.11.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.17 Safari/537.36",
    "Mozilla/5.0 (X11; CrOS x86_64 14436.0.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4803.0 Safari/537.36",
    "Mozilla/5.0 (X11; CrOS x86_64 14475.0.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4840.0 Safari/537.36",
    "Mozilla/5.0 (X11; CrOS x86_64 14469.3.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.9 Safari/537.36",
    "Mozilla/5.0 (X11; CrOS x86_64 14471.0.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4840.0 Safari/537.36",
    "Mozilla/5.0 (X11; CrOS x86_64 14388.37.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.9 Safari/537.36",
    "Mozilla/5.0 (X11; CrOS x86_64 14409.0.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4829.0 Safari/537.36",
    "Mozilla/5.0 (X11; CrOS x86_64 14395.0.2021) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4765.0 Safari/537.36",
    "Mozilla/5.0 (X11; CrOS x86_64 14469.8.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.14 Safari/537.36",
    "Mozilla/5.0 (X11; CrOS x86_64 14484.0.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4840.0 Safari/537.36",
    "Mozilla/5.0 (X11; CrOS x86_64 14450.0.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4817.0 Safari/537.36",
    "Mozilla/5.0 (X11; CrOS x86_64 14473.0.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4840.0 Safari/537.36",
    "Mozilla/5.0 (X11; CrOS x86_64 14324.72.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.91 Safari/537.36",
    "Mozilla/5.0 (X11; CrOS x86_64 14454.0.2022) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4824.0 Safari/537.36",
    "Mozilla/5.0 (X11; CrOS x86_64 14453.0.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4816.0 Safari/537.36",
    "Mozilla/5.0 (X11; CrOS x86_64 14447.0.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4815.0 Safari/537.36",
    "Mozilla/5.0 (X11; CrOS x86_64 14477.0.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4840.0 Safari/537.36",
    "Mozilla/5.0 (X11; CrOS x86_64 14476.0.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4840.0 Safari/537.36",
    "Mozilla/5.0 (X11; CrOS x86_64 14469.8.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.9 Safari/537.36",
    "Mozilla/5.0 (X11; CrOS x86_64 14588.67.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.41 Safari/537.36",
    "Mozilla/5.0 (X11; CrOS x86_64 14588.67.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; CrOS x86_64 14526.69.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.82 Safari/537.36",
    "Mozilla/5.0 (X11; CrOS x86_64 14695.25.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.22 Safari/537.36",
    "Mozilla/5.0 (X11; CrOS x86_64 14526.89.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.91 Safari/537.36"
    ],
    FIRST_NAMES: [
        "Akira", "Li", "Mohammed", "James", "Maria", "Hiroshi", "Wang", "Ali", "John", "Ana",
  "Yuki", "Zhang", "Fatima", "Robert", "Liza", "Kenji", "Chen", "Aisha", "Michael", "Rosa",
  "Haruto", "Huang", "Zainab", "David", "Carla", "Sakura", "Lin", "Omar", "William", "Gloria",
  "Takeshi", "Cheng", "Salma", "Joseph", "Isabel", "Yoshio", "Deng", "Nadia", "Richard", "Sofia",
  "Ryu", "Feng", "Samir", "Charles", "Valentina", "Emi", "Zhao", "Amira", "Thomas", "Mia",
  "Kaito", "Sun", "Karim", "Christopher", "Luna", "Hana", "Qian", "Layla", "Daniel", "Sophia",
  "Satoru", "Wu", "Nour", "Matthew", "Isabella", "Tsubasa", "Xu", "Aya", "George", "Emma",
  "Haruki", "Zhu", "Yasmine", "Anthony", "Olivia", "Arata", "Jiang", "Samira", "Mark", "Maya",
  "Kazuki", "Hu", "Rania", "Steven", "Ariana", "Noboru", "Gao", "Leila", "Paul", "Grace",
  "Shinji", "Cai", "Amal", "Andrew", "Victoria", "Ren", "Dong", "Khadija", "James", "Natalie",
  "Tatsuya", "Lin", "Ibrahim", "Daniel", "Lila", "Yuto", "Xie", "Aaliyah", "Henry", "Zoe",
  "Hiroki", "Liang", "Malik", "Ethan", "Mila", "Daiki", "Peng", "Nour", "Jacob", "Chloe"
    ],
    LAST_NAMES: [
        "Tanaka", "Li", "Al-Saud", "Smith", "Garcia", "Suzuki", "Wang", "Al-Mansour", "Johnson", "Rodriguez",
  "Yamamoto", "Zhang", "Al-Fahad", "Williams", "Lopez", "Nakamura", "Chen", "Al-Hussein", "Brown", "Martinez",
  "Sato", "Huang", "Al-Ghamdi", "Jones", "Gonzalez", "Takahashi", "Lin", "Al-Jaber", "Davis", "Sanchez",
  "Kobayashi", "Wong", "Al-Sharif", "Miller", "Torres", "Yamada", "Cheng", "Al-Khateeb", "Wilson", "Flores",
  "Ito", "Feng", "Al-Qahtani", "Taylor", "Nguyen", "Kimura", "Zhao", "Al-Dossary", "Anderson", "Kim",
  "Saito", "Sun", "Al-Tamimi", "Thomas", "Singh", "Matsumoto", "Xu", "Al-Hamad", "Jackson", "Lee",
  "Inoue", "Zhu", "Al-Sheikh", "White", "Campbell", "Hayashi", "Jiang", "Al-Mutairi", "Harris", "Clark",
  "Watanabe", "Hu", "Al-Ansari", "Lewis", "Robinson", "Nakagawa", "Cai", "Al-Rashid", "Walker", "Young",
  "Tsukamoto", "Deng", "Al-Harbi", "Green", "Reed", "Fujita", "Peng", "Al-Masri", "Hall", "King",
  "Kato", "Lin", "Al-Mohammed", "Adams", "Carter", "Yamaguchi", "Gao", "Al-Dhaheri", "Nelson", "Baker",
  "Ueda", "Liang", "Al-Mutlaq", "Mitchell", "Collins", "Kondo", "Xie", "Al-Juhani", "King", "Perez"
    ]
};

// Helper functions
function generateRandomName() {
    const first = CONFIG.FIRST_NAMES[Math.floor(Math.random() * CONFIG.FIRST_NAMES.length)];
    const last = CONFIG.LAST_NAMES[Math.floor(Math.random() * CONFIG.LAST_NAMES.length)];
    return { first, last };
}

function generateUsername(first, last) {
    const randomNum = Math.floor(1000 + Math.random() * 9000);
    const firstNormalized = unidecode(first).toLowerCase();
    const lastNormalized = unidecode(last).toLowerCase();
    return `${firstNormalized}.${lastNormalized}${randomNum}`;
}

function parseBirthday(bdParam) {
    // Handle various date formats: 15-5-1995, 15/5/1995, 15 5 1995
    const formats = [
        { regex: /^(\d{1,2})[-/ ](\d{1,2})[-/ ](\d{4})$/, parts: [1, 2, 3] },
        { regex: /^(\d{4})[-/ ](\d{1,2})[-/ ](\d{1,2})$/, parts: [3, 2, 1] }
    ];

    for (const format of formats) {
        const match = bdParam.match(format.regex);
        if (match) {
            return `${match[format.parts[0]]} ${match[format.parts[1]]} ${match[format.parts[2]]}`;
        }
    }
    
    return CONFIG.DEFAULT_BIRTHDAY;
}

async function getWorkingProxy() {
    try {
        const proxy = new FreeProxy({ random: true, timeout: 1000 }).get();
        console.log(`Using proxy: ${proxy}`);
        return proxy;
    } catch (error) {
        console.log("Failed to get proxy, continuing without proxy");
        return null;
    }
}

function saveAccountToFile(account) {
    const filePath = path.join(__dirname, 'accounts.json');
    let accounts = [];
    
    try {
        if (fs.existsSync(filePath)) {
            accounts = JSON.parse(fs.readFileSync(filePath, 'utf8'));
        }
    } catch (err) {
        console.error("Error reading accounts file:", err);
    }
    
    accounts.push(account);
    fs.writeFileSync(filePath, JSON.stringify(accounts, null, 2));
}

// Custom account creation endpoint
app.get('/api/create', async (req, res) => {
    const startTime = Date.now();
    
    try {
        // Parse query parameters with fallbacks
        const name = req.query.name || (() => {
            const { first, last } = generateRandomName();
            return `${first} ${last}`;
        })();
        
        const birthday = req.query.birthday ? parseBirthday(req.query.birthday) : CONFIG.DEFAULT_BIRTHDAY;
        const gender = req.query.gender || CONFIG.DEFAULT_GENDER;
        const username = req.query.username || name.toLowerCase().replace(/\s+/g, '.') + Math.floor(100 + Math.random() * 900);
        const password = req.query.password || CONFIG.DEFAULT_PASSWORD;

        const accountInfo = {
            name,
            birthday,
            gender: gender === "1" ? "male" : "female",
            username,
            email: `${username}@gmail.com`,
            password
        };

        const result = await createAccount(accountInfo);
        saveAccountToFile(result);

        res.json({
            success: true,
            data: {
                account: result
            },
            meta: {
                duration: `${(Date.now() - startTime) / 1000} seconds`,
                method: "custom"
            }
        });
    } catch (error) {
        console.error("API Error:", error);
        res.status(500).json({
            success: false,
            error: "Internal server error",
            details: error.message
        });
    }
});

// Random account creation endpoint
app.get('/api/create/random', async (req, res) => {
    const startTime = Date.now();
    
    try {
        const limit = Math.min(
            parseInt(req.query.limit) || 1,
            CONFIG.MAX_RANDOM_ACCOUNTS
        );

        const accounts = [];
        const errors = [];
        
        for (let i = 0; i < limit; i++) {
            try {
                const { first, last } = generateRandomName();
                const username = generateUsername(first, last);
                
                const accountInfo = {
                    name: `${first} ${last}`,
                    birthday: CONFIG.DEFAULT_BIRTHDAY,
                    gender: Math.random() > 0.5 ? "male" : "female",
                    username,
                    email: `${username}@gmail.com`,
                    password: CONFIG.DEFAULT_PASSWORD
                };

                const result = await createAccount(accountInfo);
                accounts.push(result);
                saveAccountToFile(result);
            } catch (error) {
                errors.push({
                    attempt: i + 1,
                    error: error.message
                });
            }
        }

        const response = {
            success: true,
            meta: {
                requested: limit,
                created: accounts.length,
                failed: errors.length,
                duration: `${(Date.now() - startTime) / 1000} seconds`,
                method: "random"
            },
            data: {
                accounts: accounts.reduce((acc, account, index) => {
                    acc[index + 1] = account;
                    return acc;
                }, {})
            },
            errors: errors.length > 0 ? errors : undefined
        };

        res.json(response);
    } catch (error) {
        console.error("API Error:", error);
        res.status(500).json({
            success: false,
            error: "Internal server error",
            details: error.message
        });
    }
});

// Function to create a single account
async function createAccount(accountInfo) {
    let driver;
    try {
        const options = new firefox.Options();
        options.headless();
        options.setPreference("general.useragent.override", 
            CONFIG.USER_AGENTS[Math.floor(Math.random() * CONFIG.USER_AGENTS.length)]);

        // Configure proxy if available
        const proxy = await getWorkingProxy();
        if (proxy) {
            const [host, port] = proxy.split(':');
            options.setPreference('network.proxy.type', 1);
            options.setPreference('network.proxy.http', host);
            options.setPreference('network.proxy.http_port', parseInt(port));
            options.setPreference('network.proxy.ssl', host);
            options.setPreference('network.proxy.ssl_port', parseInt(port));
        }

        driver = await new Builder()
            .forBrowser('firefox')
            .setFirefoxOptions(options)
            .build();

        const device_uuid = uuidv4();
        console.log(`Creating account for ${accountInfo.email} with UUID: ${device_uuid}`);

        await driver.get("https://accounts.google.com/signup/v2/createaccount?flowName=GlifWebSignIn&flowEntry=SignUp");

        // Fill in the name fields
        const firstName = await driver.wait(until.elementLocated(By.name("firstName")), 10000);
        const lastName = await driver.findElement(By.name("lastName"));
        await firstName.clear();
        await firstName.sendKeys(accountInfo.name.split(' ')[0]);
        await lastName.clear();
        await lastName.sendKeys(accountInfo.name.split(' ')[1]);

        const nextButton = await driver.wait(until.elementLocated(By.xpath("//span[text()='Next']")), 10000);
        await nextButton.click();

        // Fill birthday and gender
        const birthdayElements = accountInfo.birthday.split(' ');
        const monthDropdown = new Select(await driver.findElement(By.id("month")));
        await monthDropdown.selectByValue(birthdayElements[1]);
        
        const dayField = await driver.findElement(By.id("day"));
        await dayField.clear();
        await dayField.sendKeys(birthdayElements[0]);
        
        const yearField = await driver.findElement(By.id("year"));
        await yearField.clear();
        await yearField.sendKeys(birthdayElements[2]);
        
        const genderDropdown = new Select(await driver.findElement(By.id("gender")));
        await genderDropdown.selectByValue(accountInfo.gender === "male" ? "1" : "2");
        
        const nextButton2 = await driver.wait(until.elementLocated(By.xpath("//span[text()='Next']")), 10000);
        await nextButton2.click();

        // Create custom email
        await driver.sleep(2000);
        try {
            const createOwnOption = await driver.wait(until.elementLocated(By.xpath("//div[contains(text(), 'Create your own Gmail address')]")), 5000);
            await createOwnOption.click();
        } catch (error) {
            console.log("No 'Create your own' option found");
        }

        const usernameField = await driver.wait(until.elementLocated(By.name("Username")), 10000);
        await usernameField.clear();
        await usernameField.sendKeys(accountInfo.username);
        
        const nextButton3 = await driver.wait(until.elementLocated(By.xpath("//span[text()='Next']")), 10000);
        await nextButton3.click();

        // Enter and confirm password
        const passwordField = await driver.wait(until.elementLocated(By.name("Passwd")), 10000);
        await passwordField.clear();
        await passwordField.sendKeys(accountInfo.password);
        
        const confirmPasswd = await driver.wait(until.elementLocated(By.name("PasswdAgain")), 10000);
        await confirmPasswd.clear();
        await confirmPasswd.sendKeys(accountInfo.password);
        
        const nextButton4 = await driver.wait(until.elementLocated(By.xpath("//span[text()='Next']")), 10000);
        await nextButton4.click();

        // Skip phone number and recovery email
        try {
            const skipButton = await driver.wait(until.elementLocated(By.xpath("//span[contains(text(),'Skip')]")), 5000);
            await skipButton.click();
        } catch (error) {
            console.log("No phone number verification step");
        }

        // Agree to terms
        const agreeButton = await driver.wait(until.elementLocated(By.xpath("//span[text()='I agree']")), 10000);
        await agreeButton.click();

        // Wait for account creation to complete
        await driver.wait(until.urlContains("myaccount.google.com"), 30000);

        return {
            ...accountInfo,
            status: "created",
            timestamp: new Date().toISOString(),
            deviceId: device_uuid
        };
    } catch (error) {
        console.error("Account creation failed:", error);
        throw new Error(`Failed to create account ${accountInfo.email}: ${error.message}`);
    } finally {
        if (driver) {
            try {
                await driver.quit();
            } catch (error) {
                console.error("Error closing driver:", error);
            }
        }
    }
}

// Get all created accounts
app.get('/api/accounts', (req, res) => {
    try {
        const filePath = path.join(__dirname, 'accounts.json');
        if (fs.existsSync(filePath)) {
            const accounts = JSON.parse(fs.readFileSync(filePath, 'utf8'));
            return res.json({
                success: true,
                count: accounts.length,
                data: {
                    accounts
                }
            });
        }
        res.json({
            success: true,
            count: 0,
            data: {
                accounts: []
            }
        });
    } catch (error) {
        res.status(500).json({
            success: false,
            error: "Failed to read accounts data"
        });
    }
});

// Health check endpoint
app.get('/', (req, res) => {
    res.json({
        status: 'running',
        service: 'Gmail Account Creator API',
        version: '1.1.0',
        endpoints: {
            createCustom: {
                method: 'GET',
                path: '/api/create',
                description: 'Create custom Gmail account',
                parameters: {
                    name: 'Full name (optional)',
                    birthday: 'Birthday in format "DD-MM-YYYY", "DD/MM/YYYY", or "DD MM YYYY" (optional)',
                    gender: 'Gender ("1" for male, "2" for female) (optional)',
                    username: 'Desired username (optional)',
                    password: 'Password for the account (optional)'
                },
                example: '/api/create?name=John+Doe&birthday=15-5-1995&gender=1&username=johndoe.alpha&password=Str0ngP@ss'
            },
            createRandom: {
                method: 'GET',
                path: '/api/create/random',
                description: `Create random Gmail accounts (max ${CONFIG.MAX_RANDOM_ACCOUNTS})`,
                parameters: {
                    limit: 'Number of accounts to create (optional, default 1)'
                },
                example: '/api/create/random?limit=3'
            },
            getAccounts: {
                method: 'GET',
                path: '/api/accounts',
                description: 'Get all created accounts'
            }
        }
    });
});

// Start the server
app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
    console.log('Available endpoints:');
    console.log(`- Custom account: GET /api/create?name=John&birthday=15-5-1995&gender=1&username=john123&password=pass123`);
    console.log(`- Random accounts: GET /api/create/random?limit=3`);
    console.log(`- List accounts: GET /api/accounts`);
});