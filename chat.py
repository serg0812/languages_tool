import streamlit as st
from database import get_db_connection
from langchain_core.messages import AIMessage, HumanMessage

def load_last_conversation(user_id):
    conn = get_db_connection()
    cur = conn.cursor()
    # Fetch the latest session_id for the user
    cur.execute("""
        SELECT session_id method FROM chat_history 
        WHERE user_id = %s 
        ORDER BY timestamp DESC 
        LIMIT 1
    """, (user_id,))
    last_session = cur.fetchone()

    if not last_session:
        cur.close()
        return None, None, None, None

    session_id = last_session

    # Fetch all messages for the latest session_id
    cur.execute("""
        SELECT AI, text FROM chat_history 
        WHERE session_id = %s 
        ORDER BY timestamp
    """, (session_id,))
    messages = cur.fetchall()
    cur.close()

    # Structure messages into chat history
    chat_history = []
    for is_ai, text in messages:
        if is_ai:
            chat_history.append(AIMessage(content=text))
        else:
            chat_history.append(HumanMessage(content=text))
    
    return chat_history

