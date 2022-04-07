import logging
import random
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

logging.basicConfig(
    level=logging.INFO, format="[%(asctime)s] %(levelname)s: %(message)s"
)
logger = logging.getLogger(__name__)
logging.getLogger("pipeline").setLevel(logging.INFO)

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
    
def AddSelfHelpGroup(admin_phone_number, member_phone_number_list, name, location, initial_balance):
    #need to check whether admin exists or not 
    logging.info(f"checking if admin exists admin phone number {admin_phone_number}")
    admin_income = CheckUserExists(admin_phone_number)
    list_of_incomes = []
    if(admin_income == "nil"):
        logging.info(f"Admin {admin_phone_number} doesn't exist")
        return "Admin is not a valid user in our database"
    else:
        list_of_incomes.append(admin_income)
    #checking whether other members exist or not
    for member in member_phone_number_list:
        member_income = CheckUserExists(member)
        if member_income == "nil":
            logging.info(f"Admin {admin_phone_number} doesn't exist")
            return "Member "+member+" doesnt exist"
        else:
            list_of_incomes.append(member_income)

    #calculating the average annual salary
    total_number_members = len(list_of_incomes)
    sum_of_incomes = sum(list_of_incomes)
    average_annual_income = sum_of_incomes/total_number_members

    #estimating the range and assurance rate 
    if average_annual_income>20000:
        range = "High"
    elif average_annual_income>10000 and average_annual_income<20000:
        range = "Mid"
    elif average_annual_income<10000:
        range = "Low"
    
    #random integer for assurance rate 
    assurance_rate = random.randint(90,100)

    #making the record for insesrtion
    record = {
        "phone_number_admin": admin_phone_number,
        "phone_number_members": member_phone_number_list,
        "name": name,
        "location": location,
        "average_annual_income": average_annual_income,
        "range": range,
        "assurance_rate": assurance_rate,
        "balance": initial_balance
    }
    try:
        logging.info(f"inserting the shg group {name} details")
        result_query = shg_collection.insert_one(record)
        shg_id = result_query.inserted_id
        #logging.info(f"The shg id hence retrieved --> {shg_id}")
        logging.info(f"insertion of shg group {name} has been successfully done")
    except Exception as e:
        logging.error(e)
        logging.error(f"Error in inserting the document of shg group {name}")
    
    #updating the ShgId in each users database


def CheckUserExists(phone_number):
    query = {"phone_number": phone_number}
    query_res = users_collection.find_one(query)

    #if the user doesn't exists
    if query_res is None:
        return "nil"
    else:
        income = query_res["annual_income"]
        return income

def InsertShgId(shg_id, phone_number):

# print(CheckUserExists("9493786234"))

AddSelfHelpGroup("968982900773",["9493786234"],"test_group","vellore",9000)