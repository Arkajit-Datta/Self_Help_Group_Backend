import logging
from pymongo import MongoClient

try:
    client = MongoClient("mongodb+srv://arkajit:arkajit@cluster0.dmii1.mongodb.net/sahayata?retryWrites=true&w=majority")
    db = client.get_database('sahayata')
    users_collection = db.users
    shg_collection = db.shg
    transaction_collection = db.transaction
    logging.info("The database and the collections data connected!")
except Exception as e:
    logging.error(e)
    logging.error("Error in connecting the database")

def doSignup(name, phone_number, password, age, location, annual_income,aadhar_path, pan_path):

    record = {
        "name": name,
        "phone_number": phone_number,
        "password": password,
        "age": age,
        "location": location,
        "annual_income": annual_income,
        "aadhar_upload": aadhar_path,
        "pan_upload": pan_path
    }

    try:
        logging.info("inserting into database")
        result_transaction = users_collection.insert_one(record)
        logging.info(f"inserted the users data --> {name} successfully")
    except Exception as e:
        logging.error(result_transaction)
        logging.error(e)
        logging.error(f"Error in inserting the users data --> {name}")
    
