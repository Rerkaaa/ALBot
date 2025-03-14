# ALBot
WhatsApp bot for automating booking.  
**Current**: The bot responds with irrelevant answers from mistralai/Mistral-7B-Instruct-v0.3.  
[https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.3](https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.3)
  
**Goal**: Use preset FAQs and booking flows for reliable automation.  

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
