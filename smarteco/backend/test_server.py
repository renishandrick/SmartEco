"""
Minimal FastAPI server to test MongoDB connection
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import asyncio

app = FastAPI(title="SmartEco Test Server")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"status": "ok", "message": "SmartEco Test Server Running"}

@app.get("/api/health")
def health():
    try:
        from database import get_db
        db = get_db()
        return {
            "status": "ok",
            "mongodb": {
                "connected": db.connected,
                "database": "smarteco" if db.connected else None
            }
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }

@app.on_event("startup")
async def startup():
    print("🚀 Starting SmartEco Test Server...")
    try:
        from database import get_db
        db = get_db()
        if db.connect():
            print("✅ MongoDB Atlas connected!")
        else:
            print("⚠️  MongoDB connection failed")
    except Exception as e:
        print(f"❌ Startup error: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
