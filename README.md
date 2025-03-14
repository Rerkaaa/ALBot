# ALBot
WhatsApp bot for automating bookings for coastal hotels and Airbnb hosts in Albania.  
This version (v2) uses preset FAQs and a booking flow for reliable automation, replacing the AI-based v1.  

## Features
- **FAQs**: Instant answers to common questions like "How far is the beach?" or "What’s the price?"  
- **Booking**: Handles reservations with a simple flow: request dates, confirm, pay, and get confirmation.  
- **WhatsApp Integration**: Runs on WhatsApp via Twilio for easy access.  
- **Database Logging**: Stores all conversations in PostgreSQL for tracking.  

## Setup
1. Install dependencies: `pip install -r requirements.txt`
2. Create a `.env` file with:  
   - `TWILIO_ACCOUNT_SID`  
   - `TWILIO_AUTH_TOKEN`  
   - `TWILIO_NUMBER`  
   - `TO_NUMBER`  
   - `DB_USER`  
   - `DB_PASSWORD`  
3. Run: `uvicorn main:app --reload`