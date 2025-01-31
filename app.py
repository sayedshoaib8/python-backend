import random
import smtplib
import string
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import Flask, render_template, request, redirect, url_for, session
import os

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'your_default_secret_key')

# In-memory user database (for demonstration purposes)
users = {}

# Function to generate OTP
def generate_otp(length=6):
    characters = string.digits  # OTP will only contain numbers
    otp = ''.join(random.choice(characters) for i in range(length))
    return otp

# Function to send email with OTP
def send_email(recipient_email, otp):
    sender_email = os.environ.get('SENDER_EMAIL', 'pa3869224@gmail.com')  # Use env variable for sender email
    sender_password = os.environ.get('SENDER_PASSWORD', "zgadvpeucnkzqlgu")  # Use app password for Gmail

    # Setting up the MIME
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = 'Your OTP Code'

    # HTML email body
    body = f"""
    <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    background-color: #f7f7f7;
                    color: #333;
                    margin: 0;
                    padding: 0;
                }}
                .container {{
                    width: 100%;
                    max-width: 600px;
                    margin: 0 auto;
                    background-color: #ffffff;
                    border-radius: 8px;
                    padding: 20px;
                    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
                }}
                .header {{
                    background-color: #007bff;
                    color: #ffffff;
                    padding: 10px 20px;
                    text-align: center;
                    font-size: 24px;
                    border-radius: 8px 8px 0 0;
                }}
                .otp {{
                    font-size: 36px;
                    font-weight: bold;
                    color: #007bff;
                    text-align: center;
                    margin-top: 20px;
                }}
                .footer {{
                    text-align: center;
                    margin-top: 20px;
                    font-size: 14px;
                    color: #888;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    OTP Verification
                </div>
                <div class="body">
                    <p>Hi,</p>
                    <p>Here is your OTP code:</p>
                    <div class="otp">{otp}</div>
                    <p>Please enter this code to complete your verification.</p>
                </div>
                <div class="footer">
                    <p>If you didn't request this OTP, please ignore this email.</p>
                    <p>Thank you for using our service!</p>
                </div>
            </div>
        </body>
    </html>
    """
    
    msg.attach(MIMEText(body, 'html'))

    # Setting up the server
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()  # Encrypt the connection
    server.login(sender_email, sender_password)

    # Send the email
    text = msg.as_string()
    server.sendmail(sender_email, recipient_email, text)
    server.quit()

@app.route('/')
def home():
    return render_template('signup.html')

@app.route('/signup', methods=['POST'])
def signup():
    username = request.form['username']
    email = request.form['email']
    password = request.form['password']
    
    # Check if username or email already exists
    if username in users:
        return "Username already taken. Please try a different one."
    
    # Save user info (just for demonstration, normally this would be a database)
    users[username] = {'email': email, 'password': password}
    
    # Generate OTP
    otp = generate_otp()

    # Send OTP to the email
    send_email(email, otp)

    # Store OTP and user info in session for later verification
    session['otp'] = otp
    session['username'] = username
    session['email'] = email

    # Redirect to OTP verification page
    return redirect(url_for('verify_otp'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Check if the username exists and password matches
        user = users.get(username)
        if user and user['password'] == password:
            session['logged_in'] = True
            session['username'] = username
            return f"Welcome back, {username}!"
        else:
            return "Invalid credentials. Please try again."

    return render_template('login.html')

@app.route('/verify-otp', methods=['GET', 'POST'])
def verify_otp():
    if request.method == 'POST':
        entered_otp = request.form['otp']
        # Compare the entered OTP with the one stored in session
        if entered_otp == session.get('otp'):
            return f"OTP verified successfully for {session.get('email')}"
        else:
            return "Invalid OTP, please try again."

    return render_template('verify_otp.html')

if __name__ == '__main__':
    app.run(debug=True)
