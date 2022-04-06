'''
This python file will have all the routes of the fast api
'''
#imports
from email import message
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import logging
import uvicorn
import shutil
import os
from functions import doSignup

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


if __name__ == "__main__":
    uvicorn.run(
        app,
        port=5000,
        host="127.0.0.1",
    )
