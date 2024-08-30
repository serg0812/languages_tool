import logging
from telegram.ext import Application
from openai import OpenAI
import re
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

CHANNEL_ID = [-1002169277065,-1002201911415,-1002191340632,-1002196952107,-1002152024965,-1002148395087]  # Switched to array fo channels, the last one for portuguese still to the test channel

languages = ['English', 'Español', 'Français', 'Deutsch', 'Italiano', 'Português']

def escape_markdown_v2(text):
    """
    Escapes special characters in MarkdownV2.
    """
    return re.sub(r'([_\[\]()~`>#+\-=|{}.!\\])', r'\\\1', text)

async def post_song(topic, text_to_voice, index) -> None:
    application = Application.builder().token(TOKEN).build()
    await application.initialize()
    
    # Properly format the topic text with MarkdownV2 for bold
    bold_topic = f"*{escape_markdown_v2(topic)}*"
    intro_text = escape_markdown_v2(f" Перевод:\n {bold_topic}\n")

    # Format the text with MarkdownV2
    lines = text_to_voice.split('\n')
    formatted_lines = []
    for line in lines:
        # Replace ' - ' with a unique separator to avoid conflict with escaped '-'
        parts = line.replace(' - ', ' \n- ').split(' \n- ')
        if len(parts) == 2:
            sentence, translation = parts
            escaped_sentence = escape_markdown_v2(sentence)
            escaped_translation = escape_markdown_v2(translation)
            formatted_line = f"*{escaped_sentence}* \- {escaped_translation}"
            formatted_lines.append(formatted_line)

    message_text = intro_text + "\n".join(formatted_lines)

    try:
        # Send the message to the channel
        await application.bot.send_message(chat_id=CHANNEL_ID[index], text=message_text, parse_mode="MarkdownV2")
                
    except Exception as e:
        logger.error(f"Failed to send song lyrics: {e}")
    
    await application.shutdown()
