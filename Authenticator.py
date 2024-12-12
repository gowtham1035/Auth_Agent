import os
import random
from flask import Flask, request, jsonify
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from passwords import *

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Connection string (Use your full Supabase connection string)
DB_CONNECTION_STRING = 'postgresql://postgres.galoagmfzuficlijofeu:korehyd1@aws-0-ap-south-1.pooler.supabase.com:6543/postgres'

# SQLAlchemy setup
Base = declarative_base()
engine = create_engine(DB_CONNECTION_STRING)  # Using the provided connection string
Session = sessionmaker(bind=engine)

# Define the OTP table using SQLAlchemy ORM
class OTPRecord(Base):
    __tablename__ = 'otp_records'

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), nullable=False)
    otp = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime)

# Create OTP table if it doesn't exist
def create_otp_table():
    Base.metadata.create_all(engine)

# Function to generate 6-digit OTP
def generate_otp():
    otp = random.randint(100000, 999999)
    return otp

# Route to send email with OTP
# Route to send email with OTP
from flask import jsonify

@app.route('/', methods=['GET'])
def send_email():
    # Retrieve email from query parameters
    to_email = request.args.get('email')  # Get email from query parameter
    if not to_email:
        return jsonify({"error": "Email parameter is missing"}), 400

    otp = generate_otp()  # Generate OTP
    from_email = email  # Replace with your email
    from_password = password  # Replace with your email password

    # Set up the MIME
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = 'Your Authenticating OTP Code'

    # Add OTP to the email body
    body = f"Your 6-digit OTP code is: {otp}"
    msg.attach(MIMEText(body, 'plain'))

    # Save or update the OTP in the database
    try:
        session = Session()  # Create session
        
        # Check if the email already exists in the database
        existing_record = session.query(OTPRecord).filter_by(email=to_email).first()
        
        if existing_record:
            # Update the existing record with the new OTP
            existing_record.otp = otp
            existing_record.created_at = datetime.now()  # Update timestamp
            print(f"Updated OTP for email: {to_email}")
        else:
            # Create a new record if it doesn't exist
            otp_record = OTPRecord(email=to_email, otp=otp)
            session.add(otp_record)
            print(f"Added new OTP for email: {to_email}")
        
        session.commit()  # Commit the transaction
        session.close()  # Close the session
    except Exception as e:
        return jsonify({"error": f"Error saving OTP to database: {e}"}), 500

    # Send the OTP via email
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(from_email, from_password)
        text = msg.as_string()
        server.sendmail(from_email, to_email, text)
        server.quit()

        return jsonify({"message": f"OTP sent successfully to {to_email}!"}), 200
    except Exception as e:
        return jsonify({"error": f"Error: {e}"}), 500

@app.route('/validate', methods=['GET'])
def validate_otp():
    # Retrieve email and OTP from query parameters
    to_email = request.args.get('email')  # Get email from query parameter
    entered_otp = int(request.args.get('otp'))  # Get OTP from query parameter

    # Validate inputs
    if not to_email or not entered_otp:
        return {"error": "Missing email or OTP in the request."}, 400

    try:
        session = Session()  # Create session

        # Query the database for the given email
        otp_record = session.query(OTPRecord).filter_by(email=to_email).first()

        if not otp_record:
            session.close()  # Close session if no record is found
            return {"error": "Email not found."}, 404

        # Check if the entered OTP matches the stored OTP
        if otp_record.otp == entered_otp:
            response = {
                "message": "Your OTP is correct. Welcome to the chatbot app!",
                "email": otp_record.email
            }
            session.close()  # Close the session
            return response, 200

        # OTP does not match
        session.close()  # Close the session
        return {"error": "Invalid OTP. Please try again."}, 401

    except Exception as e:
        return {"error": f"Error retrieving OTP from database: {e}"}, 500




if __name__ == '__main__':
    # Create OTP table when app starts
    create_otp_table()
    app.run(debug=True)