import uvicorn
import sys
import os

# Add the current directory to Python path so imports work
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def main():
    """Run the FastAPI development server"""
    
    print("🚀 Starting Resume Screening AI Backend...")
    print("📍 Current directory:", os.getcwd())
    
    # Import here to avoid circular imports
    from app.core.config import settings
    from app.core.database import test_db_connection, create_tables
    
    # Test database connection
    print("📊 Testing database connection...")
    if test_db_connection():
        print("✅ Database connection successful")
        
        # Create tables if they don't exist
        print("🗄️  Creating database tables...")
        try:
            create_tables()
            print("✅ Database tables ready")
        except Exception as e:
            print(f"❌ Error creating tables: {e}")
            print("   Continuing anyway - you can set up database later")
    else:
        print("⚠️  Database connection failed - continuing without database")
        print("   You can configure PostgreSQL later")
    
    # Check API keys
    if not settings.google_api_key:
        print("⚠️  Warning: No Google API key configured")
        print("   Add GOOGLE_API_KEY to .env file from https://aistudio.google.com/")
    else:
        print("✅ Google AI API key configured")
    
    print(f"\n🌐 Starting server...")
    print(f"   API: http://localhost:8000")
    print(f"   Documentation: http://localhost:8000/docs")
    print(f"   Health Check: http://localhost:8000/health")
    print(f"   Config Test: http://localhost:8000/test-config")
    print(f"\n🔧 Debug mode: {settings.debug}")
    print("   Press Ctrl+C to stop the server")
    
    # Run the server
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level="info" if settings.debug else "warning"
    )

if __name__ == "__main__":
    main()