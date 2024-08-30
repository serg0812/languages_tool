the apps are connected to the cloud db. details are stored in streamlit and locally

sign up is disabled, new users can be created only locally from ling... in lang.._ch

app.py - the main app
auth.py - authorize the users and checks the creds
database.py - saves the last conversation 
chat.py - fetches the last conversation with user_id and session_id
tooling.py - tools to work, words, sentences, quiz and song are available now
When song is generated, the actual music  has to run and to be uploaded locally for now
post_to_... - these are called from app.py based on send_json and are posted to the channels
