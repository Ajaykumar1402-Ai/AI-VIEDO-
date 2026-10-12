"""
Step 11 Verification Test Suite: Complete FastAPI & PostgreSQL Auth Endpoints
"""

import sys
import os
import uuid
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.main import app
from app.database import Base, get_db
from app.models.user import User

# Setup isolated test database
TEST_DB_URL = "sqlite:///./test_auth.db"
test_engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

def override_get_db():
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

def test_full_auth_suite():
    print("==================================================")
    print("[TEST SUITE] RUNNING FASTAPI AUTHENTICATION TESTS")
    print("==================================================")

    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)

    # 1. Signup
    test_email = f"director_{uuid.uuid4().hex[:6]}@sivacine.ai"
    test_pwd = "SuperSecretPassword2026!"
    print(f"\n[TEST 1] POST /api/auth/signup with {test_email}")
    res = client.post("/api/auth/signup", json={
        "name": "Siva Krishna",
        "email": test_email,
        "password": test_pwd
    })
    print(f"Status: {res.status_code}, Body: {res.json()}")
    assert res.status_code == 201, "Signup failed"
    data = res.json()
    assert "access_token" in data
    assert data["user"]["email"] == test_email
    assert "password_hash" not in data["user"]
    token = data["access_token"]

    # 2. Duplicate Signup Rejection (409 Conflict)
    print(f"\n[TEST 2] Duplicate signup with same email (Expect 409 Conflict)")
    res_dup = client.post("/api/auth/signup", json={
        "name": "Siva Krishna Duplicate",
        "email": test_email,
        "password": test_pwd
    })
    print(f"Status: {res_dup.status_code}, Detail: {res_dup.json()['detail']}")
    assert res_dup.status_code == 409, "Duplicate email not rejected"

    # 3. Login with Correct Credentials
    print(f"\n[TEST 3] POST /api/auth/login (Correct credentials)")
    res_login = client.post("/api/auth/login", json={
        "email": test_email,
        "password": test_pwd
    })
    print(f"Status: {res_login.status_code}, Body: {res_login.json()}")
    assert res_login.status_code == 200, "Login failed"
    login_token = res_login.json()["access_token"]

    # 4. Login with Incorrect Password (Expect 401)
    print(f"\n[TEST 4] POST /api/auth/login (Incorrect password - Expect 401)")
    res_bad_login = client.post("/api/auth/login", json={
        "email": test_email,
        "password": "WrongPassword123!"
    })
    print(f"Status: {res_bad_login.status_code}, Detail: {res_bad_login.json()['detail']}")
    assert res_bad_login.status_code == 401, "Invalid password not rejected"

    # 5. GET /api/auth/me Authenticated
    print(f"\n[TEST 5] GET /api/auth/me (Authenticated with Bearer token)")
    res_me = client.get("/api/auth/me", headers={"Authorization": f"Bearer {login_token}"})
    print(f"Status: {res_me.status_code}, User: {res_me.json()}")
    assert res_me.status_code == 200, "/api/auth/me failed"
    assert res_me.json()["email"] == test_email

    # 6. GET /api/auth/me Unauthenticated (Expect 401)
    print(f"\n[TEST 6] GET /api/auth/me (Unauthenticated - Expect 401)")
    client.cookies.clear()
    res_unauth = client.get("/api/auth/me")
    print(f"Status: {res_unauth.status_code}, Detail: {res_unauth.json().get('detail')}")
    assert res_unauth.status_code == 401, "Unauthenticated request was not rejected"

    # 7. POST /api/auth/logout
    print(f"\n[TEST 7] POST /api/auth/logout")
    res_logout = client.post("/api/auth/logout")
    print(f"Status: {res_logout.status_code}, Response: {res_logout.json()}")
    assert res_logout.status_code == 200, "Logout failed"

    print("\n==================================================")
    print("[SUCCESS] ALL 7 FASTAPI AUTH TESTS PASSED!")
    print("==================================================")

    if os.path.exists("./test_auth.db"):
        try:
            os.remove("./test_auth.db")
        except Exception:
            pass

if __name__ == "__main__":
    test_full_auth_suite()
