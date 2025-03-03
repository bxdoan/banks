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

# This is important for Vercel serverless deployment
@app.get("/")
async def root():
    """
    Root endpoint
    """
    return {"message": "Welcome to the API. Go to /docs for documentation."} 