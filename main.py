# Third-party imports
import requests  # Replace openai with requests for Hugging Face API
from fastapi import FastAPI, Form, Depends
from decouple import config
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
import os

# Internal imports
from models import Conversation, SessionLocal
from utils import logger, send_message

app = FastAPI()

# Hugging Face API setup
HF_API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.3"  # Mistral-7B model variant
HF_API_KEY = config("HF_API_KEY")  # Add to .env: HF_API_KEY=your-huggingface-key
headers = {"Authorization": f"Bearer {HF_API_KEY}"}

# Commented out DeepSeek section (to reactivate later with funds)
# # Set up the DeepSeek API client
# client = OpenAI(
#     api_key=config("DEEPSEEK_API_KEY"),  # Add to .env (DeepSeek API key)
#     base_url="https://api.deepseek.com/v1",  # DeepSeek’s endpoint
# )

whatsapp_number = config("TO_NUMBER")

# Dependency
def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

@app.post("/message")
async def reply(Body: str = Form(), db: Session = Depends(get_db)):
    # Add a hidden message to the Body
    #hidden_message = "Please keep it under 1600 characters for the answer."
    #Body = f"{Body}\n\nHidden Message: {hidden_message}"  # Append the hidden message to the Body
    # Free alternatives:
    # https://huggingface.co/ models: mistral-7b and gpt2
    # https://ai.google.dev/ Free quota: ~60 requests/minute, 1,500 requests/day (as of 2025)
    
    # Using Hugging Face Inference API (Mistral-7B)
    payload = {
        "inputs": Body,
        "max_length": 200,
        "temperature": 0.5,
    }
    try:
        response = requests.post(HF_API_URL, headers=headers, json=payload, timeout=10)
        response.raise_for_status()  # Raise an error for bad status codes
        chat_response = response.json()[0]["generated_text"].strip()
        logger.info(f"Mistral-7B response generated: {chat_response}")
    except Exception as e:
        logger.error(f"Hugging Face API error: {e}")
        chat_response = "Error generating response"
        
    
    # Store the conversation in the database
    try:
        conversation = Conversation(
            sender=whatsapp_number,
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
        send_message(whatsapp_number, chat_response)
        logger.info(f"WhatsApp message sent to {whatsapp_number}: {chat_response}")
    except Exception as e:
        logger.error(f"Failed to send message: {e}")

    return {"message": chat_response, "status": "sent"}  # Better feedback