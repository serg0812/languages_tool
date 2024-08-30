# main.py

import streamlit as st
from auth import sign_in
#from auth import sign_up
from database import create_table, close_db_connection, save_message
from chat import load_last_conversation
from tooling import quiz_tool, words_tool, sentences_tool, song_tool
from post_to_quiz import post_quiz
from post_to_words import post_words
from post_to_sentences import post_sentences
from post_to_song import post_song
import re
import psycopg2
import time
import uuid
import json
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents.format_scratchpad.openai_tools import format_to_openai_tool_messages
from langchain.agents import AgentExecutor
from langchain_core.messages import AIMessage, HumanMessage
from langchain.agents.output_parsers.openai_tools import OpenAIToolsAgentOutputParser
from langchain_community.callbacks import get_openai_callback
from langchain_core.tools import StructuredTool
import asyncio

# Set page configuration
st.set_page_config(page_title="Инструмент для квизов, слов и предложений", initial_sidebar_state="auto", menu_items=None)

DB_NAME = st.secrets["DB_NAME"]
DB_USER = st.secrets["DB_USER"]
DB_PASS = st.secrets["DB_PASS"]
DB_HOST = st.secrets["DB_HOST"]
DB_PORT = st.secrets["DB_PORT"]

# Define the inactivity timeout (5 minutes)
INACTIVITY_TIMEOUT = 300

# Function to clear session state
def clear_session_state():
    for key in st.session_state.keys():
        del st.session_state[key]

# Initialize database table
create_table()

# Wrap the tool functions using StructuredTool
quiz_tool_def = StructuredTool.from_function(
    quiz_tool,
    name="quiz",
    description="""creates quiz in the format specified in system message 
    and returns it in a pure json output without word json and ```    
    """
)

words_tool_def = StructuredTool.from_function(
    words_tool,
    name="words",
    description="""creates a list of words on a given topic 
    in the specified language and their translations into russian
    returns this list in a pure json output without word json and ```    
    """
)

sentences_tool_def = StructuredTool.from_function(
    sentences_tool,
    name="sentences",
    description="""creates a list of sentences on a given topic 
    in the specified language and their translations into russian
    returns this list in a pure json output without word json and ```    
    """
)
song_tool_def = StructuredTool.from_function(
    song_tool,
    name="song",
    description="""creates a song on a given topic 
    in the specified language and their translations into russian on per sentence basis
    returns this list in a pure json output without word json and ```    
    """
)

# Function to send JSON output to the channel

def send_json(json_output):
    try:
        # Clean up the JSON string by removing the markdown formatting and extra whitespaces
        json_output = json_output.strip("```json").strip("```").strip()

        # Load the JSON to a Python dictionary
        data = json.loads(json_output)

        # The rest of the processing logic based on response_type
        response_type = data.get('type', 'unknown')

        if response_type == "quiz":
            # Handle quiz data
            text_to_voice = data.get("question")
            options = data.get("options")
            correct_option_id = data.get("correct_option_id")
            language_index = data.get("language_index")
            asyncio.run(post_quiz(text_to_voice, options, correct_option_id, language_index))

        elif response_type == "words":
            # Handle words data
            print(response_type)
            language_index = data.get("language_index")
            words_list = data
            topic = words_list["topic"]
            text_to_voice = "\n".join([f"{word} - {translation} [pause]" for word, translation in words_list.items() if word not in ["topic", "language_index", "type"]])
            asyncio.run(post_words(topic, text_to_voice, language_index))

        elif response_type == "sentences":
            # Handle sentences data
            print(response_type)
            language_index = data.get("language_index")
            sentences_list = data
            topic = sentences_list["topic"]
            text_to_voice = "\n".join([f"{sentence} - {translation} [pause]" for sentence, translation in sentences_list.items() if sentence not in ["topic", "language_index", "type"]])
            asyncio.run(post_sentences(topic, text_to_voice, language_index))

        elif response_type == "song":
            # Handle song data
            print(response_type)
            language_index = data.get("language_index")
            translation_list = data.get("translation", {})
            topic = data.get("topic", "Song Lyrics")
            
            # Convert the translations to the desired format: original in bold - translation
            text_to_voice = "\n".join([f"**{sentence}** - {translation}" for sentence, translation in translation_list.items()])
            
            # Send the formatted text to the channel
            asyncio.run(post_song(topic, text_to_voice, language_index))

        else:
            st.error("Unknown JSON structure or missing type")
    
    except json.JSONDecodeError as e:
        st.error(f"JSON decoding error: {e}")

    except Exception as e:
        st.error(f"Error in sending JSON: {e}")

