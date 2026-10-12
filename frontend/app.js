/**
 * SIVACINE AI &bull; NEXT-GEN AI VIDEO PLATFORM ENGINE
 * Fully Interactive Studio: Real Video Cards, Spark Particle Physics Cursor,
 * Dynamic Generation Experience, Watermark & Payment Checkout Flow.
 */

// ===================================================================
// 1. DATA VAULT: EXPLORE COMMUNITY CINEMA VIDEOS
// ===================================================================
const EXPLORE_VIDEOS = [
  {
    id: "vid-1",
    title: "Cinematic City at Sunset",
    prompt: "A cinematic drone shot flying through a futuristic city at sunset, golden hour volumetric rays, 4K anamorphic lens, Kodak 2383 master grade",
    category: "cinematic",
    model: "Premium",
    ratio: "16:9",
    duration: "10s",
    aspectClass: "",
    videoUrl: "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4",
    poster: "https://images.unsplash.com/photo-1542751371-adc38448a05e?auto=format&fit=crop&w=800&q=80"
  },
  {
    id: "vid-2",
    title: "Alpine Hypercar Mountain Drift",
    prompt: "Matte-graphite electric hypercar drifting tightly around Swiss alpine mountain switchbacks, dense tire smoke, high shutter speed 60fps",
    category: "product",
    model: "Advanced",
    ratio: "16:9",
    duration: "10s",
    aspectClass: "",
    videoUrl: "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerEscapes.mp4",
    poster: "https://images.unsplash.com/photo-1503376780353-7e6692767b70?auto=format&fit=crop&w=800&q=80"
  },
  {
    id: "vid-3",
    title: "Quantum Monolith Server Arc",
    prompt: "Architectural slow dolly through glowing sapphire optical neural server racks pulsating with data, brutalist concrete, moody soft daylight",
    category: "story",
    model: "Standard",
    ratio: "16:9",
    duration: "5s",
    aspectClass: "",
    videoUrl: "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/WeAreGoingOnBullrun.mp4",
    poster: "https://images.unsplash.com/photo-1551288049-bebda4e38f71?auto=format&fit=crop&w=800&q=80"
  },
  {
    id: "vid-4",
    title: "Photoreal HeyGen AI Avatar Host",
    prompt: "Photorealistic AI digital avatar speaking confidently with natural eye contact, subtle facial muscle movements, studio spotlighting, 4K",
    category: "avatar",
    model: "Premium",
    ratio: "16:9",
    duration: "10s",
    aspectClass: "",
    videoUrl: "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerFun.mp4",
    poster: "https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=800&q=80"
  },
  {
    id: "vid-5",
    title: "Frosted Crystal Perfume Splash",
    prompt: "120fps ultra slow-motion of a frosted crystal perfume bottle crashing into turquoise ocean waves, sunlight caustics, luxury commercial",
    category: "product",
    model: "Premium",
    ratio: "16:9",
    duration: "10s",
    aspectClass: "",
    videoUrl: "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerJoyBlazes.mp4",
    poster: "https://images.unsplash.com/photo-1522335789203-aabd1fc54bc9?auto=format&fit=crop&w=800&q=80"
  },
  {
    id: "vid-6",
    title: "Orbital Biosphere Earth Horizon",
    prompt: "Vast rotating orbital biosphere structure passing over Earth terminator line into twilight, solar arrays reflecting specular sun flares, IMAX 70mm",
    category: "fantasy",
    model: "Advanced",
    ratio: "16:9",
    duration: "10s",
    aspectClass: "",
    videoUrl: "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerMeltdowns.mp4",
    poster: "https://images.unsplash.com/photo-1451187580459-43490279c0fa?auto=format&fit=crop&w=800&q=80"
  },
  {
    id: "vid-7",
    title: "Kyoto Anime Laser Dancer",
    prompt: "Makoto Shinkai style animated android dancer with glowing laser ribbon fans in neon-soaked rainy Kyoto, 60fps high fluidity, pastel sunset",
    category: "animation",
    model: "Standard",
    ratio: "16:9",
    duration: "5s",
    aspectClass: "",
    videoUrl: "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4",
    poster: "https://images.unsplash.com/photo-1578632767115-351597cf2477?auto=format&fit=crop&w=800&q=80"
  },
  {
    id: "vid-8",
    title: "Sahara Sand Dunes Solar Galleon",
    prompt: "Giant levitating solar sail galleon skimming across golden crimson sand waves, heat shimmer haze, cinematic 2.39:1 Panavision lens",
    category: "fantasy",
    model: "Premium",
    ratio: "16:9",
    duration: "10s",
    aspectClass: "",
    videoUrl: "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ElephantsDream.mp4",
    poster: "https://images.unsplash.com/photo-1509316975850-ff9c5deb0cd9?auto=format&fit=crop&w=800&q=80"
  },
  {
    id: "vid-9",
    title: "Viral TikTok 3-Second Hook",
    prompt: "Fast zoom-in dynamic transition of a creator snapping fingers as the studio environment morphs into a neon holographic command center",
    category: "social",
    model: "Standard",
    ratio: "16:9",
    duration: "5s",
    aspectClass: "",
    videoUrl: "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/TearsOfSteel.mp4",
    poster: "https://images.unsplash.com/photo-1509631179647-0177331693ae?auto=format&fit=crop&w=800&q=80"
  }
];

