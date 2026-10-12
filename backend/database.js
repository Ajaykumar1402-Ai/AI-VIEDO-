/**
 * SIVACINE AI &bull; Database & User Management Layer
 * Native PostgreSQL 18 driver with resilient fallback for unified identity.
 */

const { Pool } = require("pg");
const crypto = require("crypto");

// In-Memory fallback store
const fallbackUsersDb = new Map();

let pool = null;
let isPgConnected = false;

function normalizeUser(row) {
  if (!row) return null;
  return {
    id: row.id,
    name: row.name,
    email: row.email,
    provider: row.auth_provider || row.provider || "local",
    provider_id: row.provider_subject || row.provider_id || null,
    avatar: row.avatar || "https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=200&q=80",
    plan: row.plan || "Free",
    generations_remaining: 200,
    is_active: row.is_active !== false,
    created_at: row.created_at
  };
}

async function initDatabase(config = {}) {
  const { DB_HOST, DB_USER, DB_PASSWORD, DB_NAME, DB_PORT } = config;

  const host = DB_HOST || "localhost";
  const port = parseInt(DB_PORT || "5432", 10);
  const user = DB_USER || "storytelling_app";
  const password = DB_PASSWORD || "storytelling_pass_2026";
  const database = DB_NAME || "storytelling_db";

  try {
    pool = new Pool({
      host,
      port,
      user,
      password,
      database,
      max: 10,
      idleTimeoutMillis: 30000,
      connectionTimeoutMillis: 5000
    });

    const client = await pool.connect();
    const res = await client.query("SELECT current_database(), current_user, version();");
    console.log(`✅ [PostgreSQL] Connected to ${res.rows[0].current_database} as ${res.rows[0].current_user}`);
    client.release();
    isPgConnected = true;
  } catch (err) {
    console.warn(`⚠️ [PostgreSQL] Connection warning (${err.message}). Using In-Memory Fallback.`);
    pool = null;
    isPgConnected = false;
  }
}

/**
 * Find user by ID (UUID)
 */
async function findUserById(userId) {
  if (isPgConnected && pool) {
    try {
      const res = await pool.query("SELECT * FROM users WHERE id = $1 LIMIT 1", [userId]);
      if (res.rows.length > 0) return normalizeUser(res.rows[0]);
    } catch (e) {
      console.error("PostgreSQL query error findUserById:", e.message);
    }
  }

  for (const user of fallbackUsersDb.values()) {
    if (user.id === userId) return user;
  }
  return null;
}

/**
 * Find user by Email (Case-insensitive)
 */
async function findUserByEmail(email) {
  if (!email) return null;
  const cleanEmail = email.trim().toLowerCase();

  if (isPgConnected && pool) {
    try {
      const res = await pool.query("SELECT * FROM users WHERE LOWER(email) = LOWER($1) LIMIT 1", [cleanEmail]);
      if (res.rows.length > 0) return normalizeUser(res.rows[0]);
    } catch (e) {
      console.error("PostgreSQL query error findUserByEmail:", e.message);
    }
  }

  for (const user of fallbackUsersDb.values()) {
    if (user.email && user.email.toLowerCase() === cleanEmail) return user;
  }
  return null;
}

/**
 * Find user by Provider and Subject
 */
async function findUserByProviderSubject(provider, subject) {
  if (!provider || !subject) return null;

  if (isPgConnected && pool) {
    try {
      const res = await pool.query(
        "SELECT * FROM users WHERE auth_provider = $1 AND provider_subject = $2 LIMIT 1",
        [provider, String(subject)]
      );
      if (res.rows.length > 0) return normalizeUser(res.rows[0]);
    } catch (e) {
      console.error("PostgreSQL query error findUserByProviderSubject:", e.message);
    }
  }

  return fallbackUsersDb.get(`${provider}:${subject}`) || null;
}

/**
 * Safely create or update user authenticated via Google OAuth 2.0
 */
