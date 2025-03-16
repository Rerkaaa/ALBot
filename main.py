# Third-party imports
from fastapi import FastAPI, Form, Depends
from decouple import config
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from datetime import datetime
import os

# Internal imports
from models import Conversation, Booking, SessionLocal
from utils import logger, send_message

app = FastAPI()

whatsapp_number = config("TO_NUMBER")

faqs = {
    "check-in": "Check-in is 2 PM, check-out is 11 AM. Need a late check-out? Reply ‘late’ for options.",
    "beach": "We’re 200 meters from the beach—a quick 3-minute walk!",
    "wifi": "Yes, free Wi-Fi is available in all rooms and common areas.",
    "price": "Rates start at €40/night. Tell me your dates (e.g., 20-22 June) to check availability!",
    "parking": "Yes, free parking is on-site. Limited spots—book early!",
    "pets": "Sorry, no pets allowed. Need pet-friendly options? Reply ‘pets’ for suggestions.",
    "ac": "Yes, all rooms have AC—perfect for those hot summer days!",
    "breakfast": "Breakfast is €5 extra per person. Want to add it? Reply ‘yes’.",
    "airport": "From Tirana Airport, it’s a 1-hour drive. Taxis cost ~€30, or reply ‘shuttle’ for our €15 pickup option.",
    "cancel": "Cancellations are free up to 48 hours before arrival. Booked already? Reply ‘cancel’ to check."
}

def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

@app.post("/message")
async def reply(Body: str = Form(), From: str = Form(default=whatsapp_number), db: Session = Depends(get_db)):
    incoming_msg = Body.lower().strip()
    sender = From.replace("whatsapp:", "")
    chat_response = "Not sure what you mean. Try ‘price,’ ‘book,’ or ‘beach’!"

    # FAQ handling
    for key, answer in faqs.items():
        if key in incoming_msg:
            chat_response = answer
            break

    # Booking flow with improved availability check
    if "book" in incoming_msg:
        dates = incoming_msg.replace("book", "").strip()
        try:
            # Handle formats like "20-22 June" or "20 June-22 June"
            parts = dates.split("-")
            if len(parts) != 2:
                raise ValueError("Invalid date range format, must include two dates separated by '-'")
            
            # Extract start and end, assuming month is in the last part
            start_part = parts[0].strip()
            end_part = parts[1].strip()
            month = None
            
            # Extract month from the end part (e.g., "22 June" -> "June")
            for part in end_part.split():
                if part.capitalize() in ["January", "February", "March", "April", "May", "June", 
                                       "July", "August", "September", "October", "November", "December"]:
                    month = part.capitalize()
                    end_part = " ".join([p for p in end_part.split() if p.lower() != month.lower()]).strip()
                    break
            if not month:
                raise ValueError("Month not found in date range")
            
            # Ensure start_part and end_part are just days
            start_day = start_part.split()[0] if " " in start_part else start_part  # Take first word as day
            end_day = end_part.split()[0] if " " in end_part else end_part  # Take first word as day
            
            # Parse dates with placeholder year
            start = datetime.strptime(f"{start_day} {month} 2025", "%d %B %Y")
            end = datetime.strptime(f"{end_day} {month} 2025", "%d %B %Y")
            if end <= start:
                raise ValueError("End date must be after start date")

            # Check for overlap with confirmed bookings
            existing_bookings = db.query(Booking).filter(Booking.status == "confirmed").all()
            has_overlap = False
            for existing in existing_bookings:
                existing_parts = existing.dates.split("-")
                existing_start_part = existing_parts[0].strip()
                existing_end_part = existing_parts[1].strip()
                existing_month = None
                for part in existing_end_part.split():
                    if part.capitalize() in ["January", "February", "March", "April", "May", "June", 
                                           "July", "August", "September", "October", "November", "December"]:
                        existing_month = part.capitalize()
                        existing_end_part = " ".join([p for p in existing_end_part.split() if p.lower() != existing_month.lower()]).strip()
                        break
                existing_start_day = existing_start_part.split()[0] if " " in existing_start_part else existing_start_part
                existing_end_day = existing_end_part.split()[0] if " " in existing_end_part else existing_end_part
                existing_start = datetime.strptime(f"{existing_start_day} {existing_month} 2025", "%d %B %Y")
                existing_end = datetime.strptime(f"{existing_end_day} {existing_month} 2025", "%d %B %Y")
                if (start < existing_end) and (end > existing_start):
                    has_overlap = True
                    break

            if has_overlap:
                chat_response = f"Sorry, {dates} overlaps with an existing booking. Try different dates!"
            else:
                booking = Booking(sender=sender, dates=dates, status="pending", total=100)  # €100 for 2 nights
                db.add(booking)
                db.commit()
                chat_response = f"Checking… {dates} is available. 2 nights at €50/night = €100. Confirm with ‘yes’?"
        except ValueError as e:
            chat_response = f"Invalid date format. Use ‘book DD-DD Month’ (e.g., ‘book 20-22 June’) or ‘book DD Month-DD Month’ (e.g., ‘book 20 June-22 June’). Error: {str(e)}"

    elif incoming_msg == "yes":
        booking = db.query(Booking).filter(Booking.sender == sender, Booking.status == "pending").first()
        if booking:
            chat_response = "Awesome! Pay €100 here: [PayPal.me/ALBotExample]. Reply ‘paid’ when done."

    elif incoming_msg == "paid":
        booking = db.query(Booking).filter(Booking.sender == sender, Booking.status == "pending").first()
        if booking:
            booking.status = "confirmed"
            db.commit()
            chat_response = "Got it—your stay is confirmed! You’ll hear from me the day before with check-in details."

    # Store conversation
    try:
        conversation = Conversation(sender=sender, message=Body, response=chat_response)
        db.add(conversation)
        db.commit()
        logger.info(f"Conversation #{conversation.id} stored in database")
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error storing conversation: {e}")

    # Send response
    try:
        if len(chat_response) > 1600:
            chat_response = chat_response[:1597] + "..."
            logger.warning("Response truncated to 1600 characters")
        send_message(sender, chat_response)
        logger.info(f"WhatsApp message sent to {sender}: {chat_response}")
    except Exception as e:
        logger.error(f"Failed to send message: {e}")

    return {"message": chat_response, "status": "sent"}