// ===================================================================
// 2. DATA VAULT: TEMPLATES
// ===================================================================
const TEMPLATES_DATA = [
  {
    id: "tpl-1",
    title: "Cinematic 3-Act Trailer",
    category: "Cinematic",
    desc: "Establishing drone wide shot, character push-in, and climactic action climax.",
    prompt: "A cinematic film trailer establishing a futuristic desert citadel, intense character close-up, and sudden airlock breach at 24fps",
    model: "premium",
    ratio: "16:9",
    style: "Cinematic 35mm",
    videoUrl: "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4",
    poster: "https://images.unsplash.com/photo-1536440136628-849c177e76a1?auto=format&fit=crop&w=600&q=80"
  },
  {
    id: "tpl-2",
    title: "Story Arc Multi-Scene",
    category: "Story",
    desc: "Multi-shot narrative progression with consistent lighting and character identity.",
    prompt: "Narrative detective sequence navigating through a rainy cyberpunk alley into a glowing underground club, tracking camera",
    model: "advanced",
    ratio: "16:9",
    style: "Cyberpunk Neon",
    videoUrl: "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerEscapes.mp4",
    poster: "https://images.unsplash.com/photo-1542751371-adc38448a05e?auto=format&fit=crop&w=600&q=80"
  },
  {
    id: "tpl-3",
    title: "3D Anime Anime Opening",
    category: "Animation",
    desc: "Vibrant cell-shaded anime style with volumetric sunbeams and fluid character moves.",
    prompt: "High-energy anime opening scene with flying mecha over sparkling blue ocean, vibrant watercolor clouds, 60fps",
    model: "standard",
    ratio: "16:9",
    style: "3D Animation",
    videoUrl: "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4",
    poster: "https://images.unsplash.com/photo-1578632767115-351597cf2477?auto=format&fit=crop&w=600&q=80"
  },
  {
    id: "tpl-4",
    title: "Luxury Commercial 120fps",
    category: "Product Ads",
    desc: "Macro liquid splashes, studio lighting, and high-speed specular reflections.",
    prompt: "Luxury matte black smartwatch splashing in crystal clear water droplets, studio softbox lighting, 120fps macro lens",
    model: "premium",
    ratio: "16:9",
    style: "Luxury Commercial",
    videoUrl: "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerJoyBlazes.mp4",
    poster: "https://images.unsplash.com/photo-1522335789203-aabd1fc54bc9?auto=format&fit=crop&w=600&q=80"
  },
  {
    id: "tpl-5",
    title: "Social Reel 3s Retention",
    category: "Social Media",
    desc: "Scroll-stopping vertical visual transition engineered for Instagram & TikTok.",
    prompt: "Fast zoom-in dynamic transition with neon particle explosion and high energy hook",
    model: "standard",
    ratio: "9:16",
    style: "Photorealistic",
    videoUrl: "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/TearsOfSteel.mp4",
    poster: "https://images.unsplash.com/photo-1509631179647-0177331693ae?auto=format&fit=crop&w=600&q=80"
  },
  {
    id: "tpl-6",
    title: "HeyGen Avatar Presenter",
    category: "Avatar",
    desc: "Studio presenter avatar with synchronized natural lip motion and expressions.",
    prompt: "Executive spokesperson in dark suit delivering product announcement in modern architectural office",
    model: "premium",
    ratio: "16:9",
    style: "HeyGen Avatar",
    videoUrl: "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerFun.mp4",
    poster: "https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=600&q=80"
  },
  {
    id: "tpl-7",
    title: "YouTube Intro Sequence",
    category: "YouTube",
    desc: "Bold dynamic motion graphics and cinematic intro title card reveal.",
    prompt: "3D metallic title card exploding out of glowing cyber matrix, electric sparks, 4K",
    model: "advanced",
    ratio: "16:9",
    style: "Cinematic 35mm",
    videoUrl: "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/WeAreGoingOnBullrun.mp4",
    poster: "https://images.unsplash.com/photo-1551288049-bebda4e38f71?auto=format&fit=crop&w=600&q=80"
  },
  {
    id: "tpl-8",
    title: "SaaS Marketing Explainer",
    category: "Marketing",
    desc: "Clean isometric visuals and smooth camera motion showcasing digital workflows.",
    prompt: "Futuristic holographic tablet user interface floating over minimalist wooden desk, soft natural light",
    model: "standard",
    ratio: "16:9",
    style: "Photorealistic",
    videoUrl: "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerMeltdowns.mp4",
    poster: "https://images.unsplash.com/photo-1508739773434-c26b3d09e071?auto=format&fit=crop&w=600&q=80"
  }
];

// ===================================================================
// 3. APPLICATION STATE
// ===================================================================
const appState = {
  freeGenerationsRemaining: 2,
  maxFreeGenerations: 2,
  isProUser: false,
  isEarlyBird: false,
  activePlanName: "Free Plan",
  
  // Generator Settings
  selectedModel: "standard",
  selectedRatio: "16:9",
  selectedDuration: "5",
  selectedResolution: "1080p",
  selectedStyle: "Cinematic 35mm",
  
  isGenerating: false,
  sparkThemeEnabled: true,
  currentVideoUrl: "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4",
  
  user: {
    name: "sivakrishna s",
    role: "Cinema Director & AI Creator",
    isLoggedIn: false
  }
};

// ===================================================================
// 4. DOM REFERENCES
// ===================================================================
const navFreeRemaining = document.getElementById("navFreeRemaining");
const freeGensLeftCount = document.getElementById("freeGensLeftCount");
const promptInput = document.getElementById("promptInput");
const promptCharCounter = document.getElementById("promptCharCounter");
const btnEnhancePrompt = document.getElementById("btnEnhancePrompt");
const btnGenerateVideo = document.getElementById("btnGenerateVideo");
const generateBtnLabel = document.getElementById("generateBtnLabel");
const genCostBadge = document.getElementById("genCostBadge");

// Generator Views
const outputIdleBox = document.getElementById("outputIdleBox");
const outputLoadingBox = document.getElementById("outputLoadingBox");
const outputPlayerBox = document.getElementById("outputPlayerBox");
const genProgressCircle = document.getElementById("genProgressCircle");
const genProgressNumber = document.getElementById("genProgressNumber");
const genStageMain = document.getElementById("genStageMain");
const genStageSub = document.getElementById("genStageSub");
const generatedVideoElement = document.getElementById("generatedVideoElement");
const videoWatermarkOverlay = document.getElementById("videoWatermarkOverlay");

// Chips on output
const outModelChip = document.getElementById("outModelChip");
const outRatioChip = document.getElementById("outRatioChip");
const outResChip = document.getElementById("outResChip");

// Grids
const exploreVideoGrid = document.getElementById("exploreVideoGrid");
const exploreCategoriesBar = document.getElementById("exploreCategoriesBar");
const templatesCardsGrid = document.getElementById("templatesCardsGrid");
const templateCatBar = document.getElementById("templateCatBar");

// Hero Video
const heroMainVideo = document.getElementById("heroMainVideo");
const heroMuteToggle = document.getElementById("heroMuteToggle");
const heroMuteIcon = document.getElementById("heroMuteIcon");
const heroMuteText = document.getElementById("heroMuteText");

// Modals
const videoViewerModal = document.getElementById("videoViewerModal");
const loginModal = document.getElementById("loginModal");
const paymentModal = document.getElementById("paymentModal");
const watermarkModal = document.getElementById("watermarkModal");
const freeLimitModal = document.getElementById("freeLimitModal");
const toastContainer = document.getElementById("toastContainer");

// Spark Canvas & Toggle
const sparkCanvas = document.getElementById("sparkCursorCanvas");
const sparkThemeToggleBtn = document.getElementById("sparkThemeToggleBtn");
const sparkStatusLabel = document.getElementById("sparkStatusLabel");

// ===================================================================
// 5. INITIALIZATION
// ===================================================================
document.addEventListener("DOMContentLoaded", () => {
  initSparkCursorPhysics();
  initCinematicAiLens();
  initExploreGrid(EXPLORE_VIDEOS);
  initTemplatesGrid(TEMPLATES_DATA);
  initIntersectionVideoAutoplay();
  initGeneratorEvents();
  initHeroVideoControls();
  updateCreditsBadges();
  checkAuthCallback();
});

