'''
This python file will have all the routes of the fast api
'''
#imports
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import logging
import uvicorn
import shutil
import os
from functions import *

logging.basicConfig(
    level=logging.INFO, format="[%(asctime)s] %(levelname)s: %(message)s"
)
logger = logging.getLogger(__name__)
logging.getLogger("pipeline").setLevel(logging.INFO)

app = FastAPI(title="Sahayata", version="1.0.0")

#allowing the API to all the specefic orgins
origins = [
    "http://localhost:3000",
    "http://localhost",
    "http://localhost:8080",
]

#CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
class signupRequest(BaseModel):
    name: str
    phone_number: str
    password: str
    age: int
    location: str
    annual_income: int

class withdrawRequest(BaseModel):
    shg_name: str
    phone_number: str
    amount: int


class searchRequest(BaseModel):
    location: str

class joinShgRequest(BaseModel):
    shg_name: str
    user_phone_number :str

class transactionDepositRequest(BaseModel):
    shg_name :str
    user_phone_number :str 
    amount :int 



    
@app.get("/")
def root():
    logging.info("This api is up")
    return JSONResponse(
        status_code=200,
        content={
            "message": "The API is alive"
        }
    )

@app.post("/signup/")
def signup(
    aadhar: UploadFile = File(...),
    pan: UploadFile = File(...),
    name: str = Form(...),
    phone_number: str = Form(...),
    password: str = Form(...),
    age: int = Form(...),
    location: str = Form(...),
    annual_income: int = Form(...)):

    aadhar_filename = aadhar.filename
    pan_filename = pan.filename

    name = name
    phone_number = phone_number
    password = password
    age = age
    location = location
    annual_income = annual_income
    path_aadhar = "Aadhar_files"
    path_pan = "Pan_files"
    path_aadhar_final = os.path.join(path_aadhar,aadhar_filename)
    path_pan_final = os.path.join(path_pan,pan_filename)

    try:
        logging.info("saving the aadhar and pan")
        with open(path_aadhar_final,"wb") as buffer:
            shutil.copyfileobj(aadhar.file, buffer)     
        with open(path_pan_final,"wb") as buffer1:
            shutil.copyfileobj(pan.file, buffer1)      
        logging.info("saved!!")
    except Exception as e:
        logging.error(e)
        logging.error("the file saving process didnt work properly")

    doSignup(name=name, phone_number=phone_number, password=password, age=age, location=location, annual_income=annual_income, aadhar_path=path_aadhar_final, pan_path=path_pan_final)

    return JSONResponse(
        status_code=200,
        content={
            "message": "Signed Up successfully",
            "signup_result": 1
        }
    )

@app.post("/createshg")
def createshg(
    name: str = Form(...),
    admin_phone_number: str = Form(...),
    member_phone_number_list: list = Form(...),
    location: str = Form(...),
    initial_balance: int = Form(...)):

    name = name
    admin_phone_number = admin_phone_number
    location = location
    initial_balance = initial_balance
    member_phone_number_list =  member_phone_number_list
    
    try:
        result = AddSelfHelpGroup(admin_phone_number= admin_phone_number, 
                        member_phone_number_list = member_phone_number_list, 
                        name= name, 
                        location=location, 
                        initial_balance=initial_balance)

        return JSONResponse(
            status_code=200,
            content={
                "message": result,
                "shg_creation_result": 1
            }
        )
    except Exception as e:
        return JSONResponse(
            status_code=404,
            content={
                "message": "didnt work properly",
                "shg_creation_result": 0
            }
        )

