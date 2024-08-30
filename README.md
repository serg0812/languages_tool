auth.py - authorise the user, create and sign him in, the db in this version is in aws postgres
database.py inserts into chat_history table the latest conversation
chat.py fetches the latest conversation of the user from the database
app.py - main app, yet to be splitted, runs the show, call the functions from tooling and the functions to send to the channel
tooling.py main function to do magic
post_to... functions to send specific blocks to specific channels

as of 29.08 night: tested post_words, changed all other posts but not tested, test randomly in the morning, then switch using secrets and good to push