// ===================================================================
// 6. UNIQUE SPARK CURSOR PARTICLE PHYSICS SYSTEM
// ===================================================================
let sparkCtx;
let sparkParticles = [];
let mousePos = { x: -100, y: -100 };
let lastMousePos = { x: -100, y: -100 };
let isMouseMoving = false;
let mouseStopTimer;

function initSparkCursorPhysics() {
  if (!sparkCanvas) return;
  sparkCtx = sparkCanvas.getContext("2d");

  function resizeCanvas() {
    sparkCanvas.width = window.innerWidth;
    sparkCanvas.height = window.innerHeight;
  }
  resizeCanvas();
  window.addEventListener("resize", resizeCanvas);

  window.addEventListener("mousemove", (e) => {
    if (!appState.sparkThemeEnabled) return;
    
    lastMousePos.x = mousePos.x;
    lastMousePos.y = mousePos.y;
    mousePos.x = e.clientX;
    mousePos.y = e.clientY;
    
    const speed = Math.hypot(mousePos.x - lastMousePos.x, mousePos.y - lastMousePos.y);
    const spawnCount = Math.min(Math.floor(speed / 4) + 2, 7);

    for (let i = 0; i < spawnCount; i++) {
      spawnSparkParticle(mousePos.x, mousePos.y, speed);
    }

    isMouseMoving = true;
    clearTimeout(mouseStopTimer);
    mouseStopTimer = setTimeout(() => { isMouseMoving = false; }, 80);
  });

  // Spark toggle button
  if (sparkThemeToggleBtn) {
    sparkThemeToggleBtn.addEventListener("click", () => {
      appState.sparkThemeEnabled = !appState.sparkThemeEnabled;
      sparkStatusLabel.textContent = appState.sparkThemeEnabled ? "ON" : "OFF";
      sparkStatusLabel.style.color = appState.sparkThemeEnabled ? "#A78BFA" : "#6B7280";
      showToast(appState.sparkThemeEnabled ? "✨ Spark Cursor theme activated" : "Cursor Spark disabled");
      if (!appState.sparkThemeEnabled && sparkCtx) {
        sparkCtx.clearRect(0, 0, sparkCanvas.width, sparkCanvas.height);
      }
    });
  }

  // Animation Loop
  function renderSparks() {
    if (appState.sparkThemeEnabled && sparkCtx) {
      sparkCtx.clearRect(0, 0, sparkCanvas.width, sparkCanvas.height);

      for (let i = sparkParticles.length - 1; i >= 0; i--) {
        const p = sparkParticles[i];
        p.x += p.vx;
        p.y += p.vy;
        p.vy += 0.04; // Gentle gravity
        p.life -= p.decay;
        p.size *= 0.96;

        if (p.life <= 0 || p.size <= 0.2) {
          sparkParticles.splice(i, 1);
          continue;
        }

        // Draw glowing particle
        sparkCtx.save();
        sparkCtx.beginPath();
        sparkCtx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
        sparkCtx.fillStyle = p.color;
        sparkCtx.globalAlpha = p.life;
        sparkCtx.shadowColor = p.glow;
        sparkCtx.shadowBlur = p.size * 5;
        sparkCtx.fill();
        sparkCtx.restore();
      }
    }
    requestAnimationFrame(renderSparks);
  }
  requestAnimationFrame(renderSparks);
}

function spawnSparkParticle(x, y, speed) {
  const colors = [
    { fill: "#C084FC", glow: "#8B5CF6" }, // Violet
    { fill: "#F472B6", glow: "#EC4899" }, // Pink
    { fill: "#FBBF24", glow: "#F59E0B" }, // Gold
    { fill: "#67E8F9", glow: "#06B6D4" }, // Cyan
    { fill: "#FFFFFF", glow: "#E0E7FF" }  // White star
  ];
  const chosen = colors[Math.floor(Math.random() * colors.length)];
  const angle = Math.random() * Math.PI * 2;
  const velocity = (Math.random() * 2 + 0.5) * (Math.min(speed, 25) / 10 + 0.5);

  sparkParticles.push({
    x: x + (Math.random() - 0.5) * 8,
    y: y + (Math.random() - 0.5) * 8,
    vx: Math.cos(angle) * velocity,
    vy: Math.sin(angle) * velocity,
    size: Math.random() * 3 + 1.5,
    life: 1.0,
    decay: Math.random() * 0.035 + 0.02,
    color: chosen.fill,
    glow: chosen.glow
  });

  if (sparkParticles.length > 150) {
    sparkParticles.shift();
  }
}

// ===================================================================
// 7. EXPLORE SECTION: REAL PLAYABLE VIDEO CARDS
// ===================================================================
function initExploreGrid(items) {
  if (!exploreVideoGrid) return;
  exploreVideoGrid.innerHTML = "";

  items.forEach((item) => {
    const card = document.createElement("div");
    card.className = "video-preview-card";
    card.id = item.id;
    card.dataset.category = item.category;

    card.innerHTML = `
      <div class="video-card-media ${item.aspectClass}" onclick="openViewerModal('${item.id}')">
        <video 
          class="card-html5-video" 
          muted 
          loop 
          playsinline 
          preload="metadata"
          poster="${item.poster}"
        >
          <source src="${item.videoUrl}" type="video/mp4">
        </video>

        <div class="card-media-top">
          <span class="card-model-badge">${item.model} Model</span>
          <span class="card-duration-badge">${item.duration}</span>
        </div>

        <div class="card-play-overlay">
          <div class="play-circle-btn">▶</div>
        </div>
      </div>

      <div class="video-card-body">
        <div>
          <div class="card-title-row">
            <h4 class="card-title">${item.title}</h4>
            <span class="card-category-tag">${item.category}</span>
          </div>
          <p class="card-prompt-snippet" title="${item.prompt}">"${item.prompt}"</p>
        </div>

        <div class="card-actions-row">
          <button class="btn-card-similar" onclick="event.stopPropagation(); loadPromptToCreate('${item.prompt.replace(/'/g, "\\'")}', '${item.model.toLowerCase()}')">
            <span>✨ Create Similar</span>
          </button>
          <button class="btn-card-inspect" onclick="event.stopPropagation(); openViewerModal('${item.id}')">
            <span>Inspect</span>
          </button>
        </div>
      </div>
    `;

    // Interactive Hover playback
    const videoEl = card.querySelector("video");
    card.addEventListener("mouseenter", () => {
      if (videoEl && videoEl.paused) {
        videoEl.play().catch(() => {});
      }
    });

    card.addEventListener("mouseleave", () => {
      // pause on mouseleave if not currently in intersection view
      if (videoEl && !videoEl.dataset.inView) {
        videoEl.pause();
      }
    });

    exploreVideoGrid.appendChild(card);
  });
}