#This api will search the shgs 
'''
Function to be used --
    SearchSelfHelpGroup() <-- Takes the input of location in string
        Returns int(0) if there is no groups exist
        Else would return the list of groups recommended for the particular area

NOTE: To use Pydantic (BaseModel class)

'''
@app.post("/searchShg")
def searchShg(req:searchRequest):
    location = req.location
    try:
        result= SearchSelfHelpGroup(location)
    except Exception as e:
        logging.error(e)
        logging.error("error in search shg function")
    
    if len(result)==0:
        return JSONResponse(
            status_code=404,
            content={
                "message": "didnt work properly",
                "shg_search_result": "not found"
            }
        )
    else:
        print(result)
        #json_list = json.dumps(result)

        return JSONResponse(
            status_code=200,
            content={
                "message":result
            }
        )
    

#This api will facilitiate the joining process of a person in a SHG
'''
Function to be used,
    JoinSelfHelpGroup() <-- Takes the input of the self help group name and the phonenumber of the person to be added
        Returns the integer (0) if the person is or the shg group doesnt exist
        Else, would return integer (1) if the person joined the SHG

NOTE: To use Pydantic (BaseModel class)
'''
@app.post("/joinShg")
def joinSelfHelpGroup(req: joinShgRequest):
    shg_name= req.shg_name
    user_phone_number=req.user_phone_number

    try:
        result = JoinSelfHelpGroup(shg_name,user_phone_number)
    except Exception as e:
        logging.error(e)
        logging.error("error in join group function")

    if result:
        return JSONResponse(
            status_code=200,
            content= {
                "message":"Successfully joined!",
                "joining_result": 1
            }
        )
    else:
        return JSONResponse(
            status_code=400,
            content= {
                "message":" Error in joining!",
                "joining_result": 0
            }
        )


#This api will transaction process for transacting the amount
@app.post("/depositAmount")
def depositAmount(req: transactionDepositRequest):
    shg_name =req.shg_name
    user_phone_number = req.user_phone_number
    amount= req.amount
    try:
        result= transaction_deposit(shg_name=shg_name,phone_number=user_phone_number,amount=amount)
    except Exception as e:
        logging.error(e)
        logging.error("error in amount deposit function")
    
    if result==-1:
        return JSONResponse(
            status_code=400,
            content= {
                "message":" Error in transacting amount",
                "transaction_result": 0
            }
        )
    else:
        return JSONResponse(
            status_code=200,
            content= {
                "message":"transaction successful",
                "balance":result,
                "transaction_result": 1
            }
        )
#This api will give the user details in the profile page
@app.post("/userProfile")
def userProfile(phone_number: str = Form(...)):
    try:
        result = SeeProfile(phone_number=phone_number)
    except Exception as e:
        logging.error(e)
        logging.error("Error in accessing user information")

    if result==0:
        return JSONResponse(
            status_code=404,
            content={
                "message":"Error in accessing user information",
                "user_profile_result" :0
            }
        )
    elif not bool(result):
        return JSONResponse(
            status_code=404,
            content={
                "message":"Error in accessing user information, returning empty dict()",
                "user_profile_result" :0
            }
        )
    else:
        return JSONResponse(
            status_code=200,
            content={
                "message": "Successfully received user information",
                "user_profile" :result,
                "user_profile_result":1
            }
        )


# This route will help in withdrawing the amount from the SHG
'''
Takes the input of SHG name, phone number of the user and amount to be withdrawn
'''
@app.post("/withdrawAmount")
def withdraw(req: withdrawRequest):
    shg_name = req.shg_name
    phone_number = req.phone_name
    amount = req.amount

    try:
        result = transaction_withdraw(shg_name, phone_number, amount)
    except Exception as e:
        logging.error(e)
        logging.error("error in executing the transaction")

    if result==-1:
        return JSONResponse(
            status_code=404,
            content={
                "message": "There was an error in the transaction",
                "transaction_result": 0
            }
        )
    else:
        return JSONResponse(
            status_code= 200,
            content={
                "message": "Transaction Successful",
                "balance": result,
                "transaction_result": 1
            }
        )
if __name__ == "__main__":
    uvicorn.run(
        app,
        port=5000,
        host="127.0.0.1",
    )
