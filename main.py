import datetime
from typing import Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

# Cache cho session MBBank để tránh khởi tạo lại
mbbank_sessions = {}

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
    days: int = Query(default=30, le=100)  # Limit max days to 60
):
    """
    Get transaction history from MB Bank
    """
    if username is None or password is None:
        raise HTTPException(status_code=400, detail="Username and password are required")
    
    try:
        # Tạo cache key từ username (không lưu password)
        cache_key = f"mb_{username}"
        
        # Import MBBank only when this endpoint is called
        from mbbank import MBBank
        
        # Kiểm tra session trong cache
        if cache_key in mbbank_sessions:
            mb = mbbank_sessions[cache_key]
            # Kiểm tra xem session có còn hợp lệ không
            try:
                # Thử lấy thông tin để kiểm tra session
                mb.getBalance()
            except:
                # Nếu session hết hạn, tạo mới session
                mb = MBBank(username=username, password=password)
                mbbank_sessions[cache_key] = mb
        else:
            # Tạo session mới và lưu vào cache
            mb = MBBank(username=username, password=password)
            mbbank_sessions[cache_key] = mb
        
        # Get balance first as a separate operation
        try:
            balance = mb.getBalance()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error fetching balance: {str(e)}")
        
        # Get transactions with limited date range
        end_query_day = datetime.datetime.now()
        start_query_day = end_query_day - datetime.timedelta(days=min(days, 60))  # Ensure max 60 days
        
        try:
            trans = mb.getTransactionAccountHistory(from_date=start_query_day, to_date=end_query_day)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error fetching transactions: {str(e)}")
        
        # Limit the amount of data returned to reduce size
        transactions = trans.get('transactionHistoryList', [])
        
        # Limit number of transactions to maximum 100
        transactions = transactions[:100] if len(transactions) > 100 else transactions
        
        # Return only essential fields to reduce response size
        simplified_transactions = []
        
        for t in transactions:
            # Only include transactions with actual monetary value
            if t.get("creditAmount", 0) > 0 or t.get("debitAmount", 0) > 0:
                simplified_transactions.append({
                    "id": t.get("transactionId", "")[:10],  # Truncate ID
                    "date": t.get("transactionDate", ""),
                    "credit": t.get("creditAmount", 0),
                    "debit": t.get("debitAmount", 0),
                    "desc": t.get("description", "")[:100] if t.get("description") else "",  # Truncate description
                    "balance": t.get("availableBalance", 0),
                })
        
        return {
            "balance": balance,
            "count": len(simplified_transactions),
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