// Category filter
if (exploreCategoriesBar) {
  exploreCategoriesBar.querySelectorAll(".cat-pill").forEach(btn => {
    btn.addEventListener("click", () => {
      exploreCategoriesBar.querySelectorAll(".cat-pill").forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      const filter = btn.dataset.cat;

      if (filter === "all") {
        initExploreGrid(EXPLORE_VIDEOS);
      } else {
        const filtered = EXPLORE_VIDEOS.filter(v => v.category === filter);
        initExploreGrid(filtered);
      }
      initIntersectionVideoAutoplay();
    });
  });
}

// ===================================================================
// 8. INTERSECTION OBSERVER FOR VIEWPORT AUTOPLAY
// ===================================================================
function initIntersectionVideoAutoplay() {
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      const video = entry.target.querySelector("video");
      if (!video) return;

      if (entry.isIntersecting) {
        video.dataset.inView = "true";
        video.play().catch(() => {});
      } else {
        delete video.dataset.inView;
        video.pause();
      }
    });
  }, { threshold: 0.45 });

  document.querySelectorAll(".video-preview-card, .template-box-card").forEach(card => {
    observer.observe(card);
  });
}

// ===================================================================
// 9. TEMPLATES SECTION
// ===================================================================
function initTemplatesGrid(templates) {
  if (!templatesCardsGrid) return;
  templatesCardsGrid.innerHTML = "";

  templates.forEach(tpl => {
    const card = document.createElement("div");
    card.className = "template-box-card";
    card.dataset.tcat = tpl.category;

    card.innerHTML = `
      <div class="template-media-wrap">
        <video class="template-video" muted loop playsinline preload="metadata" poster="${tpl.poster}">
          <source src="${tpl.videoUrl}" type="video/mp4">
        </video>
        <span class="template-tag">${tpl.category}</span>
      </div>

      <div class="template-body">
        <div>
          <h4 class="template-title">${tpl.title}</h4>
          <p class="template-desc">${tpl.desc}</p>
        </div>
        <button class="btn-use-template" onclick="useTemplate('${tpl.id}')">
          <span>Use Template &rarr;</span>
        </button>
      </div>
    `;

    const vid = card.querySelector("video");
    card.addEventListener("mouseenter", () => { if (vid) vid.play().catch(() => {}); });
    card.addEventListener("mouseleave", () => { if (vid) vid.pause(); });

    templatesCardsGrid.appendChild(card);
  });
}

// Template Category Filters
if (templateCatBar) {
  templateCatBar.querySelectorAll(".t-pill").forEach(btn => {
    btn.addEventListener("click", () => {
      templateCatBar.querySelectorAll(".t-pill").forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      const cat = btn.dataset.tcat;

      if (cat === "all") {
        initTemplatesGrid(TEMPLATES_DATA);
      } else {
        const filtered = TEMPLATES_DATA.filter(t => t.category.toLowerCase() === cat.toLowerCase());
        initTemplatesGrid(filtered);
      }
      initIntersectionVideoAutoplay();
    });
  });
}

function useTemplate(tplId) {
  const tpl = TEMPLATES_DATA.find(t => t.id === tplId);
  if (!tpl) return;

  promptInput.value = tpl.prompt;
  promptCharCounter.textContent = `${tpl.prompt.length}/500`;

  // Select Model
  selectModel(tpl.model || "standard");

  // Select Ratio
  document.querySelectorAll("#ratioGroup .pill-btn").forEach(b => {
    if (b.dataset.ratio === tpl.ratio) b.click();
  });

  // Select Style
  if (document.getElementById("styleSelect")) {
    document.getElementById("styleSelect").value = tpl.style;
  }

  showToast(`🎬 Template "${tpl.title}" loaded into Studio`);
  document.getElementById("create").scrollIntoView({ behavior: "smooth" });
}

// ===================================================================
// 10. CREATE SECTION & AI GENERATION SIMULATION
// ===================================================================
function initGeneratorEvents() {
  // Prompt character count
  if (promptInput) {
    promptInput.addEventListener("input", () => {
      promptCharCounter.textContent = `${promptInput.value.length}/500`;
    });
  }

  // Enhance Prompt Button
  if (btnEnhancePrompt) {
    btnEnhancePrompt.addEventListener("click", () => {
      const current = promptInput.value.trim();
      const enhancements = [
        "volumetric golden hour lighting, cinematic 35mm anamorphic lens, shallow depth of field, 4k 24fps Kodak 2383",
        "dramatic rim light, high-speed fluid camera movement, photorealistic octane render, 8K ultra detail",
        "atmospheric haze, reflections on wet pavement, subtle bokeh, master color grading, IMAX aspect ratio"
      ];
      const randomAdd = enhancements[Math.floor(Math.random() * enhancements.length)];

      if (!current) {
        promptInput.value = "Cinematic drone shot flying through a futuristic metropolis at twilight, " + randomAdd;
      } else {
        promptInput.value = current + ", " + randomAdd;
      }
      promptCharCounter.textContent = `${promptInput.value.length}/500`;
      showToast("✨ AI enhanced your scene prompt with cinematic optics");
    });
  }

  // Model Selection Radio Cards
  document.querySelectorAll("#modelSelector .model-radio-card").forEach(card => {
    card.addEventListener("click", () => {
      selectModel(card.dataset.model);
    });
  });

  // Ratio Buttons
  document.querySelectorAll("#ratioGroup .pill-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      document.querySelectorAll("#ratioGroup .pill-btn").forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      appState.selectedRatio = btn.dataset.ratio;
    });
  });

  // Duration Buttons
  document.querySelectorAll("#durationGroup .pill-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      document.querySelectorAll("#durationGroup .pill-btn").forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      appState.selectedDuration = btn.dataset.sec;
      genCostBadge.textContent = `${btn.dataset.sec}s Generation`;
    });
  });

  // Generate Button Click
  if (btnGenerateVideo) {
    btnGenerateVideo.addEventListener("click", handleGenerateClick);
  }
}

function selectModel(modelName) {
  appState.selectedModel = modelName;
  document.querySelectorAll("#modelSelector .model-radio-card").forEach(c => {
    if (c.dataset.model === modelName) {
      c.classList.add("active");
    } else {
      c.classList.remove("active");
    }
  });
}

function handleGenerateClick() {
  if (appState.isGenerating) return;

  const prompt = (promptInput.value || "").trim();
  if (!prompt) {
    showToast("⚠️ Please enter a prompt for your video scene");
    promptInput.focus();
    return;
  }

  // Check free generations limit
  if (!appState.isProUser && !appState.isEarlyBird && appState.freeGenerationsRemaining <= 0) {
    openFreeLimitModal();
    return;
  }

  // Consume free generation if on free tier
  if (!appState.isProUser && !appState.isEarlyBird) {
    appState.freeGenerationsRemaining--;
    updateCreditsBadges();
  }

  startGenerationSequence(prompt);
}

