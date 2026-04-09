import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Email Configuration
SMTP_HOST = "smtp.gmail.com"  # Change to your SMTP server
SMTP_PORT = 587
SMTP_USER = "your-email@gmail.com"  # Change to your email
SMTP_PASSWORD = "your-app-password"  # Use app-specific password
FROM_EMAIL = "noreply@skylink-airlines.com"
FROM_NAME = "SkyLink Airlines"

async def send_email(to_email: str, subject: str, html_content: str):
    """
    Send email using SMTP
    For development: prints email to console
    For production: actually sends email
    """
    
    # FOR DEVELOPMENT: Just print to console
    print("=" * 50)
    print("📧 EMAIL NOTIFICATION")
    print("=" * 50)
    print(f"To: {to_email}")
    print(f"Subject: {subject}")
    print(f"Content:\n{html_content}")
    print("=" * 50)
    
    # UNCOMMENT FOR PRODUCTION EMAIL SENDING:
    """
    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = f"{FROM_NAME} <{FROM_EMAIL}>"
    message["To"] = to_email
    
    html_part = MIMEText(html_content, "html")
    message.attach(html_part)
    
    try:
        await aiosmtplib.send(
            message,
            hostname=SMTP_HOST,
            port=SMTP_PORT,
            username=SMTP_USER,
            password=SMTP_PASSWORD,
            start_tls=True,
        )
        print(f"✅ Email sent to {to_email}")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
    """

async def send_verification_email(to_email: str, token: str, user_name: str):
    """Send email verification link"""
    verification_link = f"http://127.0.0.1:8000/verify-email?token={token}"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px; }}
            .container {{ background: white; padding: 30px; border-radius: 10px; max-width: 600px; margin: 0 auto; }}
            .header {{ background: linear-gradient(135deg, #667eea, #764ba2); color: white; padding: 20px; text-align: center; border-radius: 10px 10px 0 0; }}
            .content {{ padding: 20px; }}
            .button {{ background: #667eea; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; display: inline-block; margin: 20px 0; }}
            .footer {{ text-align: center; color: #666; margin-top: 30px; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>✈️ Welcome to SkyLink Airlines!</h1>
            </div>
            <div class="content">
                <h2>Hello {user_name},</h2>
                <p>Thank you for registering with SkyLink Airlines!</p>
                <p>Please verify your email address by clicking the button below:</p>
                <a href="{verification_link}" class="button">Verify Email Address</a>
                <p>Or copy this link: <br><code>{verification_link}</code></p>
                <p>This link will expire in 24 hours.</p>
            </div>
            <div class="footer">
                <p>© 2024 SkyLink Airlines. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    await send_email(to_email, "Verify Your Email - SkyLink Airlines", html_content)

async def send_password_reset_email(to_email: str, token: str, user_name: str):
    """Send password reset link"""
    reset_link = f"http://127.0.0.1:8000/reset-password?token={token}"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px; }}
            .container {{ background: white; padding: 30px; border-radius: 10px; max-width: 600px; margin: 0 auto; }}
            .header {{ background: linear-gradient(135deg, #667eea, #764ba2); color: white; padding: 20px; text-align: center; border-radius: 10px 10px 0 0; }}
            .content {{ padding: 20px; }}
            .button {{ background: #667eea; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; display: inline-block; margin: 20px 0; }}
            .footer {{ text-align: center; color: #666; margin-top: 30px; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🔐 Password Reset Request</h1>
            </div>
            <div class="content">
                <h2>Hello {user_name},</h2>
                <p>We received a request to reset your password.</p>
                <p>Click the button below to reset your password:</p>
                <a href="{reset_link}" class="button">Reset Password</a>
                <p>Or copy this link: <br><code>{reset_link}</code></p>
                <p>This link will expire in 1 hour.</p>
                <p><strong>If you didn't request this, please ignore this email.</strong></p>
            </div>
            <div class="footer">
                <p>© 2024 SkyLink Airlines. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    await send_email(to_email, "Password Reset - SkyLink Airlines", html_content)