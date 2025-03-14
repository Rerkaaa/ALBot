# ALBot
WhatsApp bot for automating bookings for coastal hotels and Airbnb hosts in Albania.  
This version (v2) uses preset FAQs and a booking flow for reliable automation, replacing the AI-based v1.  

## Features
- **FAQs**: Instant answers to common questions like "How far is the beach?" or "What’s the price?"  
- **Booking**: Handles reservations with a simple flow: request dates, confirm, pay, and get confirmation.  
- **WhatsApp Integration**: Runs on WhatsApp via Twilio for easy access.  
- **Database Logging**: Stores all conversations in PostgreSQL for tracking.  

## Setup Guide
Follow these steps to set up ALBot on your local machine. This guide assumes a Windows, Linux, or Mac environment.

### 1. Prerequisites
- **Python 3.8+**: Install from [python.org](https://www.python.org/downloads/).  
- **PostgreSQL**: Install from [postgresql.org](https://www.postgresql.org/download/) (e.g., version 15+).  
- **Git**: Install from [git-scm.com](https://git-scm.com/downloads).  
- **Twilio Account**: Sign up at [twilio.com](https://www.twilio.com) for WhatsApp API access.  
- **Ngrok**: Download from [ngrok.com](https://ngrok.com/download) for local tunneling.  

### 2. Clone the Repository
Clone ALBot to your machine:  
```bash
git clone https://github.com/Rerkaaa/ALBot.git
cd ALBot
```

### 3. Install Python Dependencies
Install required packages:
```bash
pip install -r requirements.txt
```
If `requirements.txt` is missing, install manually:
```bash
pip install fastapi uvicorn twilio sqlalchemy psycopg2-binary python-decouple
```

### 4. Set Up PostgreSQL
ALBot logs conversations to a PostgreSQL database named `mydb`.

#### On Windows:
1. Install PostgreSQL (e.g., via installer from postgresql.org).
2. Open pgAdmin (comes with PostgreSQL) or use the command line:
   - Start the PostgreSQL server (usually auto-starts).
   - Open a terminal or `psql`:
   ```bash
   psql -U postgres
   ```
   - Create the database:
   ```sql
   CREATE DATABASE mydb;
   ```
   - Create a user (replace `youruser` and `yourpassword`):
   ```sql
   CREATE USER youruser WITH PASSWORD 'yourpassword';
   GRANT ALL PRIVILEGES ON DATABASE mydb TO youruser;
   ```
   - Exit: `\q`

#### On Linux/Mac:
1. Install PostgreSQL (e.g., `sudo apt install postgresql` on Ubuntu).
2. Start the service:
   ```bash
   sudo service postgresql start
   ```
3. Create the database and user:
   ```bash
   psql -U postgres
   CREATE DATABASE mydb;
   CREATE USER youruser WITH PASSWORD 'yourpassword';
   GRANT ALL PRIVILEGES ON DATABASE mydb TO youruser;
   \q
   ```

### 5. Configure Environment Variables
Create a `.env` file in the ALBot folder with these keys:
```env
TWILIO_ACCOUNT_SID=your_twilio_sid           # From Twilio dashboard
TWILIO_AUTH_TOKEN=your_twilio_auth_token     # From Twilio dashboard
TWILIO_NUMBER=+14155238886                   # Twilio WhatsApp sandbox number
TO_NUMBER=+your_phone_number                 # Your WhatsApp number for testing
DB_USER=youruser                             # PostgreSQL username from step 4
DB_PASSWORD=yourpassword                     # PostgreSQL password from step 4
```
- Get Twilio credentials from [twilio.com/console](https://twilio.com/console).
- Use your phone number (with country code, e.g., +1234567890) for `TO_NUMBER`.

### 6. Set Up Ngrok
Ngrok exposes your local server to the internet for WhatsApp webhooks.
1. Download and unzip Ngrok from [ngrok.com](https://ngrok.com/).
2. Run Ngrok in a terminal:
   ```bash
   ngrok http 8000
   ```
3. Copy the public URL (e.g., `https://abc123.ngrok.io`) for Twilio.

### 7. Configure Twilio WhatsApp Sandbox
1. Log in to [twilio.com/console](https://twilio.com/console).
2. Go to **Messaging** > **Try it out** > **WhatsApp Sandbox**.
3. Send the join code (e.g., `join <your-code>`) from your WhatsApp to the sandbox number.
4. Set the webhook:
   - "When a message comes in" → `https://your-ngrok-url/message` (from step 6).
   - Method: `POST`.
   - Save changes.

### 8. Run the Bot
Start ALBot locally:
```bash
uvicorn main:app --reload
```
- `--reload` auto-restarts on code changes (great for testing).
- Keep Ngrok running in another terminal.

### 9. Test the Bot
1. Open WhatsApp on your phone.
2. Text the Twilio sandbox number (`TWILIO_NUMBER`):
   ```
   beach → "We’re 200 meters from the beach—a quick 3-minute walk!"
   book 20-22 June → Starts the booking flow.
   ```
3. Check logs in your terminal and PostgreSQL:
   ```sql
   SELECT * FROM conversations;
   ```

## Troubleshooting
- **Database Error**: Ensure PostgreSQL is running and `.env` credentials match.
- **Webhook Fails**: Verify Ngrok URL is active and matches Twilio settings.
- **No Response**: Confirm Twilio sandbox is joined and number is correct.

## Notes
- Older AI version (Mistral-7B) is archived on the `v1-mistral` branch.
- Booking availability is hardcoded—future updates will add a calendar.