function startGenerationSequence(prompt) {
  appState.isGenerating = true;
  
  // Switch to loading box
  outputIdleBox.style.display = "none";
  outputPlayerBox.style.display = "none";
  outputLoadingBox.style.display = "block";

  const stages = [
    { p: 15, title: "Creating your video...", sub: "Analyzing prompt & framing scene composition", step: "step1" },
    { p: 45, title: "Generating scene...", sub: "Synthesizing latent 3D keyframe tensors", step: "step2" },
    { p: 75, title: "Rendering motion...", sub: "Calculating temporal optical flow vectors", step: "step3" },
    { p: 95, title: "Finalizing video...", sub: "Color grading in 4K DCI master cadence", step: "step4" }
  ];

  let progress = 0;
  let currentStageIdx = 0;

  document.querySelectorAll(".step-pill").forEach(p => p.classList.remove("active"));
  document.getElementById("step1").classList.add("active");

  const interval = setInterval(() => {
    progress += Math.floor(Math.random() * 8) + 6;
    if (progress > 100) progress = 100;

    genProgressNumber.textContent = `${progress}%`;
    const offset = 314 - (314 * progress) / 100;
    genProgressCircle.style.strokeDashoffset = offset;

    if (currentStageIdx < stages.length && progress >= stages[currentStageIdx].p) {
      const stg = stages[currentStageIdx];
      genStageMain.textContent = stg.title;
      genStageSub.textContent = stg.sub;
      
      document.querySelectorAll(".step-pill").forEach(p => p.classList.remove("active"));
      const stepEl = document.getElementById(stg.step);
      if (stepEl) stepEl.classList.add("active");
      currentStageIdx++;
    }

    if (progress >= 100) {
      clearInterval(interval);
      setTimeout(() => {
        finishGenerationSequence(prompt);
      }, 400);
    }
  }, 120);
}

function finishGenerationSequence(prompt) {
  appState.isGenerating = false;
  outputLoadingBox.style.display = "none";
  outputPlayerBox.style.display = "block";

  // Pick next video
  const videoPool = [
    "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4",
    "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerEscapes.mp4",
    "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/WeAreGoingOnBullrun.mp4",
    "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerJoyBlazes.mp4",
    "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerMeltdowns.mp4"
  ];
  const nextVideo = videoPool[Math.floor(Math.random() * videoPool.length)];
  appState.currentVideoUrl = nextVideo;

  generatedVideoElement.src = nextVideo;
  generatedVideoElement.load();
  generatedVideoElement.play().catch(() => {});

  // Update chips
  outModelChip.textContent = appState.selectedModel.toUpperCase();
  outRatioChip.textContent = appState.selectedRatio;
  outResChip.textContent = document.getElementById("resolutionSelect").value.toUpperCase();

  // Watermark status
  if (appState.isProUser || appState.isEarlyBird) {
    videoWatermarkOverlay.style.display = "none";
  } else {
    videoWatermarkOverlay.style.display = "flex";
  }

  showToast("🎬 Video generation complete &bull; Master render ready");
}

function updateCreditsBadges() {
  if (appState.isProUser || appState.isEarlyBird) {
    navFreeRemaining.parentElement.innerHTML = `<strong>PRO</strong> Unlimited`;
    freeGensLeftCount.parentElement.innerHTML = `<strong>PRO ACTIVE:</strong> Unlimited Generations`;
  } else {
    navFreeRemaining.textContent = appState.freeGenerationsRemaining;
    freeGensLeftCount.textContent = appState.freeGenerationsRemaining;
  }
}

// Quick generator action helpers
function regenerateVideo() {
  handleGenerateClick();
}

function createSimilarFromCurrent() {
  const current = promptInput.value;
  promptInput.value = current + " (Variation with dynamic camera orbit)";
  promptCharCounter.textContent = `${promptInput.value.length}/500`;
  handleGenerateClick();
}

function extendCurrentVideo() {
  showToast("⏩ Extending scene by +5 seconds temporal coherence...");
  handleGenerateClick();
}

function editCurrentVideoPrompt() {
  promptInput.focus();
  showToast("✂️ Edit your scene prompt on the left");
}

function loadPromptToCreate(promptText, modelName) {
  promptInput.value = promptText;
  promptCharCounter.textContent = `${promptText.length}/500`;
  if (modelName) selectModel(modelName);
  document.getElementById("create").scrollIntoView({ behavior: "smooth" });
  showToast("✨ Prompt loaded into Studio");
}

// ===================================================================
// 11. WATERMARK & DOWNLOAD EXPERIENCE
// ===================================================================
function handleDownloadAttempt() {
  if (appState.isProUser || appState.isEarlyBird) {
    proceedFreeWatermarkedDownload();
  } else {
    openWatermarkModal();
  }
}

function openWatermarkModal() {
  if (watermarkModal) watermarkModal.style.display = "flex";
}

function closeWatermarkModal() {
  if (watermarkModal) watermarkModal.style.display = "none";
}

function proceedFreeWatermarkedDownload() {
  closeWatermarkModal();
  showToast("⬇️ Starting MP4 Master Video Download...");
  
  // Simulate browser download
  const link = document.createElement("a");
  link.href = appState.currentVideoUrl;
  link.download = `SIVACINE_${Date.now()}.mp4`;
  link.target = "_blank";
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}

function openFreeLimitModal() {
  if (freeLimitModal) freeLimitModal.style.display = "flex";
}

function closeFreeLimitModal() {
  if (freeLimitModal) freeLimitModal.style.display = "none";
}

// ===================================================================
// 12. PAYMENT & CHECKOUT SYSTEM
// ===================================================================
function openPaymentModal(itemName, amount, description) {
  if (!paymentModal) return;
  
  document.getElementById("payItemName").textContent = itemName;
  document.getElementById("payItemDesc").textContent = description;
  document.getElementById("payAmountNumber").textContent = amount;
  document.getElementById("btnPayAmountText").textContent = amount;

  paymentModal.style.display = "flex";
}

function closePaymentModal() {
  if (paymentModal) paymentModal.style.display = "none";
}

function selectPayTab(tabName) {
  document.querySelectorAll(".pay-tab").forEach(t => t.classList.remove("active"));
  document.querySelectorAll(".pay-tab-content").forEach(c => c.style.display = "none");

  const activeTab = document.querySelector(`.pay-tab[data-tab="${tabName}"]`);
  if (activeTab) activeTab.classList.add("active");

  if (tabName === "card") document.getElementById("tabContentCard").style.display = "block";
  if (tabName === "upi") document.getElementById("tabContentUpi").style.display = "block";
  if (tabName === "apple") document.getElementById("tabContentApple").style.display = "block";
  if (tabName === "crypto") document.getElementById("tabContentCrypto").style.display = "block";
}