# User authentication
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

if not st.session_state['authenticated']:
    auth_action = st.sidebar.selectbox('Select Action', ['Sign In', 'Sign Up'])

    if auth_action == 'Sign Up':
        st.title('Sign Up')
        name = st.text_input('First Name')
        surname = st.text_input('Surname')
        email = st.text_input('Email')
        password = st.text_input('Password', type='password')
        if st.button('Sign Up'):
#            sign_up(name, surname, email, password)
#            st.success("You have successfully signed up! Please sign in.")
             st.success("There is no sign up here! Please sign in.")

    if auth_action == 'Sign In':
        st.title('Sign In')
        email = st.text_input('Email')
        password = st.text_input('Password', type='password')
        if st.button('Sign In'):
            if sign_in(email, password):
                st.session_state['authenticated'] = True
                st.session_state['email'] = email
                # Fetch user details from the database
                conn = psycopg2.connect(
                    dbname=DB_NAME,
                    user=DB_USER,
                    password=DB_PASS,
                    host=DB_HOST,
                    port=DB_PORT
                )
                cur = conn.cursor()
                cur.execute("SELECT name, surname FROM users WHERE email = %s", (email,))
                user = cur.fetchone()
                cur.close()
                conn.close()
                st.session_state['name'] = user[0]
                st.session_state['surname'] = user[1]

                chat_history = load_last_conversation(st.session_state['email'])

                # Ensure chat_history contains only valid messages
                chat_history = [msg for msg in chat_history if isinstance(msg, (HumanMessage, AIMessage))]
                
                st.session_state['chat_history'] = chat_history

                # Always start a new session ID
                st.session_state['session_id'] = str(uuid.uuid4())

                st.rerun()
            else:
                st.error("Invalid email or password")
