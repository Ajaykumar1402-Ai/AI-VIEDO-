/**
 * SIVACINE AI &bull; Production OAuth 2.0 Backend Authentication Server
 * Implements: Google OAuth 2.0, GitHub OAuth 2.0, JWT Tokens, CSRF State Protection, and MySQL / Fallback DB.
 */

const http = require("http");
const https = require("https");
const url = require("url");
const crypto = require("crypto");
const fs = require("fs");
const path = require("path");
const db = require("./database");

// ===================================================================
// 1. CONFIGURATION & ENVIRONMENT
// ===================================================================
const envFilePath = path.join(__dirname, ".env");
const envVars = {};

if (fs.existsSync(envFilePath)) {
  const envContent = fs.readFileSync(envFilePath, "utf-8");
  envContent.split("\n").forEach(line => {
    const trimmed = line.trim();
    if (trimmed && !trimmed.startsWith("#")) {
      const [key, ...vals] = trimmed.split("=");
      if (key) envVars[key.trim()] = vals.join("=").trim();
    }
  });
}

const PORT = parseInt(process.env.PORT || envVars.PORT || "5000", 10);
const CLIENT_URL = process.env.CLIENT_URL || envVars.CLIENT_URL || "http://localhost:3000";
const JWT_SECRET = process.env.JWT_SECRET || envVars.JWT_SECRET || "sivacine_jwt_secret_2026_filmmaker_key";
const NODE_ENV = process.env.NODE_ENV || envVars.NODE_ENV || "development";

// Google OAuth Credentials
const GOOGLE_CLIENT_ID = process.env.GOOGLE_CLIENT_ID || envVars.GOOGLE_CLIENT_ID || "";
const GOOGLE_CLIENT_SECRET = process.env.GOOGLE_CLIENT_SECRET || envVars.GOOGLE_CLIENT_SECRET || "";
const GOOGLE_CALLBACK_URL = process.env.GOOGLE_CALLBACK_URL || envVars.GOOGLE_CALLBACK_URL || `http://localhost:${PORT}/auth/google/callback`;

// GitHub OAuth Credentials
const GITHUB_CLIENT_ID = process.env.GITHUB_CLIENT_ID || envVars.GITHUB_CLIENT_ID || "";
const GITHUB_CLIENT_SECRET = process.env.GITHUB_CLIENT_SECRET || envVars.GITHUB_CLIENT_SECRET || "";
const GITHUB_CALLBACK_URL = process.env.GITHUB_CALLBACK_URL || envVars.GITHUB_CALLBACK_URL || `http://localhost:${PORT}/auth/github/callback`;

// Initialize Database Connection
db.initDatabase({
  DB_HOST: process.env.DB_HOST || envVars.DB_HOST,
  DB_PORT: process.env.DB_PORT || envVars.DB_PORT,
  DB_USER: process.env.DB_USER || envVars.DB_USER,
  DB_PASSWORD: process.env.DB_PASSWORD || envVars.DB_PASSWORD,
  DB_NAME: process.env.DB_NAME || envVars.DB_NAME
});

