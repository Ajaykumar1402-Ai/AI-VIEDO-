import uuid
from fastapi.testclient import TestClient
from app.main import app
from app.database import SessionLocal, engine
from app.models.user import User

client = TestClient(app)
db = SessionLocal()

print("===========================================================")
print("   LIVE POSTGRESQL AUTHENTICATION & SECURITY TEST SUITE   ")
print("===========================================================")

test_email = f"director_{uuid.uuid4().hex[:6]}@sivacine.ai"
test_password = "UltraSecurePassword2026!"
test_name = "Siva Director"

created_user_id = None

try:
    # 1. Test Signup (POST /api/auth/signup)
    print(f"[TEST 1] Registering {test_email}...")
    signup_res = client.post("/api/auth/signup", json={
        "name": test_name,
        "email": test_email,
        "password": test_password
    })
    assert signup_res.status_code == 201, f"Expected 201, got {signup_res.status_code}: {signup_res.text}"
    signup_data = signup_res.json()
    assert signup_data["success"] is True
    assert "access_token" in signup_data
    assert "password_hash" not in signup_data["user"]
    assert signup_data["user"]["email"] == test_email
    created_user_id = signup_data["user"]["id"]
    print(f" -> PASS: User created. ID={created_user_id}")

    # 2. Verify in PostgreSQL directly
    print("[TEST 2] Verifying record directly in PostgreSQL...")
    db_user = db.query(User).filter(User.email == test_email).first()
    assert db_user is not None, "User not found in PostgreSQL!"
    assert db_user.password_hash.startswith("$argon2"), f"Password is not Argon2 hash: {db_user.password_hash}"
    assert test_password not in db_user.password_hash, "Plaintext password leaked in hash field!"
    print(f" -> PASS: Verified Argon2id hash in PostgreSQL: {db_user.password_hash[:30]}...")

    # 3. Duplicate Signup Check (409 Conflict)
    print("[TEST 3] Duplicate signup with same email...")
    dup_res = client.post("/api/auth/signup", json={
        "name": "Duplicate User",
        "email": test_email.upper(),  # test case-insensitive normalization
        "password": "DifferentPassword123!"
    })
    assert dup_res.status_code == 409, f"Expected 409, got {dup_res.status_code}"
    assert "already exists" in dup_res.json()["detail"]
    print(" -> PASS: Duplicate signup rejected with 409 Conflict.")

    # 4. Correct Login (POST /api/auth/login)
    print("[TEST 4] Logging in with correct credentials...")
    login_res = client.post("/api/auth/login", json={
        "email": test_email,
        "password": test_password
    })
    assert login_res.status_code == 200, f"Expected 200, got {login_res.status_code}"
    login_data = login_res.json()
    assert "access_token" in login_data
    token = login_data["access_token"]
    print(f" -> PASS: Login succeeded. JWT token issued.")

    # 5. Invalid Password Login Check (401)
    print("[TEST 5] Logging in with invalid password...")
    wrong_pwd_res = client.post("/api/auth/login", json={
        "email": test_email,
        "password": "WrongPassword123!"
    })
    assert wrong_pwd_res.status_code == 401, f"Expected 401, got {wrong_pwd_res.status_code}"
    assert wrong_pwd_res.json()["detail"] == "Invalid email or password"
    print(" -> PASS: Invalid password rejected with 401 Unauthorized.")

    # 6. Non-existent User Login Check (401 - timing/existence safe)
    print("[TEST 6] Logging in with non-existent email...")
    non_exist_res = client.post("/api/auth/login", json={
        "email": "nonexistent_user_999@sivacine.ai",
        "password": "SomePassword123!"
    })
    assert non_exist_res.status_code == 401, f"Expected 401, got {non_exist_res.status_code}"
    assert non_exist_res.json()["detail"] == "Invalid email or password"
    print(" -> PASS: Non-existent email rejected with identical 401 Unauthorized message.")

    # 7. Authenticated User Profile (GET /api/auth/me)
    print("[TEST 7] Fetching authenticated profile (/api/auth/me)...")
    me_res = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_res.status_code == 200, f"Expected 200, got {me_res.status_code}"
    me_data = me_res.json()
    assert me_data["id"] == created_user_id
    assert me_data["email"] == test_email
    assert "password_hash" not in me_data
    print(f" -> PASS: Correct user profile returned: {me_data['name']} ({me_data['email']})")

    # 8. Unauthenticated Access Check (401)
    print("[TEST 8] Accessing /api/auth/me with clean unauthenticated client...")
    unauth_client = TestClient(app)
    unauth_res = unauth_client.get("/api/auth/me")
    assert unauth_res.status_code == 401, f"Expected 401, got {unauth_res.status_code}"
    print(" -> PASS: Unauthenticated request rejected with 401 Unauthorized.")

    # 9. Logout & Invalidate Cookie Check
    print("[TEST 9] Logging out...")
    logout_res = client.post("/api/auth/logout")
    assert logout_res.status_code == 200
    # After logout, cookie is deleted, so subsequent request without Bearer token must fail with 401
    post_logout_res = client.get("/api/auth/me")
    assert post_logout_res.status_code == 401, f"Expected 401 after logout, got {post_logout_res.status_code}"
    print(" -> PASS: Logout cleared session cookies; subsequent requests return 401.")

    print("\n===========================================================")
    print("   ALL 9 LIVE POSTGRESQL AUTH & SECURITY TESTS PASSED!    ")
    print("===========================================================")

finally:
    # Cleanup test user from PostgreSQL
    if created_user_id:
        user_to_delete = db.query(User).filter(User.id == uuid.UUID(created_user_id)).first()
        if user_to_delete:
            db.delete(user_to_delete)
            db.commit()
            print(f"[CLEANUP] Test user {test_email} safely removed from PostgreSQL.")
    db.close()
