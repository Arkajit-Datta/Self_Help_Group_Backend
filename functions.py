import logging
import random
from pymongo import MongoClient

logging.basicConfig(
    level=logging.INFO, format="[%(asctime)s] %(levelname)s: %(message)s"
)
logger = logging.getLogger(__name__)
logging.getLogger("pipeline").setLevel(logging.INFO)

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
        "pan_upload": pan_path,
        "shg_id": 0,
        "admin": False
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
        "balance": initial_balance,
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
    InsertShgId(shg_id=shg_id, phone_number = admin_phone_number, is_admin=1)

    #update for all the members 
    for number in member_phone_number_list:
        InsertShgId(shg_id=shg_id, phone_number = number, is_admin=0)
    return "Self Help Group Created! All members Database updated!"

def CheckUserExists(phone_number):
    query = {"phone_number": phone_number}
    query_res = users_collection.find_one(query)

    #if the user doesn't exists
    if query_res is None:
        return "nil"
    else:
        income = query_res["annual_income"]
        return income

def InsertShgId(shg_id, phone_number,is_admin):
    if is_admin:
        filter = {"phone_number": phone_number}
        new_values = {"$set": {'shg_id': shg_id, 'admin':True}}
        res = users_collection.update_one(filter, new_values)
    else:
        filter = {"phone_number": phone_number}
        new_values = {"$set": {'shg_id': shg_id, 'admin':False}}
        res = users_collection.update_one(filter, new_values)

#This function will search for the self help groups and would return a list of recommended self help group
def SearchSelfHelpGroup(location):
    try:
        query_res = shg_collection.find({"location": location}).sort("assurance_rate", -1)
    except Exception as e:
        logging.error(e)
        logging.error("Error in searching for the group")
    list_of_searches = []
    if query_res is None:
        return 0
    else:
        for x in query_res:
            del x['_id']
            list_of_searches.append(x)
        return list_of_searches

def JoinSelfHelpGroup(name, phone_number):
    try:
        query_res = shg_collection.find_one({"name":name })
    except Exception as e:
        logging.error(e)
        logging.error("Issue in finding the shg_collection")

    try:
        income =CheckUserExists(phone_number=phone_number)
    except Exception as e:
        logging.error(e)
        logging.error("Issue in checking the validity of user")

    if income=="nil":
        return 0

    
    if query_res is None:
        return 0
    else:
        logging.info("SHG with the name exists")
        shg_id = query_res["_id"]
        list_of_numbers = query_res["phone_number_members"]
        list_of_numbers.append(phone_number)
        logging.info(f"The group id --> {shg_id}")

        try:
            #inserting the user into that shg group
            filter_for_shg = {"_id": shg_id}
            new_value_shg = {"$set": {"phone_number_members": list_of_numbers}}
            res_for_updating_value_in_shg = shg_collection.update_one(filter_for_shg, new_value_shg)
        except Exception as e:
            logging.error(e)
            logging.error("Error occured while updating the new users value in SHG collection")

        try:
            #inserting the shg details in users table
            filter_for_user = {"phone_number": phone_number}
            new_value_for_user = {"$set": {"shg_id": shg_id, "admin": False}}
            res_for_updating_value_in_user = users_collection.update_one(filter_for_user, new_value_for_user)
        except Exception as e:
            logging.error(e)
            logging.error("Error in updating the value of shg and admin in user collection")
    return 1

#Get the profile of any user given the phone number             
def SeeProfile(phone_number):
    try:
        query_res = users_collection.find_one({"phone_number": phone_number})
    except Exception as e:
        logging.error(e)
        logging.error("Error in fetching the users details")
    
    #initialising the dictionary
    user_details = dict()
    #checking if the user exists or not 
    if query_res is None:
        return 0
    else:
        user_details["name"] = query_res["name"]
        user_details["phone_number"] = query_res["phone_number"]
        user_details["age"] = query_res["age"]
        user_details["location"] = query_res["location"]
        user_details["annual_income"] = query_res["annual_income"]

        try:
            shg_id = query_res["shg_id"]
            print(shg_id)
            if shg_id == 0:
                user_details["shg_name"] = "No Self Help Groups Joined"
                user_details["admin"] = "Not an Admin"
                return user_details
            else:
                try:
                    #searching for the namoup", "9493786234", 1000)e of the self help group
                    query_for_searching_name_of_shg = shg_collection.find_one({"_id": shg_id})
                    user_details["shg_name"] = query_for_searching_name_of_shg["name"]

                except Exception as e:
                    logging.error(e)
                    logging.error("Error in searching the name of SHG")
                return user_details
        except Exception as e:
            logging.error(e)


#For executing the transaction
def transaction_deposit(shg_name, phone_number, amount):
    try:
        query_res = shg_collection.find_one({"name": shg_name})
    except Exception as e:
        logging.error(e)

    if query_res is None:
        return -1
    else:
        shg_id = query_res["_id"]
        balance = query_res["balance"]
        balance = balance + amount

    filter_shg_id = {"_id": shg_id}         
    new_value_shg = {"$set": {"balance": balance}}
    res_for_updating_value_in_shg = shg_collection.update_one(filter_shg_id, new_value_shg)

    record_trans = {
        "shg_id": shg_id,
        "amount" : amount,
        "credit" : True,
        "debit" : False,
        "phone_number": phone_number
    }
    query_res_transaction  = transaction_collection.insert_one(record_trans)

    return balance

#For executing the withdraw
def transaction_withdraw(shg_name, phone_number, amount):
    try:
        query_res = shg_collection.find_one({"name": shg_name})
        if query_res is None:
            return -1
        else:
            shg_id = query_res["_id"]
            balance = query_res["balance"]
            balance = balance - amount

    except Exception as e:
        logging.error(e)

    filter_shg_id = {"_id": shg_id}         
    new_value_shg = {"$set": {"balance": balance}}
    res_for_updating_value_in_shg = shg_collection.update_one(filter_shg_id, new_value_shg)

    record_trans = {
        "shg_id": shg_id,
        "amount" : amount,
        "credit" : False,
        "debit" : True,
        "phone_number": phone_number
    }
    query_res_transaction  = transaction_collection.insert_one(record_trans)
    return balance


'''
Testing Purpose
'''
# print(CheckUserExists("9493786234"))
# AddSelfHelpGroup("968982900773",["9493786234"],"test_group","vellore",9000)
# SearchSelfHelpGroup("vellore")
# JoinSelfHelpGroup("New_group","8658322524")
# transaction_withdraw("New_group", "9493786234", 1000)
# print(SeeProfile("9515617916"))