"""Main application entry point for SpendSense."""

import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from src.config import config
from src.agents import agent
from src.models import Transaction, TransactionType, TransactionCategory

# Configure logging
logging.basicConfig(level=config.LOG_LEVEL)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="SpendSense",
    description="Personal Budgeting & Financial Decision AI Agent",
    version="0.1.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to SpendSense - Your Personal Budgeting AI Agent",
        "version": "0.1.0",
        "status": "active",
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


@app.post("/transactions")
async def add_transaction(
    user_id: str,
    description: str,
    amount: float,
    transaction_type: TransactionType = TransactionType.EXPENSE,
    category: str = None,
):
    """Add a new transaction."""
    try:
        if category is None:
            # Auto-categorize if not provided
            from src.utils import categorize_transaction

            category = categorize_transaction(description, amount)

        transaction = Transaction(
            user_id=user_id,
            description=description,
            amount=amount,
            transaction_type=transaction_type,
            category=category,
            date=datetime.now(),
        )

        success = agent.add_transaction(user_id, transaction)

        if success:
            return {
                "message": "Transaction added successfully",
                "transaction": transaction.dict(),
            }
        else:
            raise HTTPException(status_code=400, detail="Failed to add transaction")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/spending/{user_id}")
async def get_spending_analysis(user_id: str, period: str = "monthly"):
    """Get spending analysis for user."""
    try:
        analysis = agent.analyze_spending(user_id, period)
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/recommendations/{user_id}")
async def get_financial_recommendations(user_id: str):
    """Get personalized financial recommendations."""
    try:
        recommendations = agent.get_recommendations(user_id)
        return {
            "user_id": user_id,
            "recommendations": recommendations,
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/budget")
async def set_budget(user_id: str, category: str, limit: float):
    """Set a budget for a category."""
    try:
        success = agent.set_budget(user_id, category, limit)

        if success:
            return {
                "message": "Budget set successfully",
                "user_id": user_id,
                "category": category,
                "limit": limit,
            }
        else:
            raise HTTPException(status_code=400, detail="Failed to set budget")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/dashboard/{user_id}")
async def get_dashboard(user_id: str):
    """Get comprehensive dashboard for user."""
    try:
        spending = agent.analyze_spending(user_id, "monthly")
        recommendations = agent.get_recommendations(user_id)

        return {
            "user_id": user_id,
            "spending_analysis": spending,
            "recommendations": recommendations,
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    logger.info(f"Starting SpendSense API on port {config.PORT}")
    uvicorn.run(
        app, host="0.0.0.0", port=config.PORT, log_level=config.LOG_LEVEL.lower()
    )
