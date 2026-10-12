/**
 * Comprehensive Automated Test Suite for Google & GitHub OAuth + PostgreSQL Persistence
 */

const http = require("http");
const https = require("https");
const { Pool } = require("pg");
const crypto = require("crypto");
const jwt = require("jsonwebtoken");

const JWT_SECRET = "sivacine_storytelling_super_secret_jwt_key_2026";
const pgPool = new Pool({
  host: "localhost",
  port: 5432,
  user: "storytelling_app",
  password: "storytelling_pass_2026",
  database: "storytelling_db"
});

function makeRequest(url, options = {}) {
  return new Promise((resolve, reject) => {
    const parsedUrl = new URL(url);
    const req = http.request(url, options, (res) => {
      let body = "";
      res.on("data", chunk => body += chunk);
      res.on("end", () => {
        resolve({
          status: res.statusCode,
          headers: res.headers,
          body: body
        });
      });
    });
    req.on("error", reject);
    if (options.data) {
      req.write(typeof options.data === "string" ? options.data : JSON.stringify(options.data));
    }
    req.end();
  });
}

async function runTests() {
  console.log("===========================================================");
  console.log("   SIVACINE AI &bull; OAUTH 2.0 & POSTGRESQL TEST SUITE   ");
  console.log("===========================================================\n");

  const createdUserIds = [];

  try {
    // -----------------------------------------------------------------
    // TEST 1: Google OAuth Initiation (GET /auth/google)
    // -----------------------------------------------------------------
    console.log("[TEST 1] Testing Google OAuth Initiation (GET /auth/google)...");
    const googleInit = await makeRequest("http://localhost:5000/auth/google", { method: "GET" });
    if (googleInit.status !== 302) throw new Error(`Expected 302 redirect, got ${googleInit.status}`);
    
    const googleLoc = googleInit.headers.location;
    if (!googleLoc || !googleLoc.startsWith("https://accounts.google.com/o/oauth2/v2/auth")) {
      throw new Error(`Invalid Google Auth URL: ${googleLoc}`);
    }
    if (!googleLoc.includes("client_id=") || !googleLoc.includes("redirect_uri=") || !googleLoc.includes("state=")) {
      throw new Error(`Missing OAuth parameters in Google redirect URL: ${googleLoc}`);
    }
    const googleCookie = googleInit.headers["set-cookie"] ? googleInit.headers["set-cookie"][0] : "";
    if (!googleCookie.includes("oauth_state=")) {
      throw new Error("Missing oauth_state cookie in Google init response");
    }
    console.log(" -> PASS: Google OAuth initiation redirects to Google with CSRF state and scopes.");

    // -----------------------------------------------------------------
    // TEST 2: GitHub OAuth Initiation (GET /auth/github)
    // -----------------------------------------------------------------
    console.log("[TEST 2] Testing GitHub OAuth Initiation (GET /auth/github)...");
    const githubInit = await makeRequest("http://localhost:5000/auth/github", { method: "GET" });
    if (githubInit.status !== 302) throw new Error(`Expected 302 redirect, got ${githubInit.status}`);

    const githubLoc = githubInit.headers.location;
    if (!githubLoc || !githubLoc.startsWith("https://github.com/login/oauth/authorize")) {
      throw new Error(`Invalid GitHub Auth URL: ${githubLoc}`);
    }
    if (!githubLoc.includes("client_id=") || !githubLoc.includes("redirect_uri=") || !githubLoc.includes("state=")) {
      throw new Error(`Missing OAuth parameters in GitHub redirect URL: ${githubLoc}`);
    }
    console.log(" -> PASS: GitHub OAuth initiation redirects to GitHub with CSRF state and scopes.");

    // -----------------------------------------------------------------
    // TEST 3: CSRF State Mismatch Protection
    // -----------------------------------------------------------------
    console.log("[TEST 3] Testing CSRF State Validation & Attack Rejection...");
    const badStateRes = await makeRequest("http://localhost:5000/auth/google/callback?code=fake_code&state=forged_state_123", {
      headers: { Cookie: "oauth_state=legitimate_state_456" }
    });
    if (!badStateRes.headers.location || !badStateRes.headers.location.includes("auth_error=state_mismatch")) {
      throw new Error(`Expected state mismatch redirect, got ${badStateRes.headers.location}`);
    }
    console.log(" -> PASS: State mismatch correctly detected and rejected with auth_error=state_mismatch.");

    // -----------------------------------------------------------------
    // TEST 4: OAuth Denial / User Cancellation
    // -----------------------------------------------------------------
    console.log("[TEST 4] Testing User Cancellation Handling...");
    const cancelRes = await makeRequest("http://localhost:5000/auth/google/callback?error=access_denied", {});
    if (!cancelRes.headers.location || !cancelRes.headers.location.includes("auth_error=cancelled_by_user")) {
      throw new Error(`Expected cancellation redirect, got ${cancelRes.headers.location}`);
    }
    const ghCancelRes = await makeRequest("http://localhost:5000/auth/github/callback?error=access_denied", {});
    if (!ghCancelRes.headers.location || !ghCancelRes.headers.location.includes("auth_error=github_cancelled")) {
      throw new Error(`Expected cancellation redirect, got ${ghCancelRes.headers.location}`);
    }
    console.log(" -> PASS: User cancellations handled gracefully with user-friendly error codes.");

    // -----------------------------------------------------------------
    // TEST 5: Google First-Time User Persistence in PostgreSQL
    // -----------------------------------------------------------------
    console.log("[TEST 5] Testing Google User Creation & PostgreSQL Persistence...");
    const db = require("./database");
    await db.initDatabase({
      DB_HOST: "localhost",
      DB_PORT: 5432,
      DB_USER: "storytelling_app",
      DB_PASSWORD: "storytelling_pass_2026",
      DB_NAME: "storytelling_db"
    });

    const mockGoogleId = `google_sub_${crypto.randomBytes(6).toString("hex")}`;
    const mockGoogleEmail = `google_creator_${crypto.randomBytes(4).toString("hex")}@gmail.com`;
    const mockGoogleName = "Google Visionary Director";

    const gUser = await db.createOrUpdateGoogleUser({
      googleId: mockGoogleId,
      email: mockGoogleEmail,
      name: mockGoogleName,
      avatar: "https://lh3.googleusercontent.com/a/mockavatar",
      emailVerified: true
    });

    if (!gUser || !gUser.id) throw new Error("Google user creation failed");
    createdUserIds.push(gUser.id);

    // Verify record in PostgreSQL directly
    const pgCheckG = await pgPool.query("SELECT * FROM users WHERE id = $1", [gUser.id]);
    if (pgCheckG.rows.length === 0) throw new Error("User was not found in PostgreSQL users table!");
    const dbRowG = pgCheckG.rows[0];
    if (dbRowG.email !== mockGoogleEmail || dbRowG.auth_provider !== "google" || dbRowG.provider_subject !== mockGoogleId) {
      throw new Error(`PostgreSQL columns mismatch: ${JSON.stringify(dbRowG)}`);
    }
    console.log(` -> PASS: Google user created in PostgreSQL (ID=${gUser.id}, email=${gUser.email}, provider=${gUser.provider}).`);

    // -----------------------------------------------------------------
    // TEST 6: Google Returning User / Account Linking
    // -----------------------------------------------------------------
    console.log("[TEST 6] Testing Google Returning User Login...");
    const returningGUser = await db.createOrUpdateGoogleUser({
      googleId: mockGoogleId,
      email: mockGoogleEmail,
      name: "Google Director Updated",
      avatar: "https://lh3.googleusercontent.com/a/mockavatar2",
      emailVerified: true
    });
    if (returningGUser.id !== gUser.id) throw new Error("Returning user generated new ID instead of linking!");
    console.log(" -> PASS: Returning Google user correctly authenticated to existing account.");

    // -----------------------------------------------------------------
    // TEST 7: GitHub First-Time User Persistence in PostgreSQL
    // -----------------------------------------------------------------
    console.log("[TEST 7] Testing GitHub User Creation & PostgreSQL Persistence...");
    const mockGhId = `${Math.floor(10000000 + Math.random() * 90000000)}`;
    const mockGhEmail = `gh_coder_${crypto.randomBytes(4).toString("hex")}@github.com`;
    const mockGhName = "Cinematic Octocat";

    const ghUser = await db.createOrUpdateGitHubUser({
      githubId: mockGhId,
      email: mockGhEmail,
      name: mockGhName,
      avatar: "https://avatars.githubusercontent.com/u/mock"
    });

    if (!ghUser || !ghUser.id) throw new Error("GitHub user creation failed");
    createdUserIds.push(ghUser.id);

    const pgCheckGH = await pgPool.query("SELECT * FROM users WHERE id = $1", [ghUser.id]);
    if (pgCheckGH.rows.length === 0) throw new Error("GitHub user not found in PostgreSQL!");
    const dbRowGH = pgCheckGH.rows[0];
    if (dbRowGH.auth_provider !== "github" || dbRowGH.provider_subject !== mockGhId) {
      throw new Error(`PostgreSQL GitHub row mismatch: ${JSON.stringify(dbRowGH)}`);
    }
    console.log(` -> PASS: GitHub user created in PostgreSQL (ID=${ghUser.id}, email=${ghUser.email}, subject=${ghUser.provider_id}).`);

    // -----------------------------------------------------------------
    // TEST 8: JWT Token Generation & Verification
    // -----------------------------------------------------------------
    console.log("[TEST 8] Testing JWT Signing & FastAPI Interoperability...");
    const token = jwt.sign(
      {
        sub: String(gUser.id),
        id: String(gUser.id),
        email: gUser.email,
        name: gUser.name,
        provider: "google"
      },
      JWT_SECRET,
      { expiresIn: "7d" }
    );

    // Test Node.js /auth/me
    const nodeMe = await makeRequest("http://localhost:5000/auth/me", {
      headers: { Authorization: `Bearer ${token}` }
    });
    if (nodeMe.status !== 200) throw new Error(`Node /auth/me failed: ${nodeMe.status}`);
    const nodeMeData = JSON.parse(nodeMe.body);
    if (!nodeMeData.success || nodeMeData.user.email !== mockGoogleEmail) {
      throw new Error(`Node /auth/me returned invalid data: ${nodeMe.body}`);
    }
    console.log(" -> PASS: Node.js /auth/me authenticated successfully via Bearer token.");

    // Test FastAPI /api/auth/me using the same token
    const fastapiMe = await makeRequest("http://127.0.0.1:8000/api/auth/me", {
      headers: { Authorization: `Bearer ${token}` }
    });
    if (fastapiMe.status !== 200) throw new Error(`FastAPI /api/auth/me rejected token: ${fastapiMe.status} ${fastapiMe.body}`);
    const pyMeData = JSON.parse(fastapiMe.body);
    if (pyMeData.email !== mockGoogleEmail || pyMeData.id !== gUser.id) {
      throw new Error(`FastAPI profile mismatch: ${fastapiMe.body}`);
    }
    console.log(" -> PASS: FastAPI verified the OAuth JWT seamlessly and loaded user from PostgreSQL.");

    // -----------------------------------------------------------------
    // TEST 9: Protected Route Rejection & Logout
    // -----------------------------------------------------------------
    console.log("[TEST 9] Testing Unauthenticated Rejection & Logout...");
    const unauthNode = await makeRequest("http://localhost:5000/auth/me");
    if (unauthNode.status !== 401) throw new Error("Expected 401 for unauthenticated /auth/me");

    const logoutRes = await makeRequest("http://localhost:5000/auth/logout", { method: "POST" });
    if (logoutRes.status !== 200) throw new Error("Logout failed");
    console.log(" -> PASS: Unauthenticated rejection & logout verified.");

    console.log("\n===========================================================");
    console.log("   ALL 9 OAUTH & POSTGRESQL AUTOMATED TESTS PASSED!       ");
    console.log("===========================================================");

  } finally {
    // Clean up created test users
    for (const uid of createdUserIds) {
      await pgPool.query("DELETE FROM users WHERE id = $1", [uid]).catch(() => {});
    }
    console.log(`[CLEANUP] Safely cleaned up ${createdUserIds.length} test records from PostgreSQL.`);
    await pgPool.end();
  }
}

runTests().catch(err => {
  console.error("TEST FAILED:", err);
  process.exit(1);
});
