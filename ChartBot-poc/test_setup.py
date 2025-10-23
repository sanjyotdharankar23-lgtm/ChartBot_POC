import requests
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def test_neondb_connection():
    """Test NeonDB connection"""
    try:
        conn = psycopg2.connect(os.getenv('DATABASE_URL'))
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        db_version = cursor.fetchone()
        print("✅ NeonDB: Connected successfully")
        print(f"   Database: {db_version[0]}")
        
        # Check tables
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)
        tables = [table[0] for table in cursor.fetchall()]
        print(f"   Tables: {', '.join(tables)}")
        
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"❌ NeonDB: Connection failed - {e}")
        return False

def test_services():
    """Test if services are running"""
    services = {
        'Chatbot': 'http://localhost:8001/health',
        'Website': 'http://localhost:8002/health',
        'ChromaDB': 'http://localhost:8000/api/v1/heartbeat'
    }
    
    for service, url in services.items():
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"✅ {service}: Running")
            else:
                print(f"⚠️  {service}: HTTP {response.status_code}")
        except Exception as e:
            print(f"❌ {service}: Not reachable - {e}")

def test_openai():
    """Test OpenAI API key"""
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key or api_key == 'your_openai_api_key_here':
        print("❌ OpenAI: API key not configured")
        return False
    
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        models = client.models.list()
        print("✅ OpenAI: API key is valid")
        return True
    except Exception as e:
        print(f"❌ OpenAI: API key invalid - {e}")
        return False

if __name__ == "__main__":
    print("🚀 Testing Access Control System Setup...\n")
    
    print("1. Testing Database Connection...")
    db_ok = test_neondb_connection()
    
    print("\n2. Testing Services...")
    test_services()
    
    print("\n3. Testing OpenAI API...")
    openai_ok = test_openai()
    
    print("\n" + "="*50)
    if db_ok and openai_ok:
        print("🎉 All systems are ready! You can now:")
        print("   - Chatbot: http://localhost:8001")
        print("   - Website: http://localhost:8002")
    else:
        print("⚠️  Some components need attention. Please check the errors above.")