else:
    st.sidebar.button('Sign Out', on_click=clear_session_state)

    session_id = st.session_state['session_id']
    name = st.session_state['name']

    with open("instructions/instructions.txt") as file:
        specific_instructions = file.read()

    st.session_state['system_prompt'] = f"""
            This session has this id {session_id}.
            Your detailed instructions are here: 
            """ + f"{specific_instructions}"

    text = st.session_state['system_prompt']

    llm = ChatOpenAI(model="gpt-4o", temperature=0, max_tokens=4000)
    tools = [quiz_tool_def, words_tool_def, sentences_tool_def, song_tool_def]
    llm_with_tools = llm.bind_tools(tools=tools)

    MEMORY_KEY = "chat_history"
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", f"{text}"),
            MessagesPlaceholder(variable_name=MEMORY_KEY),
            ("user", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ]
    )

    if 'chat_history' not in st.session_state:
        st.session_state['chat_history'] = []
        st.session_state['last_interaction_time'] = time.time()
    else:
        if not isinstance(st.session_state['chat_history'], list):
            st.session_state['chat_history'] = list(st.session_state['chat_history'])

        st.session_state['chat_history'] = [msg for msg in st.session_state['chat_history'] if isinstance(msg, (HumanMessage, AIMessage))]
        
        st.session_state['last_interaction_time'] = time.time()

    agent = (
        {
            "input": lambda x: x["input"],
            "agent_scratchpad": lambda x: format_to_openai_tool_messages(x["intermediate_steps"]),
            "chat_history": lambda x: x["chat_history"],
        }
        | prompt
        | llm_with_tools
        | OpenAIToolsAgentOutputParser()
    )

    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True, stream_runnable=False)

    st.markdown("<h2 style='text-align: center; color: grey;'>📱 Welcome to our language school 📱</h2>", unsafe_allow_html=True)

    user_input = st.chat_input("")

    if user_input:
        st.session_state['chat_history'].append(HumanMessage(content=user_input))
        save_message(st.session_state['email'], st.session_state['name'], st.session_state['surname'], st.session_state['session_id'], False, user_input)
        st.session_state['last_interaction_time'] = time.time()

        with get_openai_callback() as cb:
            result = agent_executor.invoke({
                "input": user_input,
                "chat_history": st.session_state['chat_history']
            })
            json_output = result["output"]
            print(cb.total_tokens)

        st.session_state['chat_history'].append(AIMessage(content=json_output))
        save_message(st.session_state['email'], st.session_state['name'], st.session_state['surname'], st.session_state['session_id'], True, json_output)
        st.session_state['last_interaction_time'] = time.time()

    st.write("--------------------------------------")
    for message in st.session_state['chat_history']:
        if isinstance(message, HumanMessage):
            st.markdown(f"**You:** {message.content}")
        elif isinstance(message, AIMessage):
            st.markdown(f"**Quiz_helper:** {message.content}")

    if 'last_interaction_time' in st.session_state and time.time() - st.session_state['last_interaction_time'] > INACTIVITY_TIMEOUT:
        close_db_connection()

    # Button to show the json editor
    if st.button("Edit Last Message"):
        st.session_state['show_json_editor'] = True
        # Display the last message in the text area
        if st.session_state['chat_history']:
            last_message = st.session_state['chat_history'][-1]
            if isinstance(last_message, AIMessage):
                st.session_state['last_message_content'] = last_message.content
            else:
                st.session_state['last_message_content'] = ""

    # Json editor
    if st.session_state.get('show_json_editor', False):

        edited_json = st.text_area("Edit Last Message", value=st.session_state.get('last_message_content', ""), key='json_editor')

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Discard"):
                st.session_state['show_json_editor'] = False
                st.rerun()
        with col2:
            if st.button("Send"):
                # this block is to handle complicated structure of song, otherwise should be straight forward
                try:
                    # Step 1: Clean up the JSON string by removing the markdown formatting and extra whitespaces
                    cleaned_json = edited_json.strip("```json").strip("```").strip()

                    # Step 2: Remove the 'song_text' field manually from the string
                    if '"song_text"' in cleaned_json:
                        # Remove everything from "song_text" to the closing quote of its value
                        cleaned_json = re.sub(r'"song_text":\s*".*?",\s*', '', cleaned_json, flags=re.DOTALL)

                    # Step 3: Convert 'translation' array to a dictionary format in the string itself
                    if '"translation": [' in cleaned_json:
                        cleaned_json = cleaned_json.replace('"translation": [', '"translation": {')
                        cleaned_json = cleaned_json.replace(']', '}')

                        # Further formatting if the list items are not properly separated by commas or if there's any format error.
                        cleaned_json = re.sub(r'\}\s*\{', '}, {', cleaned_json)  # Ensure correct dictionary syntax

                    # Step 4: Convert the cleaned string to a JSON object
                    data = json.loads(cleaned_json)

                    # Step 5: Now send the processed JSON
                    send_json(json.dumps(data, ensure_ascii=False, indent=2))
                    st.session_state['show_json_editor'] = False
                    st.rerun()
                
                except json.JSONDecodeError as e:
                    st.error(f"JSON decoding error: {e}")
                except Exception as e:
                    st.error(f"Error in processing or sending JSON: {e}")