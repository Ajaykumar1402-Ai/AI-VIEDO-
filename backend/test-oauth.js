const http = require("http");

async function request(options, body = null) {
  return new Promise((resolve, reject) => {
    const req = http.request(options, (res) => {
      let data = "";
      res.on("data", chunk => data += chunk);
      res.on("end", () => {
        let json = null;
        try { json = JSON.parse(data); } catch (e) {}
        resolve({
          statusCode: res.statusCode,
          headers: res.headers,
          data,
          json
        });
      });
    });
    req.on("error", reject);
    if (body) {
      req.write(typeof body === "string" ? body : JSON.stringify(body));
    }
    req.end();
  });
}

async function runTests() {
  console.log("==================================================");
  console.log("🧪 RUNNING COMPREHENSIVE GOOGLE OAUTH & API TESTS");
  console.log("==================================================");

  // 1. Health Check
  const health = await request({ hostname: "localhost", port: 5000, path: "/health", method: "GET" });
  console.log(`[TEST 1] GET /health -> Status: ${health.statusCode}, Body:`, health.json);
  if (health.statusCode !== 200 || !health.json.status) throw new Error("Health check failed");

  // 2. GET /auth/me Unauthenticated
  const unauthMe = await request({ hostname: "localhost", port: 5000, path: "/auth/me", method: "GET" });
  console.log(`[TEST 2] GET /auth/me (Unauthenticated) -> Status: ${unauthMe.statusCode} (Expected 401), Msg:`, unauthMe.json.message);
  if (unauthMe.statusCode !== 401) throw new Error("Expected 401 for unauthenticated /auth/me");

  // 3. GET /auth/google Initiation
  const googleInit = await request({ hostname: "localhost", port: 5000, path: "/auth/google", method: "GET" });
  console.log(`[TEST 3] GET /auth/google -> Status: ${googleInit.statusCode} (Expected 302 Redirect)`);
  console.log(`         Redirect Location: ${googleInit.headers.location.substring(0, 80)}...`);
  if (googleInit.statusCode !== 302) throw new Error("Expected 302 for /auth/google");

  // 4. GET /auth/google/callback with Access Denied (User Cancelled)
  const userCancel = await request({ hostname: "localhost", port: 5000, path: "/auth/google/callback?error=access_denied", method: "GET" });
  console.log(`[TEST 4] GET /auth/google/callback (Cancelled) -> Status: ${userCancel.statusCode}, Location: ${userCancel.headers.location}`);
  if (!userCancel.headers.location.includes("cancelled_by_user")) throw new Error("Expected cancelled_by_user error in redirect");

  // 5. GET /auth/google/callback with State Mismatch
  const stateMismatch = await request({ hostname: "localhost", port: 5000, path: "/auth/google/callback?code=testcode&state=badstate", method: "GET" });
  console.log(`[TEST 5] GET /auth/google/callback (State Mismatch) -> Status: ${stateMismatch.statusCode}, Location: ${stateMismatch.headers.location}`);
  if (!stateMismatch.headers.location.includes("state_mismatch")) throw new Error("Expected state_mismatch error in redirect");

  // 6. Demo Sign-in and GET /auth/me with Bearer Token
  const demoLogin = await request({
    hostname: "localhost",
    port: 5000,
    path: "/auth/demo-login",
    method: "POST",
    headers: { "Content-Type": "application/json" }
  }, { email: "sivakrishna@cinema.ai", name: "sivakrishna s" });
  
  console.log(`[TEST 6] POST /auth/demo-login -> Status: ${demoLogin.statusCode}, Token Generated:`, Boolean(demoLogin.json.token));
  const token = demoLogin.json.token;

  const authMe = await request({
    hostname: "localhost",
    port: 5000,
    path: "/auth/me",
    method: "GET",
    headers: { Authorization: `Bearer ${token}` }
  });
  console.log(`[TEST 7] GET /auth/me (Authenticated) -> Status: ${authMe.statusCode}, Profile:`, authMe.json.user);
  if (authMe.statusCode !== 200 || !authMe.json.user.email) throw new Error("Failed to fetch authenticated profile");

  // 7. POST /auth/logout
  const logout = await request({ hostname: "localhost", port: 5000, path: "/auth/logout", method: "POST" });
  console.log(`[TEST 8] POST /auth/logout -> Status: ${logout.statusCode}, Success:`, logout.json.success);
  if (logout.statusCode !== 200 || !logout.json.success) throw new Error("Failed to logout");

  console.log("\n==================================================");
  console.log("🎉 ALL 8 AUTOMATED TESTS PASSED SUCCESSFULLY!");
  console.log("==================================================");
}

runTests().catch(err => {
  console.error("❌ Test failure:", err);
  process.exit(1);
});
