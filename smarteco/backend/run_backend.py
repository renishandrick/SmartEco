"""
SmartEco Backend Startup Script
Runs uvicorn directly with proper configuration
"""
import uvicorn

if __name__ == "__main__":
    print("=" * 60)
    print("Starting SmartEco Backend with MongoDB Atlas")
    print("=" * 60)
    print()
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
