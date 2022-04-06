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
    "http://34.222.224.208/",
    "http://smartrecon.finstinct.com/",
]

#CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return JSONResponse(
        status_code=200,
        content={
            "message": "The API is alive"
        }
    )

if __name__ == "__main__":
    uvicorn.run(
        app,
        port=5000,
        host="127.0.0.1",
    )