function simulatePaymentSuccess() {
  closePaymentModal();
  
  // Upgrade Account
  appState.isProUser = true;
  appState.isEarlyBird = true;
  appState.activePlanName = "Early Access Founder";
  
  // Hide watermarks
  if (videoWatermarkOverlay) videoWatermarkOverlay.style.display = "none";
  updateCreditsBadges();

  // Burst celebratory spark particles
  for (let i = 0; i < 60; i++) {
    spawnSparkParticle(window.innerWidth / 2, window.innerHeight / 2, 35);
  }

  showToast("🎉 Payment Successful! Account upgraded to Early Access 4K.");
}

const AUTH_BACKEND_URL = "http://localhost:5000";

// ===================================================================
// 13. LOGIN MODAL SYSTEM & BACKEND OAUTH INTEGRATION
// ===================================================================
function openLoginModal() {
  if (loginModal) loginModal.style.display = "flex";
}

function closeLoginModal() {
  if (loginModal) loginModal.style.display = "none";
}

function handleSocialLogin(provider) {
  closeLoginModal();
  showToast(`🔄 Connecting to ${provider} OAuth...`);

  if (provider.toLowerCase() === "google") {
    window.location.href = `${AUTH_BACKEND_URL}/auth/google`;
  } else if (provider.toLowerCase() === "github") {
    window.location.href = `${AUTH_BACKEND_URL}/auth/github`;
  } else {
    // Fallback simulation
    authenticateUserLocally({
      name: "sivakrishna s",
      email: "sivakrishna@cinema.ai",
      provider: provider
    });
  }
}

let isSignupMode = false;
let isSubmittingAuth = false;

function toggleAuthMode() {
  if (isSubmittingAuth) return;
  isSignupMode = !isSignupMode;
  const nameInput = document.getElementById("loginNameInput");
  const submitBtn = document.getElementById("btnLoginSubmit");
  const toggleBtn = document.getElementById("btnToggleAuthMode");
  const dividerLabel = document.getElementById("authDividerLabel");

  if (isSignupMode) {
    if (nameInput) nameInput.style.display = "block";
    if (submitBtn) submitBtn.innerHTML = "Create Account &rarr;";
    if (toggleBtn) toggleBtn.textContent = "Have an Account? Sign In";
    if (dividerLabel) dividerLabel.textContent = "or create account with email & password";
  } else {
    if (nameInput) nameInput.style.display = "none";
    if (submitBtn) submitBtn.innerHTML = "Sign In &rarr;";
    if (toggleBtn) toggleBtn.textContent = "Create Account";
    if (dividerLabel) dividerLabel.textContent = "or sign in with email & password";
  }
}

const FASTAPI_URL = "http://localhost:8000";