async function createOrUpdateGoogleUser({ googleId, email, name, avatar, emailVerified }) {
  const cleanEmail = (email || "").trim().toLowerCase();
  const cleanName = (name || "Google Creator").trim();
  const cleanAvatar = avatar || "https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=200&q=80";

  // 1. Check if user already exists by Google Subject ID
  let user = await findUserByProviderSubject("google", googleId);

  // 2. Check if user exists by verified email (Safe Account Linking)
  if (!user && cleanEmail && emailVerified) {
    user = await findUserByEmail(cleanEmail);
  }

  const now = new Date();

  if (user) {
    // Update existing user
    if (isPgConnected && pool) {
      try {
        const updateRes = await pool.query(
          `UPDATE users
           SET name = COALESCE(NULLIF($1, ''), name),
               auth_provider = 'google',
               provider_subject = $2,
               updated_at = NOW()
           WHERE id = $3
           RETURNING *`,
          [cleanName, String(googleId), user.id]
        );
        if (updateRes.rows.length > 0) {
          user = normalizeUser(updateRes.rows[0]);
        }
      } catch (e) {
        console.error("PostgreSQL update error in Google auth:", e.message);
      }
    }

    user.name = cleanName || user.name;
    user.provider = "google";
    user.provider_id = String(googleId);
    user.avatar = cleanAvatar;
    fallbackUsersDb.set(`google:${googleId}`, user);
    return user;
  }

  // 3. Create new user in PostgreSQL
  const newId = crypto.randomUUID();
  const newUser = {
    id: newId,
    name: cleanName,
    email: cleanEmail,
    provider: "google",
    provider_id: String(googleId),
    avatar: cleanAvatar,
    plan: "Free",
    generations_remaining: 200,
    is_active: true,
    created_at: now.toISOString()
  };

  if (isPgConnected && pool) {
    try {
      const insertRes = await pool.query(
        `INSERT INTO users (id, name, email, auth_provider, provider_subject, is_active, created_at, updated_at)
         VALUES ($1, $2, $3, 'google', $4, true, NOW(), NOW())
         RETURNING *`,
        [newId, cleanName, cleanEmail, String(googleId)]
      );
      if (insertRes.rows.length > 0) {
        const created = normalizeUser(insertRes.rows[0]);
        fallbackUsersDb.set(`google:${googleId}`, created);
        return created;
      }
    } catch (e) {
      console.error("PostgreSQL insert error in Google auth:", e.message);
    }
  }

  fallbackUsersDb.set(`google:${googleId}`, newUser);
  return newUser;
}

/**
 * Safely create or update user authenticated via GitHub OAuth 2.0
 */
async function createOrUpdateGitHubUser({ githubId, email, name, avatar }) {
  const cleanEmail = (email || `github_${githubId}@users.noreply.github.com`).trim().toLowerCase();
  const cleanName = (name || "GitHub Creator").trim();
  const cleanAvatar = avatar || "https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=200&q=80";

  let user = await findUserByProviderSubject("github", githubId);
  if (!user && cleanEmail && !cleanEmail.includes("@users.noreply.github.com")) {
    user = await findUserByEmail(cleanEmail);
  }

  const now = new Date();

  if (user) {
    if (isPgConnected && pool) {
      try {
        const updateRes = await pool.query(
          `UPDATE users
           SET name = COALESCE(NULLIF($1, ''), name),
               auth_provider = 'github',
               provider_subject = $2,
               updated_at = NOW()
           WHERE id = $3
           RETURNING *`,
          [cleanName, String(githubId), user.id]
        );
        if (updateRes.rows.length > 0) {
          user = normalizeUser(updateRes.rows[0]);
        }
      } catch (e) {
        console.error("PostgreSQL update error in GitHub auth:", e.message);
      }
    }

    user.name = cleanName || user.name;
    user.provider = "github";
    user.provider_id = String(githubId);
    user.avatar = cleanAvatar;
    fallbackUsersDb.set(`github:${githubId}`, user);
    return user;
  }

  const newId = crypto.randomUUID();
  const newUser = {
    id: newId,
    name: cleanName,
    email: cleanEmail,
    provider: "github",
    provider_id: String(githubId),
    avatar: cleanAvatar,
    plan: "Free",
    generations_remaining: 200,
    is_active: true,
    created_at: now.toISOString()
  };

  if (isPgConnected && pool) {
    try {
      const insertRes = await pool.query(
        `INSERT INTO users (id, name, email, auth_provider, provider_subject, is_active, created_at, updated_at)
         VALUES ($1, $2, $3, 'github', $4, true, NOW(), NOW())
         RETURNING *`,
        [newId, cleanName, cleanEmail, String(githubId)]
      );
      if (insertRes.rows.length > 0) {
        const created = normalizeUser(insertRes.rows[0]);
        fallbackUsersDb.set(`github:${githubId}`, created);
        return created;
      }
    } catch (e) {
      console.error("PostgreSQL insert error in GitHub auth:", e.message);
    }
  }

  fallbackUsersDb.set(`github:${githubId}`, newUser);
  return newUser;
}

module.exports = {
  initDatabase,
  findUserById,
  findUserByEmail,
  findUserByProviderSubject,
  createOrUpdateGoogleUser,
  createOrUpdateGitHubUser
};
