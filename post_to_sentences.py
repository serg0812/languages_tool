import logging
from telegram.ext import Application
from openai import OpenAI
import re
import streamlit as st
from flux_call import generate_image

client = OpenAI()

def generate_photo_prompt(user_prompt):
  system_prompt = """
  You are a master in creating prompts for online tool making images
  You will be given a bunch of sentences with each of them translated into Russian, then you should pick up from them jsut one
  You should ignore their Russian translation, just focus on the originals
  You criteria to pick one of them up should be based on what will be the most intersting picture
  You should pick up just ONE sentence and build the prompt around it
  The sentences will be based on the same person and will contain facts of this person life.
  Examples of sentenses
  Albert Einstein loved playing violin
  He got a Nobel prize for photelectric effect
  He was married twice
  He escaped Nazi Germany and move to the US where he lived the rest of his life

  Your promp should look like this
  Examples:
  Albert Einshtein playing violin in his laboratory surronded by students
  
  """
  completion = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": f"{system_prompt}"},
        {"role": "user", "content": f"Translate this into Russian: {user_prompt}"}
      ]
      )
  print(completion.choices[0].message.content.strip())
  return completion.choices[0].message.content.strip()
    


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
    return re.sub(r'([_\[\]()~`>#+\-=|{}.!\\])', r'\\\1', text)  # Remove asterisk from here

def generate_voice_response(text_to_voice):
    voice_response = client.audio.speech.create(
        model="tts-1",
        voice="alloy",
        input=text_to_voice,
    )
    voice_audio_path = "./audio/sentences_audio.mp3"
    voice_response.stream_to_file(voice_audio_path)

async def post_sentences(topic, text_to_voice, index) -> None:
    application = Application.builder().token(TOKEN).build()
    await application.initialize()
    
    generate_voice_response(text_to_voice)

    # Properly format the topic text with MarkdownV2 for bold
    bold_topic = f"*{escape_markdown_v2(topic)}*"
    intro_text = escape_markdown_v2(f"Предложения на тему:\n {bold_topic}\n Язык: {languages[index]}\n\n")

    # Format the text with MarkdownV2
    lines = text_to_voice.split('\n')
    formatted_lines = []
    for line in lines:
        # Replace ' - ' with a unique separator to avoid conflict with escaped '-'
        parts = line.replace(' - ', ' \n- ').split(' \n- ')
        if len(parts) == 2:
            sentence, translation = parts
            translation = translation.replace("[pause]", "").strip()
            escaped_sentence = escape_markdown_v2(sentence)
            escaped_translation = escape_markdown_v2(translation)
            formatted_line = f"*{escaped_sentence}* \- ||{escaped_translation}||"
            formatted_lines.append(formatted_line)

    message_text = intro_text + "\n".join(formatted_lines)
    text=generate_photo_prompt(message_text)
    generate_image(text)


    try:
        with open("./photos/output_sentence.png", "rb") as photo_file:
            await application.bot.send_photo(
                chat_id=CHANNEL_ID[index],
                photo=photo_file,
            )

        # Send the message to the channel
        await application.bot.send_message(chat_id=CHANNEL_ID[index], text=message_text, parse_mode="MarkdownV2")
        
        # Send the generated audio
        with open("./audio/sentences_audio.mp3", "rb") as audio_file:
            await application.bot.send_audio(chat_id=CHANNEL_ID[index], audio=audio_file)
        
    except Exception as e:
        logger.error(f"Failed to send sentences or audio: {e}")
    
    await application.shutdown()