async function handleEmailLogin() {
  if (isSubmittingAuth) return;

  const emailEl = document.getElementById("loginEmailInput");
  const passwordEl = document.getElementById("loginPasswordInput");
  const nameEl = document.getElementById("loginNameInput");
  const submitBtn = document.getElementById("btnLoginSubmit");
  const toggleBtn = document.getElementById("btnToggleAuthMode");

  const email = (emailEl ? emailEl.value : "").trim();
  const password = (passwordEl ? passwordEl.value : "").trim();
  const name = (nameEl ? nameEl.value : "").trim();

  // Validation
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!email || !emailRegex.test(email)) {
    showToast("⚠️ Please enter a valid email address");
    if (emailEl) emailEl.focus();
    return;
  }
  if (!password || password.length < 8) {
    showToast("⚠️ Password must be at least 8 characters");
    if (passwordEl) passwordEl.focus();
    return;
  }
  if (isSignupMode && name.length < 2) {
    showToast("⚠️ Please enter your full name (at least 2 characters)");
    if (nameEl) nameEl.focus();
    return;
  }

  isSubmittingAuth = true;
  if (submitBtn) {
    submitBtn.disabled = true;
    submitBtn.style.opacity = "0.7";
    submitBtn.innerHTML = isSignupMode ? "⏳ Creating Account..." : "⏳ Signing In...";
  }
  if (toggleBtn) toggleBtn.disabled = true;

  try {
    if (isSignupMode) {
      // Call FastAPI POST /api/auth/signup
      const res = await fetch(`${FASTAPI_URL}/api/auth/signup`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          name: name || email.split("@")[0],
          email: email,
          password: password
        })
      });

      const data = await res.json().catch(() => ({}));
      if (!res.ok) {
        if (res.status === 409) {
          throw new Error("An account with this email address already exists. Please sign in.");
        }
        throw new Error(data.detail || `Signup failed (${res.status})`);
      }

      // Store tokens
      if (data.access_token) {
        localStorage.setItem("storytelling_token", data.access_token);
        localStorage.setItem("sivacine_auth_token", data.access_token);
      }
      if (data.user) {
        localStorage.setItem("sivacine_user", JSON.stringify(data.user));
        authenticateUserLocally(data.user);
      }

      closeLoginModal();
      if (passwordEl) passwordEl.value = "";
      
      // Burst celebratory particles
      for (let i = 0; i < 30; i++) {
        spawnSparkParticle(window.innerWidth / 2, 100, 20);
      }
      showToast(`🎉 Welcome to SIVACINE AI, ${data.user?.name || name}!`);

    } else {
      // Call FastAPI POST /api/auth/login
      const res = await fetch(`${FASTAPI_URL}/api/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          email: email,
          password: password
        })
      });

      const data = await res.json().catch(() => ({}));
      if (!res.ok) {
        if (res.status === 401) {
          throw new Error("Invalid email or password");
        }
        throw new Error(data.detail || "Sign in failed. Please try again.");
      }

      // Store tokens
      if (data.access_token) {
        localStorage.setItem("storytelling_token", data.access_token);
        localStorage.setItem("sivacine_auth_token", data.access_token);
      }
      if (data.user) {
        localStorage.setItem("sivacine_user", JSON.stringify(data.user));
        authenticateUserLocally(data.user);
      }

      closeLoginModal();
      if (passwordEl) passwordEl.value = "";
      showToast(`🎉 Welcome back, ${data.user?.name || "Creator"}!`);
    }
  } catch (err) {
    showToast(`⚠️ ${err.message}`);
  } finally {
    isSubmittingAuth = false;
    if (submitBtn) {
      submitBtn.disabled = false;
      submitBtn.style.opacity = "1";
      submitBtn.innerHTML = isSignupMode ? "Create Account &rarr;" : "Sign In &rarr;";
    }
    if (toggleBtn) toggleBtn.disabled = false;
  }
}

function authenticateUserLocally(userData) {
  appState.user.isLoggedIn = true;
  appState.user.name = userData.name || "sivakrishna s";
  appState.user.email = userData.email || "sivakrishna@cinema.ai";
  appState.user.avatar = userData.avatar || "https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=200&q=80";

  updateUserNavUI();
}

function updateUserNavUI() {
  const loginBtn = document.getElementById("btnNavLogin");
  const loginText = document.getElementById("navLoginText");
  
  if (appState.user.isLoggedIn && loginBtn && loginText) {
    loginText.textContent = appState.user.name;
    loginBtn.title = `Signed in as ${appState.user.email} (Click to Logout)`;
    loginBtn.onclick = handleUserLogout;
    loginBtn.classList.add("authenticated");
  } else if (loginBtn && loginText) {
    loginText.textContent = "Login";
    loginBtn.title = "Login";
    loginBtn.onclick = openLoginModal;
    loginBtn.classList.remove("authenticated");
  }
}

function handleUserLogout() {
  if (confirm("Do you want to log out of your SIVACINE account?")) {
    appState.user.isLoggedIn = false;
    localStorage.removeItem("storytelling_token");
    localStorage.removeItem("sivacine_auth_token");
    localStorage.removeItem("sivacine_user");
    updateUserNavUI();
    
    // Call FastAPI backend logout
    fetch(`${FASTAPI_URL}/api/auth/logout`, { method: "POST" }).catch(() => {});
    fetch(`${AUTH_BACKEND_URL}/auth/logout`, { method: "POST" }).catch(() => {});
    showToast("Logged out successfully");
  }
}

// Check for OAuth Callback Params & Session Restoration on Page Load
function checkAuthCallback() {
  const urlParams = new URLSearchParams(window.location.search);
  
  if (urlParams.get("auth_success") === "true") {
    const token = urlParams.get("token");
    const name = urlParams.get("name") || "sivakrishna s";
    const email = urlParams.get("email") || "sivakrishna@cinema.ai";
    const avatar = urlParams.get("avatar") || "";
    const provider = urlParams.get("provider") || "OAuth";

    if (token) {
      localStorage.setItem("storytelling_token", token);
      localStorage.setItem("sivacine_auth_token", token);
    }
    
    localStorage.setItem("sivacine_user", JSON.stringify({ name, email, avatar }));
    
    authenticateUserLocally({ name, email, avatar, provider });

    // Clean URL query parameters
    window.history.replaceState({}, document.title, window.location.pathname);

    // Burst celebratory particles
    for (let i = 0; i < 40; i++) {
      spawnSparkParticle(window.innerWidth / 2, 80, 25);
    }

    showToast(`🎉 Welcome, ${name}! Signed in with ${provider}`);
  } else if (urlParams.get("auth_error")) {
    const err = urlParams.get("auth_error");
    const errorMap = {
      cancelled_by_user: "Google sign-in was cancelled.",
      github_cancelled: "GitHub sign-in was cancelled.",
      unverified_email: "Your Google account email is not verified.",
      state_mismatch: "Security check failed (CSRF state mismatch). Please try again.",
      token_exchange_failed: "Authentication token exchange failed. Check backend credentials.",
      google_auth_failed: "Google authentication failed. Please try again."
    };
    const errorMsg = errorMap[err] || `Authentication failed (${err}).`;
    showToast(`⚠️ ${errorMsg}`);
    window.history.replaceState({}, document.title, window.location.pathname);
  } else {
    // Check saved token in localStorage and validate against /api/auth/me
    const savedToken = localStorage.getItem("storytelling_token") || localStorage.getItem("sivacine_auth_token");
    const savedUser = localStorage.getItem("sivacine_user");
    if (savedToken) {
      fetch(`${FASTAPI_URL}/api/auth/me`, {
        headers: { Authorization: `Bearer ${savedToken}` }
      })
      .then(res => res.ok ? res.json() : null)
      .then(userData => {
        if (userData && userData.email) {
          authenticateUserLocally(userData);
        } else if (savedUser) {
          try { authenticateUserLocally(JSON.parse(savedUser)); } catch (e) {}
        }
      })
      .catch(() => {
        if (savedUser) {
          try { authenticateUserLocally(JSON.parse(savedUser)); } catch (e) {}
        }
      });
    } else if (savedUser) {
      try {
        authenticateUserLocally(JSON.parse(savedUser));
      } catch (e) {}
    }

    // Auto-open login modal if URL contains login query or hash
    if (urlParams.get("action") === "login" || urlParams.get("login") === "true" || window.location.hash === "#login") {
      setTimeout(() => {
        openLoginModal();
      }, 300);
    }
  }

  // Bind Enter key on login inputs
  const inputs = ["loginNameInput", "loginEmailInput", "loginPasswordInput"];
  inputs.forEach(id => {
    const el = document.getElementById(id);
    if (el) {
      el.addEventListener("keyup", (e) => {
        if (e.key === "Enter") handleEmailLogin();
      });
    }
  });
}


// ===================================================================
// 14. VIDEO VIEWER / LIGHTBOX MODAL
// ===================================================================
function openViewerModal(videoId) {
  const item = EXPLORE_VIDEOS.find(v => v.id === videoId);
  if (!item || !videoViewerModal) return;

  document.getElementById("viewerSceneTitle").textContent = item.title;
  document.getElementById("viewerPromptText").textContent = item.prompt;
  document.getElementById("viewerModelBadge").textContent = `${item.model} Model • 4K Master`;
  document.getElementById("viewerCategoryTag").textContent = item.category.toUpperCase();
  document.getElementById("viewerRatioTag").textContent = item.ratio;

  const player = document.getElementById("viewerModalVideo");
  player.src = item.videoUrl;
  player.load();
  player.play().catch(() => {});

  document.getElementById("btnViewerCreateSimilar").onclick = () => {
    closeViewerModal();
    loadPromptToCreate(item.prompt, item.model.toLowerCase());
  };

  videoViewerModal.style.display = "flex";
}

function closeViewerModal() {
  if (videoViewerModal) {
    const player = document.getElementById("viewerModalVideo");
    if (player) player.pause();
    videoViewerModal.style.display = "none";
  }
}

// ===================================================================
// 15. HERO VIDEO CONTROLS
// ===================================================================
function initHeroVideoControls() {
  if (!heroMainVideo || !heroMuteToggle) return;

  heroMuteToggle.addEventListener("click", () => {
    heroMainVideo.muted = !heroMainVideo.muted;
    if (heroMainVideo.muted) {
      heroMuteIcon.textContent = "🔇";
      heroMuteText.textContent = "Muted";
    } else {
      heroMuteIcon.textContent = "🔊";
      heroMuteText.textContent = "Sound ON";
    }
  });
}

// ===================================================================
// 16. TOAST NOTIFICATIONS
// ===================================================================
function showToast(message) {
  if (!toastContainer) return;

  const toast = document.createElement("div");
  toast.className = "toast-item";
  toast.innerHTML = `<span>${message}</span>`;
  toastContainer.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = "0";
    toast.style.transform = "translateY(8px)";
    setTimeout(() => { toast.remove(); }, 300);
  }, 3600);
}

// ===================================================================
// 17. CINEMATIC AI LENS INTERACTION ENGINE
// ===================================================================
const CINEMATIC_LENS_PRESETS = [
  {
    style: "CINEMATIC",
    camera: "DOLLY IN",
    lighting: "GOLDEN HOUR",
    mood: "EPIC NARRATIVE",
    quality: "4K MASTER",
    tags: "Cinematic &bull; 35mm &bull; Golden Hour",
    prompt: "A cinematic 35mm anamorphic drone shot flying through a golden hour metropolis, volumetric light rays, 4K Kodak 2383"
  },
  {
    style: "CYBERPUNK",
    camera: "FPV DRONE",
    lighting: "NEON GLOW",
    mood: "FUTURISTIC",
    quality: "4K DCI",
    tags: "Cyberpunk &bull; Neon &bull; Futuristic",
    prompt: "Cyberpunk neon futuristic metropolis with rain reflections and volumetric haze, 4K anamorphic lens"
  },
  {
    style: "ANIME",
    camera: "360° ORBIT",
    lighting: "PASTEL SUNSET",
    mood: "ETHEREAL",
    quality: "60 FPS",
    tags: "Anime &bull; Shinkai &bull; Ethereal",
    prompt: "Makoto Shinkai style anime vibrant glowing sunset with volumetric lightbeams, fluid motion, 60fps"
  },
  {
    style: "SCI-FI",
    camera: "TRACKING SHOT",
    lighting: "VOLUMETRIC",
    mood: "DYSTOPIAN",
    quality: "8K RES",
    tags: "Sci-Fi &bull; Monolith &bull; Volumetric",
    prompt: "Vast rotating orbital biosphere structure passing over Earth terminator line into twilight, IMAX 70mm"
  },
  {
    style: "FILM NOIR",
    camera: "CRANE UP",
    lighting: "CHIAROSCURO",
    mood: "MYSTERIOUS",
    quality: "24 FPS",
    tags: "Film Noir &bull; Chiaroscuro &bull; Moody",
    prompt: "Rembrandt high contrast chiaroscuro film noir street shot with wet asphalt reflections and silhouette lighting"
  }
];

let activeLensPreset = CINEMATIC_LENS_PRESETS[1]; // default Cyberpunk

function initCinematicAiLens() {
  const heroCard = document.getElementById("heroCinemaCard");
  const lens = document.getElementById("cinematicAiLens");
  if (!heroCard || !lens) return;

  const styleEl = document.getElementById("lensHudStyle");
  const cameraEl = document.getElementById("lensHudCamera");
  const lightingEl = document.getElementById("lensHudLighting");
  const moodEl = document.getElementById("lensHudMood");
  const qualityEl = document.getElementById("lensHudQuality");
  const detectedCard = document.getElementById("aiSceneDetectedCard");
  const detectedTags = document.getElementById("detectedSceneTags");

  let isHovering = false;
  let targetX = 0;
  let targetY = 0;
  let currentX = 0;
  let currentY = 0;
  let idleHoverTimer = null;
  let animFrameId = null;

  function updateLensPosition() {
    if (isHovering) {
      // Smooth lerp easing for 60fps tracking
      currentX += (targetX - currentX) * 0.16;
      currentY += (targetY - currentY) * 0.16;

      lens.style.left = `${currentX}px`;
      lens.style.top = `${currentY}px`;

      animFrameId = requestAnimationFrame(updateLensPosition);
    }
  }

  heroCard.addEventListener("mouseenter", (e) => {
    // Disable on mobile/touch screens
    if (window.innerWidth <= 768) return;

    isHovering = true;
    const rect = heroCard.getBoundingClientRect();
    targetX = e.clientX - rect.left;
    targetY = e.clientY - rect.top;
    currentX = targetX;
    currentY = targetY;

    lens.style.left = `${currentX}px`;
    lens.style.top = `${currentY}px`;
    lens.classList.add("lens-active");

    cancelAnimationFrame(animFrameId);
    animFrameId = requestAnimationFrame(updateLensPosition);
  });

  heroCard.addEventListener("mousemove", (e) => {
    if (!isHovering) return;
    const rect = heroCard.getBoundingClientRect();
    targetX = e.clientX - rect.left;
    targetY = e.clientY - rect.top;

    // Reset 1-second idle detection timer
    if (detectedCard) detectedCard.classList.remove("detected-active");
    clearTimeout(idleHoverTimer);

    // Calculate normalized relative position
    const normX = Math.max(0, Math.min(1, targetX / rect.width));
    const normY = Math.max(0, Math.min(1, targetY / rect.height));

    // Determine preset index based on position quadrants
    const presetIdx = Math.floor((normX * 3 + normY * 2)) % CINEMATIC_LENS_PRESETS.length;
    activeLensPreset = CINEMATIC_LENS_PRESETS[presetIdx];

    // Dynamically update HUD metadata
    if (styleEl) styleEl.textContent = activeLensPreset.style;
    if (cameraEl) cameraEl.textContent = activeLensPreset.camera;
    if (lightingEl) lightingEl.textContent = activeLensPreset.lighting;
    if (moodEl) moodEl.textContent = activeLensPreset.mood;
    if (qualityEl) qualityEl.textContent = activeLensPreset.quality;

    // Set 1-second idle hover timer for detection popup
    idleHoverTimer = setTimeout(() => {
      if (isHovering && detectedCard && detectedTags) {
        detectedTags.innerHTML = activeLensPreset.tags;
        detectedCard.classList.add("detected-active");
      }
    }, 1000);
  });

  heroCard.addEventListener("mouseleave", () => {
    isHovering = false;
    clearTimeout(idleHoverTimer);
    lens.classList.remove("lens-active");
    if (detectedCard) detectedCard.classList.remove("detected-active");
    cancelAnimationFrame(animFrameId);
  });
}

function handleGenerateDetectedStyle(e) {
  if (e) e.stopPropagation();
  
  if (activeLensPreset && activeLensPreset.prompt) {
    loadPromptToCreate(activeLensPreset.prompt, "premium");
    showToast(`✨ Loaded "${activeLensPreset.style}" detected style into AI Studio!`);
  }
}

// Close modals on outside click
window.addEventListener("click", (e) => {
  if (e.target === videoViewerModal) closeViewerModal();
  if (e.target === loginModal) closeLoginModal();
  if (e.target === paymentModal) closePaymentModal();
  if (e.target === watermarkModal) closeWatermarkModal();
  if (e.target === freeLimitModal) closeFreeLimitModal();
});

// ESC key to close modals
window.addEventListener("keydown", (e) => {
  if (e.key === "Escape") {
    closeViewerModal();
    closeLoginModal();
    closePaymentModal();
    closeWatermarkModal();
    closeFreeLimitModal();
  }
});


