import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import os
from dotenv import load_dotenv

load_dotenv()

def init_database():
    try:
        # Connect to NeonDB
        conn = psycopg2.connect(os.getenv('DATABASE_URL'))
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Read and execute SQL file
        with open('init/init_db.sql', 'r', encoding='utf-8') as file:
            sql_commands = file.read()
            
            # Split commands by semicolon, but be careful with PL/pgSQL
            commands = sql_commands.split(';')
            
            for command in commands:
                if command.strip():
                    try:
                        cursor.execute(command)
                        print(f"✅ Executed: {command.strip()[:50]}...")
                    except Exception as e:
                        print(f"⚠️  Could not execute: {command.strip()[:50]}... Error: {e}")
                        continue
        
        cursor.close()
        conn.close()
        print("✅ Database initialized successfully!")
        
    except Exception as e:
        print(f"❌ Database initialization error: {e}")

def test_connection():
    try:
        conn = psycopg2.connect(os.getenv('DATABASE_URL'))
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        db_version = cursor.fetchone()
        print(f"✅ Connected to: {db_version[0]}")
        
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)
        tables = cursor.fetchall()
        print("📊 Tables created:", [table[0] for table in tables])
        
        # Test data counts
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        print(f"👥 Users in database: {user_count}")
        
        cursor.execute("SELECT COUNT(*) FROM projects")
        project_count = cursor.fetchone()[0]
        print(f"📁 Projects in database: {project_count}")
        
        cursor.execute("SELECT COUNT(*) FROM adgroups")
        adgroup_count = cursor.fetchone()[0]
        print(f"🔐 AD Groups in database: {adgroup_count}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Connection test failed: {e}")

if __name__ == "__main__":
    print("🚀 Testing database connection...")
    test_connection()
    
    print("\n🗃️ Initializing database with 9 tables...")
    init_database()
    
    print("\n✅ Final database state:")
    test_connection()