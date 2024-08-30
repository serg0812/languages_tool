import logging
from telegram.ext import Application
from openai import OpenAI
import re
import streamlit as st

client = OpenAI()

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name=s - %(levelname=s - %(message=s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Replace 'YOUR_TOKEN_HERE' with your bot's API token
TOKEN = st.secrets["TOKEN"]

CHANNEL_ID = [-1002169277065,-1002201911415,-1002191340632,-1002196952107,-1002152024965,-1002148395087]  # Switched to array fo channels, the last one for portuguese still to the test channel

# Language settings
languages = ['English', 'Español', 'Français', 'Deutsch', 'Italiano', 'Português']

def escape_markdown_v2(text):
    """
    Escapes special characters in MarkdownV2.
    """
    return re.sub(r'([_\[\]()~`>#+\-=|{}.!\\])', r'\\\1', text)  # Remove asterisk from here

def generate_voice_response(text_to_voice):
    voice_response = client.audio.speech.create(
        model="tts-1",
        voice="alloy",
        input=text_to_voice,
    )
    voice_audio_path = "./audio/words_audio.mp3"
    voice_response.stream_to_file(voice_audio_path)

async def post_words(topic, text_to_voice, index) -> None:
    application = Application.builder().token(TOKEN).build()
    await application.initialize()

    generate_voice_response(text_to_voice)

    # Properly format the topic text with MarkdownV2 for bold
    bold_topic = f"*{escape_markdown_v2(topic)}*"
    intro_text = escape_markdown_v2(f"Cлова на тему:\n {bold_topic}\n Язык: {languages[index]}\n\n")

    # Format the text with MarkdownV2
    lines = text_to_voice.split('\n')
    formatted_lines = []
    for line in lines:
        # Replace ' - ' with a unique separator to avoid conflict with escaped '-'
        parts = line.replace(' - ', ' \n- ').split(' \n- ')
        if len(parts) == 2:
            word, translation = parts
            translation = translation.replace("[pause]", "").strip()
            escaped_word = escape_markdown_v2(word)
            escaped_translation = escape_markdown_v2(translation)
            formatted_line = f"*{escaped_word}* \- ||{escaped_translation}||"
            formatted_lines.append(formatted_line)
            print(word) #to get input for song

    message_text = intro_text + "\n".join(formatted_lines)

    try:
        # Debugging: Log the message text
        logger.info(f"Message text to be sent: {message_text}")

        # Send the message to the channel
        await application.bot.send_message(chat_id=CHANNEL_ID[index], text=message_text, parse_mode="MarkdownV2")

        # Send the generated audio
        with open("./audio/words_audio.mp3", "rb") as audio_file:
            await application.bot.send_audio(chat_id=CHANNEL_ID[index], audio=audio_file)

        
    except Exception as e:
        logger.error(f"Failed to send words or audio: {e}")
    
    await application.shutdown()
