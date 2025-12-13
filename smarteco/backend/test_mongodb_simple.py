"""
Simple MongoDB Atlas Connection Test
"""
from pymongo import MongoClient

def test_simple_connection():
    """Test MongoDB Atlas connection directly"""
    print("=" * 60)
    print("Testing MongoDB Atlas Connection")
    print("=" * 60)
    
    try:
        # Direct connection test
        client = MongoClient(
            'mongodb+srv://Gcamp_07:Vte2GBUXksVsoLwh@gcamp.avvchjl.mongodb.net/',
            serverSelectionTimeoutMS=5000
        )
        
        # Ping the database
        client.admin.command('ping')
        print("✅ MongoDB Atlas connection successful!")
        
        # Get database
        db = client['smarteco']
        print(f"✅ Database 'smarteco' accessed")
        
        # List collections
        collections = db.list_collection_names()
        print(f"✅ Collections: {collections if collections else '(none yet - will be created on first insert)'}")
        
        # Test insert
        print("\nTesting data insertion...")
        result = db.test_collection.insert_one({"test": "data", "status": "working"})
        print(f"✅ Test document inserted with ID: {result.inserted_id}")
        
        # Test retrieval
        doc = db.test_collection.find_one({"test": "data"})
        print(f"✅ Test document retrieved: {doc}")
        
        # Clean up test
        db.test_collection.delete_one({"test": "data"})
        print("✅ Test document cleaned up")
        
        print("\n" + "=" * 60)
        print("✅ MongoDB Atlas is ready for deployment!")
        print("=" * 60)
        
        client.close()
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

if __name__ == "__main__":
    test_simple_connection()
