# post_to_quiz.py

import logging
from telegram import Poll
from telegram.ext import Application
from openai import OpenAI  # for calling the OpenAI API
import os
import streamlit as st

client = OpenAI()

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Replace 'YOUR_TOKEN_HERE' with your bot's API token
TOKEN = st.secrets["TOKEN"]

# Replace 'YOUR_CHANNEL_ID' with your actual channel ID from Telethon
CHANNEL_ID = [-1002169277065,-1002201911415,-1002191340632,-1002196952107,-1002152024965,-1002148395087]  # Switched to array fo channels, the last one for portuguese still to the test channel

# Language settings
languages = ['English', 'Español', 'Français', 'Deutsch', 'Italiano', 'Português']
countries = ['uk', 'spain', 'france', 'germany', 'italy', 'portugal']
guess = ['английском', 'испанском', 'французском', 'немецком', 'итальянском', 'португальском']

def generate_voice_response(text_to_voice):
    voice_response = client.audio.speech.create(
        model="tts-1",
        voice="alloy",
        input=text_to_voice,
    )

    # Save the greeting audio to a temporary file
    voice_audio_path = "../audio/quiz_audio.mp3"
    voice_response.stream_to_file(voice_audio_path)

async def post_quiz(text_to_voice, options, correct_option_id, index) -> None:
    application = Application.builder().token(TOKEN).build()
    await application.initialize()
    
    generate_voice_response(text_to_voice)

    question = {
        "intro": f"Угадываем ответ! Quiz {languages[index]}:",
        "question": f"Угадай значение этой фразы на {guess[index]}: {text_to_voice}",
        "options": options,
        "correct_option_id": correct_option_id,
        "photo": f"../photos/{countries[index]}_map_flag.png",
        "audio": "../audio/quiz_audio.mp3"
    }

    logger.info(f"Sending photo for intro: {question['intro']}")
    try:
        with open(question["photo"], "rb") as photo_file:
            await application.bot.send_photo(
                chat_id=CHANNEL_ID[index],
                photo=photo_file,
                caption=question["intro"]
            )
        
        logger.info(f"Sending poll for question: {question['question']}")
        await application.bot.send_poll(
            chat_id=CHANNEL_ID[index],
            question=question["question"],
            options=question["options"],
            is_anonymous=True,
            type=Poll.QUIZ,
            correct_option_id=question["correct_option_id"]
        )
        logger.info("Poll sent successfully")
        
        logger.info(f"Sending audio for question: {question['question']}")
        with open(question["audio"], "rb") as audio_file:
            await application.bot.send_audio(
                chat_id=CHANNEL_ID[index],
                audio=audio_file,
                caption=f"Как это звучит на {guess[index]}"
            )
        logger.info("Audio sent successfully")
        
    except Exception as e:
        logger.error(f"Failed to send poll or audio: {e}")
    
    await application.shutdown()
