import datetime
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
# Import MBBank chỉ khi cần thiết để giảm kích thước ban đầu của lambda function
# from mbbank import MBBank

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
async def get_transaction(
    username: Optional[str] = None,
    password: Optional[str] = None,
    days: int = 30
):
    """
    Get transaction history from MB Bank
    """
    if username is None or password is None:
        raise HTTPException(status_code=400, detail="Username and password are required")
    
    try:
        # Import MBBank only when this endpoint is called
        from mbbank import MBBank
        
        mb = MBBank(username=username, password=password)
        end_query_day = datetime.datetime.now()
        start_query_day = end_query_day - datetime.timedelta(days=days)
        balance = mb.getBalance()
        trans = mb.getTransactionAccountHistory(from_date=start_query_day, to_date=end_query_day)
        
        # Limit the amount of data returned to reduce size
        transactions = trans.get('transactionHistoryList', [])
        # Return only essential fields to reduce response size
        simplified_transactions = []
        
        for t in transactions:
            simplified_transactions.append({
                "transactionId": t.get("transactionId", ""),
                "transactionDate": t.get("transactionDate", ""),
                "accountNo": t.get("accountNo", ""),
                "creditAmount": t.get("creditAmount", 0),
                "debitAmount": t.get("debitAmount", 0),
                "description": t.get("description", ""),
                "availableBalance": t.get("availableBalance", 0),
            })
        
        return {
            "balance": balance,
            "transaction": simplified_transactions
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching transaction data: {str(e)}")


# This is important for Vercel serverless deployment
@app.get("/")
async def root():
    """
    Root endpoint
    """
    return {"message": "Welcome to the API. Go to /docs for documentation."} 