// ===================================================================
// 2. JWT TOKEN UTILITIES (HMAC SHA-256)
// ===================================================================
function base64UrlEncode(str) {
  return Buffer.from(str)
    .toString("base64")
    .replace(/=/g, "")
    .replace(/\+/g, "-")
    .replace(/\//g, "_");
}

function base64UrlDecode(str) {
  str = str.replace(/-/g, "+").replace(/_/g, "/");
  while (str.length % 4) str += "=";
  return Buffer.from(str, "base64").toString();
}

function signJWT(payload, expiresInSeconds = 7 * 24 * 60 * 60) {
  const header = { alg: "HS256", typ: "JWT" };
  const exp = Math.floor(Date.now() / 1000) + expiresInSeconds;
  const fullPayload = { ...payload, exp };

  const encodedHeader = base64UrlEncode(JSON.stringify(header));
  const encodedPayload = base64UrlEncode(JSON.stringify(fullPayload));

  const signature = crypto
    .createHmac("sha256", JWT_SECRET)
    .update(`${encodedHeader}.${encodedPayload}`)
    .digest("base64")
    .replace(/=/g, "")
    .replace(/\+/g, "-")
    .replace(/\//g, "_");

  return `${encodedHeader}.${encodedPayload}.${signature}`;
}

function verifyJWT(token) {
  if (!token) return null;
  const parts = token.split(".");
  if (parts.length !== 3) return null;

  const [encodedHeader, encodedPayload, signature] = parts;
  const expectedSig = crypto
    .createHmac("sha256", JWT_SECRET)
    .update(`${encodedHeader}.${encodedPayload}`)
    .digest("base64")
    .replace(/=/g, "")
    .replace(/\+/g, "-")
    .replace(/\//g, "_");

  if (signature !== expectedSig) return null;

  try {
    const payload = JSON.parse(base64UrlDecode(encodedPayload));
    if (payload.exp && payload.exp < Math.floor(Date.now() / 1000)) {
      return null; // Token expired
    }
    return payload;
  } catch (e) {
    return null;
  }
}

function extractCookie(cookieHeader, name) {
  if (!cookieHeader) return null;
  const match = cookieHeader.match(new RegExp("(^|; )" + name + "=([^;]+)"));
  return match ? decodeURIComponent(match[2]) : null;
}

// ===================================================================
// 3. HTTP REQUEST HELPER (Native HTTPS Client)
// ===================================================================
function makeHttpsRequest(options, postData = null) {
  return new Promise((resolve, reject) => {
    const req = https.request(options, (res) => {
      let body = "";
      res.on("data", (chunk) => (body += chunk));
      res.on("end", () => {
        try {
          const parsed = JSON.parse(body);
          resolve({ status: res.statusCode, headers: res.headers, data: parsed });
        } catch (e) {
          resolve({ status: res.statusCode, headers: res.headers, data: body });
        }
      });
    });

    req.on("error", (err) => reject(err));

    if (postData) {
      req.write(typeof postData === "string" ? postData : JSON.stringify(postData));
    }
    req.end();
  });
}

// In-Memory active OAuth states map with expiration for extra CSRF defense
const activeOauthStates = new Map();

function generateAndStoreState() {
  const state = crypto.randomBytes(24).toString("hex");
  activeOauthStates.set(state, Date.now() + 10 * 60 * 1000); // 10 min TTL
  return state;
}

function validateAndConsumeState(state, cookieState) {
  if (!state) return false;
  
  // Verify cookie match if present
  if (cookieState && cookieState !== state) return false;

  const expiry = activeOauthStates.get(state);
  if (expiry && expiry > Date.now()) {
    activeOauthStates.delete(state);
    return true;
  }

  // If memory state was cycled during server restart but cookie is authentic
  if (cookieState && cookieState === state) {
    return true;
  }

  return false;
}

// Clean old states periodically
setInterval(() => {
  const now = Date.now();
  for (const [s, exp] of activeOauthStates.entries()) {
    if (exp < now) activeOauthStates.delete(s);
  }
}, 5 * 60 * 1000);

// ===================================================================
// 4. HTTP SERVER & ROUTER
// ===================================================================
const server = http.createServer(async (req, res) => {
  const reqUrl = new URL(req.url, `http://${req.headers.host || "localhost:5000"}`);
  const pathname = reqUrl.pathname;
  const query = Object.fromEntries(reqUrl.searchParams.entries());
  const method = req.method.toUpperCase();

  // CORS Headers
  const origin = req.headers.origin || CLIENT_URL;
  res.setHeader("Access-Control-Allow-Origin", origin);
  res.setHeader("Access-Control-Allow-Credentials", "true");
  res.setHeader("Access-Control-Allow-Methods", "GET, POST, OPTIONS, PUT, DELETE");
  res.setHeader("Access-Control-Allow-Headers", "Content-Type, Authorization");

  if (method === "OPTIONS") {
    res.writeHead(204);
    res.end();
    return;
  }

  // Parse Body for POST / PUT
  let body = {};
  if (method === "POST" || method === "PUT") {
    try {
      const rawBody = await new Promise((resolve) => {
        let buffer = "";
        req.on("data", (chunk) => (buffer += chunk));
        req.on("end", () => resolve(buffer));
      });
      if (rawBody) {
        body = JSON.parse(rawBody);
      }
    } catch (e) {
      body = {};
    }
  }

  // Extract Auth Token
  const authHeader = req.headers["authorization"];
  const token = (authHeader && authHeader.startsWith("Bearer ") && authHeader.split(" ")[1]) || extractCookie(req.headers.cookie, "sivacine_token");
  const verifiedPayload = verifyJWT(token);

  // -----------------------------------------------------------------
  // ROUTE: Health Check (GET /health)
  // -----------------------------------------------------------------
  if (pathname === "/health" && method === "GET") {
    res.writeHead(200, { "Content-Type": "application/json" });
    res.end(JSON.stringify({
      status: "ok",
      service: "SIVACINE AI / NPTEL OAuth Authentication Backend",
      timestamp: new Date().toISOString(),
      googleConfigured: Boolean(GOOGLE_CLIENT_ID && GOOGLE_CLIENT_SECRET),
      githubConfigured: Boolean(GITHUB_CLIENT_ID && GITHUB_CLIENT_SECRET)
    }));
    return;
  }

  // -----------------------------------------------------------------
  // ROUTE: Initiate Google OAuth (GET /auth/google)
  // Scopes: openid, email, profile
  // -----------------------------------------------------------------
  if (pathname === "/auth/google" && method === "GET") {
    if (!GOOGLE_CLIENT_ID || !GOOGLE_CLIENT_SECRET) {
      console.warn("⚠️ [Google OAuth] GOOGLE_CLIENT_ID or GOOGLE_CLIENT_SECRET missing in .env. Running in Demo Mode.");
      
      const demoUser = await db.createOrUpdateGoogleUser({
        googleId: `google_demo_${Date.now()}`,
        email: "sivakrishna@cinema.ai",
        name: "sivakrishna s",
        avatar: "https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=200&q=80",
        emailVerified: true
      });

      const demoToken = signJWT({
        id: demoUser.id,
        provider: "google",
        name: demoUser.name,
        email: demoUser.email,
        avatar: demoUser.avatar,
        plan: demoUser.plan,
        generationsRemaining: demoUser.generations_remaining
      });

      const secureFlag = NODE_ENV === "production" ? "; Secure" : "";
      res.writeHead(302, {
        "Set-Cookie": `sivacine_token=${demoToken}; Path=/; Max-Age=604800; SameSite=Lax${secureFlag}`,
        Location: `${CLIENT_URL}/?auth_success=true&provider=google&token=${demoToken}&name=${encodeURIComponent(demoUser.name)}&email=${encodeURIComponent(demoUser.email)}&avatar=${encodeURIComponent(demoUser.avatar)}`
      });
      res.end();
      return;
    }

    const state = generateAndStoreState();
    const secureFlag = NODE_ENV === "production" ? "; Secure" : "";
    const cookieHeader = `oauth_state=${state}; Path=/; HttpOnly; Max-Age=600; SameSite=Lax${secureFlag}`;

    // Request openid, email, profile scopes
    const scopes = encodeURIComponent("openid https://www.googleapis.com/auth/userinfo.profile https://www.googleapis.com/auth/userinfo.email");
    const googleAuthUrl = `https://accounts.google.com/o/oauth2/v2/auth?` +
      `client_id=${encodeURIComponent(GOOGLE_CLIENT_ID)}` +
      `&redirect_uri=${encodeURIComponent(GOOGLE_CALLBACK_URL)}` +
      `&response_type=code` +
      `&scope=${scopes}` +
      `&state=${encodeURIComponent(state)}` +
      `&access_type=offline` +
      `&prompt=select_account`;

    res.writeHead(302, {
      "Set-Cookie": cookieHeader,
      Location: googleAuthUrl
    });
    res.end();
    return;
  }

  // -----------------------------------------------------------------
  // ROUTE: Handle Google OAuth Callback (GET /auth/google/callback)
  // -----------------------------------------------------------------
  if (pathname === "/auth/google/callback" && method === "GET") {
    const code = query.code;
    const state = query.state;
    const errorParam = query.error;
    const cookieState = extractCookie(req.headers.cookie, "oauth_state");

    // Handle user cancellation or error from Google
    if (errorParam || !code) {
      const safeError = errorParam === "access_denied" ? "cancelled_by_user" : "google_auth_failed";
      res.writeHead(302, {
        "Set-Cookie": "oauth_state=; Path=/; Max-Age=0; SameSite=Lax",
        Location: `${CLIENT_URL}/?action=login&auth_error=${encodeURIComponent(safeError)}`
      });
      res.end();
      return;
    }

    // Verify CSRF State
    if (!validateAndConsumeState(state, cookieState)) {
      console.error("⚠️ [Google OAuth] CSRF State validation failed.");
      res.writeHead(302, {
        "Set-Cookie": "oauth_state=; Path=/; Max-Age=0; SameSite=Lax",
        Location: `${CLIENT_URL}/?action=login&auth_error=state_mismatch`
      });
      res.end();
      return;
    }

    try {
      // 1. Exchange Code for Access Token
      const postData = `code=${encodeURIComponent(code)}&client_id=${encodeURIComponent(GOOGLE_CLIENT_ID)}&client_secret=${encodeURIComponent(GOOGLE_CLIENT_SECRET)}&redirect_uri=${encodeURIComponent(GOOGLE_CALLBACK_URL)}&grant_type=authorization_code`;

      const tokenRes = await makeHttpsRequest(
        {
          hostname: "oauth2.googleapis.com",
          path: "/token",
          method: "POST",
          headers: {
            "Content-Type": "application/x-www-form-urlencoded",
            "Content-Length": Buffer.byteLength(postData)
          }
        },
        postData
      );

      const accessToken = tokenRes.data && tokenRes.data.access_token;
      if (!accessToken) {
        console.error("Google Token Exchange Failed:", tokenRes.data);
        res.writeHead(302, { Location: `${CLIENT_URL}/?action=login&auth_error=token_exchange_failed` });
        res.end();
        return;
      }

      // 2. Fetch User Profile
      const profileRes = await makeHttpsRequest({
        hostname: "www.googleapis.com",
        path: "/oauth2/v2/userinfo",
        method: "GET",
        headers: { Authorization: `Bearer ${accessToken}` }
      });

      const gUser = profileRes.data;
      if (!gUser || !gUser.id || !gUser.email) {
        throw new Error("Invalid profile payload from Google");
      }

      // 3. Security: Validate Email Verification
      const isEmailVerified = Boolean(gUser.verified_email || gUser.email_verified);
      if (!isEmailVerified) {
        console.warn(`⚠️ [Google OAuth] Rejected unverified email: ${gUser.email}`);
        res.writeHead(302, { Location: `${CLIENT_URL}/?action=login&auth_error=unverified_email` });
        res.end();
        return;
      }

      // 4. Find or Create User in MySQL / DB
      const appUser = await db.createOrUpdateGoogleUser({
        googleId: gUser.id,
        email: gUser.email,
        name: gUser.name || "Google Creator",
        avatar: gUser.picture || "https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=200&q=80",
        emailVerified: true
      });

      // 5. Sign JWT session token
      const jwtToken = signJWT({
        sub: String(appUser.id),
        id: String(appUser.id),
        provider: "google",
        name: appUser.name,
        email: appUser.email,
        avatar: appUser.avatar,
        plan: appUser.plan || "Free",
        generationsRemaining: appUser.generations_remaining !== undefined ? appUser.generations_remaining : 200
      });

      const secureFlag = NODE_ENV === "production" ? "; Secure" : "";
      res.writeHead(302, {
        "Set-Cookie": [
          `sivacine_token=${jwtToken}; Path=/; Max-Age=604800; SameSite=Lax${secureFlag}`,
          `oauth_state=; Path=/; Max-Age=0; SameSite=Lax`
        ],
        Location: `${CLIENT_URL}/?auth_success=true&provider=google&token=${jwtToken}&name=${encodeURIComponent(appUser.name)}&email=${encodeURIComponent(appUser.email)}&avatar=${encodeURIComponent(appUser.avatar || "")}`
      });
      res.end();
      return;
    } catch (err) {
      console.error("Google Auth Exception:", err.message);
      res.writeHead(302, { Location: `${CLIENT_URL}/?action=login&auth_error=authentication_failed` });
      res.end();
      return;
    }
  }

  // -----------------------------------------------------------------
  // ROUTE: Initiate GitHub OAuth (GET /auth/github)
  // -----------------------------------------------------------------
  if (pathname === "/auth/github" && method === "GET") {
    if (!GITHUB_CLIENT_ID || !GITHUB_CLIENT_SECRET) {
      const demoUser = await db.createOrUpdateGitHubUser({
        githubId: `gh_demo_${Date.now()}`,
        email: "sivakrishna@cinema.ai",
        name: "sivakrishna s",
        avatar: "https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=200&q=80"
      });

      const demoToken = signJWT({
        id: demoUser.id,
        provider: "github",
        name: demoUser.name,
        email: demoUser.email,
        avatar: demoUser.avatar,
        plan: demoUser.plan,
        generationsRemaining: demoUser.generations_remaining
      });

      const secureFlag = NODE_ENV === "production" ? "; Secure" : "";
      res.writeHead(302, {
        "Set-Cookie": `sivacine_token=${demoToken}; Path=/; Max-Age=604800; SameSite=Lax${secureFlag}`,
        Location: `${CLIENT_URL}/?auth_success=true&provider=github&token=${demoToken}&name=${encodeURIComponent(demoUser.name)}&email=${encodeURIComponent(demoUser.email)}&avatar=${encodeURIComponent(demoUser.avatar)}`
      });
      res.end();
      return;
    }

    const state = generateAndStoreState();
    const secureFlag = NODE_ENV === "production" ? "; Secure" : "";
    const cookieHeader = `oauth_state=${state}; Path=/; HttpOnly; Max-Age=600; SameSite=Lax${secureFlag}`;

    const githubAuthUrl = `https://github.com/login/oauth/authorize?` +
      `client_id=${encodeURIComponent(GITHUB_CLIENT_ID)}` +
      `&redirect_uri=${encodeURIComponent(GITHUB_CALLBACK_URL)}` +
      `&scope=${encodeURIComponent("read:user user:email")}` +
      `&state=${encodeURIComponent(state)}`;

    res.writeHead(302, {
      "Set-Cookie": cookieHeader,
      Location: githubAuthUrl
    });
    res.end();
    return;
  }

  // -----------------------------------------------------------------
  // ROUTE: Handle GitHub OAuth Callback (GET /auth/github/callback)
  // -----------------------------------------------------------------
  if (pathname === "/auth/github/callback" && method === "GET") {
    const code = query.code;
    const state = query.state;
    const errorParam = query.error;
    const cookieState = extractCookie(req.headers.cookie, "oauth_state");

    if (errorParam || !code) {
      res.writeHead(302, {
        "Set-Cookie": "oauth_state=; Path=/; Max-Age=0; SameSite=Lax",
        Location: `${CLIENT_URL}/?action=login&auth_error=github_cancelled`
      });
      res.end();
      return;
    }

    if (!validateAndConsumeState(state, cookieState)) {
      res.writeHead(302, {
        "Set-Cookie": "oauth_state=; Path=/; Max-Age=0; SameSite=Lax",
        Location: `${CLIENT_URL}/?action=login&auth_error=state_mismatch`
      });
      res.end();
      return;
    }

    try {
      const postData = JSON.stringify({
        client_id: GITHUB_CLIENT_ID,
        client_secret: GITHUB_CLIENT_SECRET,
        code,
        redirect_uri: GITHUB_CALLBACK_URL
      });

      const tokenRes = await makeHttpsRequest(
        {
          hostname: "github.com",
          path: "/login/oauth/access_token",
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "SivaCine-AI-Auth",
            "Content-Length": Buffer.byteLength(postData)
          }
        },
        postData
      );

      const accessToken = tokenRes.data && tokenRes.data.access_token;
      if (!accessToken) throw new Error("No access token from GitHub");

      const userRes = await makeHttpsRequest({
        hostname: "api.github.com",
        path: "/user",
        method: "GET",
        headers: {
          Authorization: `Bearer ${accessToken}`,
          "User-Agent": "SivaCine-AI-Auth"
        }
      });
      const ghUser = userRes.data;

      let userEmail = ghUser.email;
      if (!userEmail) {
        try {
          const emailsRes = await makeHttpsRequest({
            hostname: "api.github.com",
            path: "/user/emails",
            method: "GET",
            headers: {
              Authorization: `Bearer ${accessToken}`,
              "User-Agent": "SivaCine-AI-Auth"
            }
          });
          if (Array.isArray(emailsRes.data)) {
            const primary = emailsRes.data.find(e => e.primary && e.verified);
            if (primary) userEmail = primary.email;
          }
        } catch (e) {}
      }

      const appUser = await db.createOrUpdateGitHubUser({
        githubId: String(ghUser.id),
        email: userEmail || `${ghUser.login}@github.oauth`,
        name: ghUser.name || ghUser.login || "GitHub Creator",
        avatar: ghUser.avatar_url || "https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=200&q=80"
      });

      const jwtToken = signJWT({
        sub: String(appUser.id),
        id: String(appUser.id),
        provider: "github",
        name: appUser.name,
        email: appUser.email,
        avatar: appUser.avatar,
        plan: appUser.plan || "Free",
        generationsRemaining: appUser.generations_remaining !== undefined ? appUser.generations_remaining : 200
      });

      const secureFlag = NODE_ENV === "production" ? "; Secure" : "";
      res.writeHead(302, {
        "Set-Cookie": [
          `sivacine_token=${jwtToken}; Path=/; Max-Age=604800; SameSite=Lax${secureFlag}`,
          `oauth_state=; Path=/; Max-Age=0; SameSite=Lax`
        ],
        Location: `${CLIENT_URL}/?auth_success=true&provider=github&token=${jwtToken}&name=${encodeURIComponent(appUser.name)}&email=${encodeURIComponent(appUser.email)}&avatar=${encodeURIComponent(appUser.avatar || "")}`
      });
      res.end();
      return;
    } catch (err) {
      console.error("GitHub Auth Error:", err.message);
      res.writeHead(302, { Location: `${CLIENT_URL}/?action=login&auth_error=github_token_exchange_failed` });
      res.end();
      return;
    }
  }

  // -----------------------------------------------------------------
  // ROUTE: Get Current User Profile (GET /auth/me)
  // -----------------------------------------------------------------
  if (pathname === "/auth/me" && method === "GET") {
    if (!verifiedPayload) {
      res.writeHead(401, { "Content-Type": "application/json" });
      res.end(JSON.stringify({
        success: false,
        message: "Unauthorized - Please sign in to access your profile"
      }));
      return;
    }

    // Lookup latest user record from DB
    const userId = verifiedPayload.sub || verifiedPayload.id;
    const freshUser = (userId ? await db.findUserById(userId) : null) || await db.findUserByEmail(verifiedPayload.email);

    res.writeHead(200, { "Content-Type": "application/json" });
    res.end(JSON.stringify({
      success: true,
      user: {
        id: (freshUser && freshUser.id) || userId,
        provider: (freshUser && freshUser.provider) || verifiedPayload.provider || "oauth",
        name: (freshUser && freshUser.name) || verifiedPayload.name,
        email: (freshUser && freshUser.email) || verifiedPayload.email,
        avatar: (freshUser && freshUser.avatar) || verifiedPayload.avatar,
        plan: (freshUser && freshUser.plan) || verifiedPayload.plan || "Free",
        generationsRemaining: freshUser && freshUser.generations_remaining !== undefined ? freshUser.generations_remaining : (verifiedPayload.generationsRemaining || 200)
      }
    }));
    return;
  }

  // -----------------------------------------------------------------
  // ROUTE: User Logout (POST /auth/logout)
  // -----------------------------------------------------------------
  if (pathname === "/auth/logout" && method === "POST") {
    const secureFlag = NODE_ENV === "production" ? "; Secure" : "";
    res.writeHead(200, {
      "Set-Cookie": `sivacine_token=; Path=/; Max-Age=0; SameSite=Lax${secureFlag}`,
      "Content-Type": "application/json"
    });
    res.end(JSON.stringify({ success: true, message: "Logged out successfully" }));
    return;
  }

  // -----------------------------------------------------------------
  // ROUTE: Quick Demo Sign-In (POST /auth/demo-login)
  // -----------------------------------------------------------------
  if (pathname === "/auth/demo-login" && method === "POST") {
    const email = body.email || "sivakrishna@cinema.ai";
    const name = body.name || "sivakrishna s";

    const demoUser = await db.createOrUpdateGoogleUser({
      googleId: `google_demo_${Date.now()}`,
      email,
      name,
      avatar: "https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=200&q=80",
      emailVerified: true
    });

    const demoToken = signJWT({
      id: demoUser.id,
      provider: body.provider || "google",
      name: demoUser.name,
      email: demoUser.email,
      avatar: demoUser.avatar,
      plan: demoUser.plan,
      generationsRemaining: demoUser.generations_remaining
    });

    const secureFlag = NODE_ENV === "production" ? "; Secure" : "";
    res.writeHead(200, {
      "Set-Cookie": `sivacine_token=${demoToken}; Path=/; Max-Age=604800; SameSite=Lax${secureFlag}`,
      "Content-Type": "application/json"
    });
    res.end(JSON.stringify({ success: true, token: demoToken, user: demoUser }));
    return;
  }

  // -----------------------------------------------------------------
  // Static Frontend File Serving (Fallback for root studio files)
  // -----------------------------------------------------------------
  const staticRootDir = path.resolve(__dirname, "..");
  let relativeFilePath = pathname === "/" || pathname === "/login" ? "index.html" : pathname.replace(/^\//, "");
  let absoluteFilePath = path.join(staticRootDir, relativeFilePath);

  if (fs.existsSync(absoluteFilePath) && fs.statSync(absoluteFilePath).isFile()) {
    const ext = path.extname(absoluteFilePath).toLowerCase();
    const mimeTypes = {
      ".html": "text/html; charset=utf-8",
      ".css": "text/css; charset=utf-8",
      ".js": "application/javascript; charset=utf-8",
      ".json": "application/json; charset=utf-8",
      ".png": "image/png",
      ".jpg": "image/jpeg",
      ".jpeg": "image/jpeg",
      ".svg": "image/svg+xml",
      ".webp": "image/webp",
      ".ico": "image/x-icon",
      ".mp4": "video/mp4",
      ".webm": "video/webm",
      ".woff2": "font/woff2",
      ".woff": "font/woff"
    };

    const contentType = mimeTypes[ext] || "application/octet-stream";
    res.writeHead(200, { "Content-Type": contentType });
    fs.createReadStream(absoluteFilePath).pipe(res);
    return;
  }

  // -----------------------------------------------------------------
  // 404 Handler
  // -----------------------------------------------------------------
  res.writeHead(404, { "Content-Type": "application/json" });
  res.end(JSON.stringify({ error: "Endpoint not found", path: pathname }));
});

// Start Server
server.listen(PORT, () => {
  console.log(`=============================================================`);
  console.log(`🎬 SIVACINE AI / NPTEL Authentication Server Started`);
  console.log(`🌐 Server URL: http://localhost:${PORT}`);
  console.log(`🔑 Google OAuth URL: http://localhost:${PORT}/auth/google`);
  console.log(`🔑 Google Callback URL: ${GOOGLE_CALLBACK_URL}`);
  console.log(`💻 Client URL: ${CLIENT_URL}`);
  console.log(`🔒 Environment: ${NODE_ENV}`);
  if (!GOOGLE_CLIENT_ID || !GOOGLE_CLIENT_SECRET) {
    console.log(`ℹ️ Google OAuth Note: Add GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET to .env for live Google sign-ins.`);
  } else {
    console.log(`✅ Google OAuth 2.0 Credentials configured.`);
  }
  console.log(`=============================================================`);
});
