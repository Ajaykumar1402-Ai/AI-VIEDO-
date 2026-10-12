"""
Step 7 Test Script: Comprehensive Database CRUD Verification
Tests connection, insert, read, update, delete in a transaction, ensuring complete cleanup.
"""

import sys
import os
import uuid

# Append app to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal, engine
from app.models.user import User
from app.security import hash_password, verify_password
from sqlalchemy import text

def run_database_tests():
    print("==================================================")
    print("🧪 STEP 7: TESTING POSTGRESQL DATABASE OPERATIONS")
    print("==================================================")

    # 1. Connection check
    print("\n[1/5] Testing PostgreSQL Connection...")
    with engine.connect() as conn:
        version = conn.execute(text("SELECT version();")).scalar()
        print(f"✅ Connection Established! Engine: {version.split(',')[0]}")

    db = SessionLocal()
    test_user_id = None
    test_email = f"test_director_{uuid.uuid4().hex[:8]}@cinema.ai"

    try:
        # 2. Insert test user
        print(f"\n[2/5] Inserting Test User ({test_email})...")
        raw_pwd = "TestSecurePassword123!"
        pwd_hash = hash_password(raw_pwd)

        new_user = User(
            name="Test Filmmaker",
            email=test_email,
            password_hash=pwd_hash,
            auth_provider="local",
            is_active=True
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        test_user_id = new_user.id
        print(f"✅ Insert Successful! User ID: {new_user.id}")
        assert verify_password(raw_pwd, new_user.password_hash), "Password verification failed"
        print("✅ Argon2id password hash verified!")

        # 3. Read test user
        print(f"\n[3/5] Reading User from Database...")
        fetched_user = db.query(User).filter(User.id == test_user_id).first()
        assert fetched_user is not None, "Failed to read inserted user"
        assert fetched_user.email == test_email, "Email mismatch"
        print(f"✅ Read Successful! Found: {fetched_user.name} <{fetched_user.email}>")

        # 4. Update test user
        print(f"\n[4/5] Updating User Field...")
        fetched_user.name = "Updated Director Master"
        db.commit()
        db.refresh(fetched_user)

        updated_user = db.query(User).filter(User.id == test_user_id).first()
        assert updated_user.name == "Updated Director Master", "Update failed"
        print(f"✅ Update Successful! New name: {updated_user.name}")

        # 5. Delete test user
        print(f"\n[5/5] Deleting Test User (Cleanup)...")
        db.delete(updated_user)
        db.commit()

        deleted_check = db.query(User).filter(User.id == test_user_id).first()
        assert deleted_check is None, "Cleanup delete failed"
        print(f"✅ Delete & Cleanup Successful! Record completely removed.")

        print("\n==================================================")
        print("🎉 ALL 5 DATABASE CRUD OPERATIONS PASSED!")
        print("==================================================")

    except Exception as e:
        db.rollback()
        print(f"❌ Database test failed: {e}")
        raise
    finally:
        # Guarantee cleanup if failed mid-way
        if test_user_id:
            try:
                db.query(User).filter(User.id == test_user_id).delete()
                db.commit()
            except Exception:
                pass
        db.close()

if __name__ == "__main__":
    run_database_tests()
