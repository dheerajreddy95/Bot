import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

def send_email(new_jobs):
    """
    Sends an email notification with the list of new jobs.
    Returns True if email was sent successfully, False otherwise.
    """
    sender_email = os.environ.get("EMAIL_ADDRESS")
    sender_password = os.environ.get("EMAIL_PASSWORD")
    receiver_email = os.environ.get("NOTIFY_EMAIL")

    # Validate configuration
    if not sender_email:
        print("⚠ Missing EMAIL_ADDRESS environment variable")
        return False
    if not sender_password:
        print("⚠ Missing EMAIL_PASSWORD environment variable")
        return False
    if not receiver_email:
        print("⚠ Missing NOTIFY_EMAIL environment variable")
        return False

    print(f"Preparing email to {receiver_email}...")
    print(f"Number of new jobs to notify: {len(new_jobs)}")

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"🚀 {len(new_jobs)} New Microsoft Job(s) Found!"
    msg["From"] = sender_email
    msg["To"] = receiver_email

    # HTML Body
    html_content = """
    <html>
    <head>
        <style>
            body { 
                font-family: 'Segoe UI', Arial, sans-serif; 
                background-color: #f5f5f5;
                margin: 0;
                padding: 20px;
            }
            .container {
                max-width: 600px;
                margin: 0 auto;
                background-color: #ffffff;
                border-radius: 8px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                overflow: hidden;
            }
            .header {
                background: linear-gradient(135deg, #0078d4 0%, #00bcf2 100%);
                color: white;
                padding: 24px;
                text-align: center;
            }
            .header h1 {
                margin: 0;
                font-size: 24px;
            }
            .content {
                padding: 24px;
            }
            .job-card { 
                border: 1px solid #e1e1e1; 
                padding: 16px; 
                margin-bottom: 16px; 
                border-radius: 8px;
                background-color: #fafafa;
                transition: all 0.2s ease;
            }
            .job-card:hover {
                border-color: #0078d4;
                box-shadow: 0 2px 4px rgba(0,120,212,0.1);
            }
            .job-title { 
                color: #0078d4; 
                font-size: 18px; 
                font-weight: 600; 
                margin: 0 0 8px 0;
            }
            .job-location { 
                color: #666; 
                font-size: 14px; 
                margin: 4px 0 12px 0;
            }
            .apply-btn {
                display: inline-block;
                background-color: #0078d4;
                color: white !important;
                padding: 10px 20px;
                text-decoration: none;
                border-radius: 4px;
                font-weight: 500;
                font-size: 14px;
            }
            .apply-btn:hover {
                background-color: #106ebe;
            }
            .footer {
                background-color: #f5f5f5;
                padding: 16px 24px;
                text-align: center;
                font-size: 12px;
                color: #888;
                border-top: 1px solid #e1e1e1;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🎯 New Microsoft Jobs Alert!</h1>
                <p style="margin: 8px 0 0 0; opacity: 0.9;">""" + f"{len(new_jobs)} new position{'s' if len(new_jobs) > 1 else ''} matching your criteria" + """</p>
            </div>
            <div class="content">
    """

    for job in new_jobs:
        title = job.get('title', 'Unknown Role')
        location = job.get('location', 'Unknown Location')
        link = job.get('link', '#')
        
        html_content += f"""
            <div class="job-card">
                <h3 class="job-title">{title}</h3>
                <p class="job-location">📍 {location}</p>
                <a href="{link}" class="apply-btn">View Job →</a>
            </div>
        """

    html_content += """
            </div>
            <div class="footer">
                <p>This email was sent by your Microsoft Job Alert Bot.</p>
                <p>Powered by automated job monitoring 🤖</p>
            </div>
        </div>
    </body>
    </html>
    """

    msg.attach(MIMEText(html_content, "html"))

    try:
        print(f"Connecting to {SMTP_SERVER}:{SMTP_PORT}...")
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        
        print("Authenticating...")
        server.login(sender_email, sender_password)
        
        print("Sending email...")
        server.sendmail(sender_email, receiver_email, msg.as_string())
        server.quit()
        
        print(f"✓ Email sent successfully to {receiver_email}")
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        print(f"❌ Authentication failed: {e}")
        print("   Make sure you're using an App Password (not your regular Gmail password)")
        print("   Generate one at: https://myaccount.google.com/apppasswords")
        return False
    except smtplib.SMTPException as e:
        print(f"❌ SMTP error: {e}")
        return False
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
        return False
