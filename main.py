import datetime
import os
from mbbank import MBBank

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Health Check API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    """
    Health check endpoint to verify the API is running
    """
    return {"status": "healthy", "message": "API is running"}


@app.get("/transaction")
def get_transaction(
    username:str=None,
    password:str=None,
    days:int=30
):
    if username is None or password is None:
        return {"error": "Username and password are required"}
    mb = MBBank(username=username, password=password)
    end_query_day = datetime.datetime.now()
    start_query_day = end_query_day - datetime.timedelta(days=days)
    balance = mb.getBalance()
    trans = mb.getTransactionAccountHistory(from_date=start_query_day, to_date=end_query_day)
    return {
        "balance": balance,
        "transaction": trans['transactionHistoryList']
    }


# This is important for Vercel serverless deployment
@app.get("/")
async def root():
    """
    Root endpoint
    """
    return {"message": "Welcome to the API. Go to /docs for documentation."} 