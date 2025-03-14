# Third-party imports
from fastapi import FastAPI, Form, Depends
from decouple import config
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
import os

# Internal imports
from models import Conversation, SessionLocal
from utils import logger, send_message

app = FastAPI()

# WhatsApp number from .env
whatsapp_number = config("TO_NUMBER")

# FAQ dictionary for ALBot
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

# In-memory booking storage (replace with DB later)
bookings = {}  # {phone: {"dates": "20-22 June", "status": "pending", "total": 100}}

# Dependency for database
def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

@app.post("/message")
async def reply(Body: str = Form(), From: str = Form(default=whatsapp_number), db: Session = Depends(get_db)):
    incoming_msg = Body.lower().strip()
    sender = From.replace("whatsapp:", "")  # Clean up 'whatsapp:' prefix from Twilio

    # Default response
    chat_response = "Not sure what you mean. Try ‘price,’ ‘book,’ or ‘beach’!"

    # FAQ handling
    for key, answer in faqs.items():
        if key in incoming_msg:
            chat_response = answer
            break

    # Booking flow
    if "book" in incoming_msg:
        dates = incoming_msg.replace("book", "").strip()
        bookings[sender] = {"dates": dates, "status": "pending", "total": 100}  # Hardcoded €100 for 2 nights
        chat_response = f"Checking… {dates} is available. 2 nights at €50/night = €100. Confirm with ‘yes’?"
    elif incoming_msg == "yes" and sender in bookings:
        chat_response = "Awesome! Pay €100 here: [PayPal.me/ALBotExample]. Reply ‘paid’ when done."
    elif incoming_msg == "paid" and sender in bookings:
        bookings[sender]["status"] = "confirmed"
        chat_response = "Got it—your stay is confirmed! You’ll hear from me the day before with check-in details."

    # Store the conversation in the database
    try:
        conversation = Conversation(
            sender=sender,
            message=Body,
            response=chat_response
        )
        db.add(conversation)
        db.commit()
        logger.info(f"Conversation #{conversation.id} stored in database")
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error storing conversation in database: {e}")

    # Send the response via WhatsApp
    try:
        if len(chat_response) > 1600:
            chat_response = chat_response[:1597] + "..."
            logger.warning("Response truncated to 1600 characters for WhatsApp")
        send_message(sender, chat_response)
        logger.info(f"WhatsApp message sent to {sender}: {chat_response}")
    except Exception as e:
        logger.error(f"Failed to send message: {e}")

    return {"message": chat_response, "status": "sent"}