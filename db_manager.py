"""
Helper file for various database tasks, like creating and loading data.

Accepted command-line arguments:
    create_db
    add_users
    add_chats
    add_messages
    get_messages
    add_user
    start_chat

"""

import argparse

import models
import time
import os
import sqlalchemy as sq
import db
import pandas as pd
import uuid
from datetime import datetime

DATABASE_NAME = "xerophyta_db.sqlite"

def create_new_db():
    """
    Deletes and recreates the SQLITE database. Is required when the model structure changes
    """
    print("Deleting old database file...")

    if os.path.exists(DATABASE_NAME):
        os.remove(DATABASE_NAME)
        
    print("Creating new db")
    engine = sq.create_engine(f"sqlite:///{DATABASE_NAME}", echo=False)
    connection = engine.connect()

    print("Creating tables")
    models.Base.metadata.create_all(engine)

    print("DONE")


def add_rna_seq():
    """
    Populates the database with dummy user data from an excel file
    """
    database = db.DB()
    data = pd.read_csv("data/Xe_seedlings_normalised_counts_tidy.csv")
    data['id'] = data["id"]+'_'+data['gene_name']

    database.batch_create_or_update(models.Gene_expressions, data.to_dict("records"), "id")



def add_chats():
    """
    Populates the database with dummy chat data from an excel file
    """

    database = db.DB()
    chats = pd.read_excel("data/chat_data.xlsx")
        
    database.create_or_update(models.Chat, chats.to_dict("records"), "chat_id")


def add_messages():
    """
    Allows entering of messages from the command line. Simulates incoming data from the server
    """
    database = db.DB()

    while True:
        chat_id = input("Chat Id: ")
        from_id = input("Your ID: ")
        
        timestamp = datetime.now()
        print("Timestamp: {}".format(timestamp))

        content = input("Message: ")

        input("Press enter to send")

        database.add_message(chat_id, content, timestamp, from_id)


def get_messages():
    """
    Fetches all messages from the database based on a chat id
    """
    chat_id = input("Chat id: ")

    database = db.DB()

    print()

    for msg in database.get_chat_messages(chat_id=chat_id):
        print("Message to {} from {} at {}: \n {}".format(msg.chat_id, msg.from_id, msg.timestamp, msg.content))


def add_user():
    """
    Either inserts or updates a user in the database
    """
    database = db.DB()

    id = input("ID: ")
    first_name = input("Name: ")
    last_name = input("Last Name: ")
    ip_address = input("IP: ")

    print(database.create_or_update(models.User, [{
        "user_id": id,
        "first_name": first_name, 
        "last_name": last_name,
        "ip_address": ip_address
    }], "user_id"))


def start_chat():
    """
    Creates a new chat in the database
    """
    users = input("Enter list of users separated by a space: ").split(" ")
    
    print(users)
    
    d = db.DB()

    new_chat = d.create_or_update(models.Chat, [{"chat_id": str(uuid.uuid4())}], "chat_id")
    
    users = d.get_users(users)
   

    for user in users:
        new_chat.users.append(user)

    d.session.commit()
        

def init_db():
    create_new_db()
    add_rna_seq()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("command")
    
    args = parser.parse_args()
   
    if args.command == "create_db":
        create_new_db()

    elif args.command == "add_rna_seq":
       add_rna_seq()

    elif args.command == "add_chats":
        add_chats()

    elif args.command == "add_messages":
        add_messages()

    elif args.command == "get_messages":
        get_messages

    elif args.command == "add_user":
        add_user()
    
    elif args.command == "start_chat":
        start_chat()

    elif args.command == "init":
        init_db()

    elif args.command == "get_chats":
        users = input("Users: ").split()
        d = db.DB()

        chat = d.get_or_create_chat(users)

        print(chat.chat_id)
        

    else:
        print("Unrecognized command")

    pass
