"""
SIVACINE AI — Universal Script Generator Service.

Uses the google-genai SDK to call Gemini and produce a structured JSON script
covering video, audio, dialogue, narration, camera, timing, and sound effects
for any video concept (cartoon, film, anime, documentary, ad, etc.).

This service is stateless — it does NOT touch the database, job queue, or
filesystem. It returns pure Pydantic models.
"""

import json
import re
import logging
import asyncio
from typing import Dict, Any, List

import httpx

from google import genai
from google.genai.types import GenerateContentConfig

from ..config import settings
from ..schemas.script_generator import (
    ScriptGenerateRequest,
    ScriptGenerateResponse,
    ScriptScene,
    DialogueLine,
    NarratorScript,
    SoundEffect,
    CameraInstruction,
    SceneTiming,
    AudioTiming,
)
from .supabase_storage_service import SupabaseStorageService

logger = logging.getLogger(__name__)


class ScriptGeneratorService:
    """Stateless service: prompt → Gemini → validated ScriptGenerateResponse."""

    # ------------------------------------------------------------------
    # Prompt construction
    # ------------------------------------------------------------------
    @classmethod
    def _build_system_prompt(cls, req: ScriptGenerateRequest) -> str:
        """Build the Gemini system instruction."""
        # Estimate scene count
        avg_dur = 8
        target_scenes = max(3, min(20, round(req.target_duration_seconds / avg_dur)))

        narration_rule = (
            "Include a narrator voiceover script for every scene. Provide voice_style and pacing."
            if req.include_narration
            else "Do NOT include narration. Set 'narrator' to null for every scene."
        )
        dialogue_rule = (
            "Include natural character dialogue where appropriate. Provide voice_style and emotion for each line."
            if req.include_dialogue
            else "Do NOT include dialogue. Set 'dialogue' to an empty list [] for every scene."
        )
        sfx_rule = (
            "Include sound effects and ambient audio cues for every scene."
            if req.include_sound_effects
            else "Do NOT include sound effects. Set 'sound_effects' to an empty list [] for every scene."
        )

        return f"""\
You are SIVACINE AI, a world-class cinematic script generator.

Given a user concept, produce a COMPLETE, STRUCTURED JSON script for a {req.video_style} style video.

RULES:
1. This is a UNIVERSAL generator — support cartoons, realistic films, anime, documentaries, advertisements, educational videos, sci-fi, horror, fantasy, or any concept the user describes.
2. Create exactly {target_scenes} scenes (adjust ±2 if the narrative demands it).
3. The SUM of all scene durations MUST equal {req.target_duration_seconds} seconds. Each scene duration must be between 3 and 60 seconds.
4. {narration_rule}
5. {dialogue_rule}
6. {sfx_rule}
7. For each scene provide:
   - scene_number (1-indexed)
   - scene_title (short slug)
   - visual_prompt (highly detailed prompt for AI video generation: subjects, environment, lighting, color palette, atmosphere, framing)
   - motion_instructions (subject motion, action choreography within the frame)
   - camera (shot_type, movement, angle, transition)
   - dialogue (list of lines with character, text, voice_style, emotion, language)
   - narrator (text, voice_style, pacing) or null
   - sound_effects (list with description, timing, intensity) or empty []
   - background_music (descriptive string)
   - visual_style (style for this scene, inheriting the global style by default)
   - scene_timing (start_time as "HH:MM:SS", end_time, duration_seconds)
   - audio_timing (narration_start, narration_end, dialogue_windows) or null
8. At the top level also include:
   - title
   - synopsis (2-3 sentences)
   - video_style ("{req.video_style}")
   - language ("{req.language}")
   - total_duration_seconds ({req.target_duration_seconds})
   - scene_count (number of scenes)
   - speakers (list of unique characters with name, role, voice_style, description)
   - global_audio_notes (project-wide audio direction)

OUTPUT: Return ONLY raw valid JSON. No markdown fences, no commentary, no preamble. Just the JSON object.\
"""

    @classmethod
    def _build_user_prompt(cls, req: ScriptGenerateRequest) -> str:
        return req.prompt

    # ------------------------------------------------------------------
    # Gemini SDK call (with retry + model fallback)
    # ------------------------------------------------------------------

    # ------------------------------------------------------------------
    # Gemini API call (Direct REST with httpx + SDK fallback + model fallback)
    # ------------------------------------------------------------------

    _MODEL_FALLBACKS: List[str] = [
        "gemini-3.5-flash",
        "gemini-flash-latest",
        "gemini-3.8-flash",
    ]

    @classmethod
    async def _call_gemini(cls, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        """Call Gemini via direct REST (httpx) with SDK fallback and model fallback."""
        if not settings.GEMINI_API_KEY:
            logger.warning("GEMINI_API_KEY not set — returning deterministic fallback script.")
            return cls._fallback_response()

        # Build prioritized list of models
        models_to_try: List[str] = [settings.GEMINI_MODEL] + [
            m for m in cls._MODEL_FALLBACKS if m != settings.GEMINI_MODEL
        ]

        # 1. Try Direct REST via httpx (fastest and most reliable)
        for model in models_to_try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={settings.GEMINI_API_KEY}"
            payload = {
                "systemInstruction": {
                    "parts": [{"text": system_prompt}]
                },
                "contents": [
                    {"parts": [{"text": user_prompt}]}
                ],
                "generationConfig": {
                    "temperature": 0.75,
                    "topP": 0.95,
                    "maxOutputTokens": 8192,
                },
            }
            try:
                logger.info(f"Calling Gemini REST: model={model}")
                async with httpx.AsyncClient(timeout=120.0) as http_client:
                    response = await http_client.post(url, json=payload)

                if response.status_code == 200:
                    data = response.json()
                    candidates = data.get("candidates", [])
                    if candidates:
                        parts = candidates[0].get("content", {}).get("parts", [])
                        if parts:
                            raw_text = parts[0].get("text", "")
                            if raw_text:
                                logger.info(f"Gemini REST success with model={model}")
                                return cls._parse_json(raw_text)
                    logger.warning(f"Gemini REST model={model} returned empty candidates. Trying fallback.")
                elif response.status_code in (404, 400):
                    logger.warning(f"Gemini REST model={model} returned HTTP {response.status_code}. Trying next model.")
                    continue
                else:
                    logger.warning(f"Gemini REST model={model} HTTP {response.status_code}: {response.text[:200]}")
            except Exception as exc:
                logger.warning(f"Gemini REST error for model={model}: {exc}")

        # 2. Try SDK fallback if REST was inconclusive
        try:
            client = genai.Client(api_key=settings.GEMINI_API_KEY)
            config = GenerateContentConfig(
                temperature=0.75,
                top_p=0.95,
                max_output_tokens=8192,
                system_instruction=system_prompt,
            )
            for model in models_to_try:
                try:
                    logger.info(f"Attempting Gemini SDK fallback with model={model}")
                    sdk_resp = await client.aio.models.generate_content(
                        model=model,
                        contents=user_prompt,
                        config=config,
                    )
                    if sdk_resp and sdk_resp.text:
                        logger.info(f"Gemini SDK fallback success with model={model}")
                        return cls._parse_json(sdk_resp.text)
                except Exception as sdk_err:
                    logger.warning(f"Gemini SDK fallback error for model={model}: {sdk_err}")
        except Exception as client_err:
            logger.warning(f"Could not initialize Gemini SDK client: {client_err}")

        # 3. Graceful fallback to deterministic generator if API is completely unavailable
        logger.warning("All live Gemini models exhausted. Returning structured deterministic script.")
        return cls._fallback_response()

    # ------------------------------------------------------------------
    # JSON parsing with recovery
    # ------------------------------------------------------------------
    @classmethod
    def _parse_json(cls, raw: str) -> Dict[str, Any]:
        clean = raw.strip()
        # Strip markdown fences
        if clean.startswith("```json"):
            clean = clean[7:]
        elif clean.startswith("```"):
            clean = clean[3:]
        if clean.endswith("```"):
            clean = clean[:-3]
        clean = clean.strip()

        try:
            return json.loads(clean)
        except json.JSONDecodeError:
            # Bounded regex recovery
            match = re.search(r"\{.*\}", clean, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group(0))
                except json.JSONDecodeError:
                    pass
            logger.error(f"JSON parse failure. Raw (first 500 chars): {clean[:500]}")
            raise RuntimeError("Failed to parse Gemini output as valid JSON.")

    # ------------------------------------------------------------------
    # Public entry point
    # ------------------------------------------------------------------
    @classmethod
    async def generate(cls, req: ScriptGenerateRequest) -> ScriptGenerateResponse:
        """
        Main public method.
        Takes a ScriptGenerateRequest, calls Gemini, validates the output
        through Pydantic, and returns a ScriptGenerateResponse.
        """
        system_prompt = cls._build_system_prompt(req)
        user_prompt = cls._build_user_prompt(req)

        raw_data = await cls._call_gemini(system_prompt, user_prompt)

        # --- Normalise and validate through Pydantic ---
        scenes_raw = raw_data.get("scenes", [])
        validated_scenes = []
        cumulative = 0

        for idx, s in enumerate(scenes_raw, start=1):
            # Build nested objects safely
            camera_data = s.get("camera")
            camera = CameraInstruction(**camera_data) if isinstance(camera_data, dict) else None

            narrator_data = s.get("narrator")
            narrator = NarratorScript(**narrator_data) if isinstance(narrator_data, dict) else None

            dialogue_raw = s.get("dialogue", [])
            dialogue = [
                DialogueLine(**d) for d in dialogue_raw
                if isinstance(d, dict) and d.get("character") and d.get("text")
            ]

            sfx_raw = s.get("sound_effects", [])
            sfx = [
                SoundEffect(**e) for e in sfx_raw
                if isinstance(e, dict) and e.get("description")
            ]

            timing_data = s.get("scene_timing", {})
            if not isinstance(timing_data, dict):
                timing_data = {}
            duration = int(timing_data.get("duration_seconds", s.get("duration_seconds", 8)))
            start_offset = f"{cumulative // 3600:02d}:{(cumulative % 3600) // 60:02d}:{cumulative % 60:02d}"
            cumulative += duration
            end_offset = f"{cumulative // 3600:02d}:{(cumulative % 3600) // 60:02d}:{cumulative % 60:02d}"

            scene_timing = SceneTiming(
                start_time=timing_data.get("start_time", start_offset),
                end_time=timing_data.get("end_time", end_offset),
                duration_seconds=duration,
            )

            audio_timing_data = s.get("audio_timing")
            audio_timing = None
            if isinstance(audio_timing_data, dict):
                dw = audio_timing_data.get("dialogue_windows")
                if isinstance(dw, list):
                    normalized_dw = []
                    for w in dw:
                        if isinstance(w, dict):
                            start = w.get("start", "")
                            end = w.get("end", "")
                            normalized_dw.append(f"{start}–{end}" if start or end else str(w))
                        else:
                            normalized_dw.append(str(w))
                    audio_timing_data["dialogue_windows"] = normalized_dw
                try:
                    audio_timing = AudioTiming(**audio_timing_data)
                except Exception:
                    audio_timing = None

            validated_scenes.append(ScriptScene(
                scene_number=idx,
                scene_title=s.get("scene_title"),
                visual_prompt=s.get("visual_prompt", "Cinematic visual shot."),
                motion_instructions=s.get("motion_instructions"),
                camera=camera,
                dialogue=dialogue,
                narrator=narrator,
                sound_effects=sfx,
                background_music=s.get("background_music"),
                visual_style=s.get("visual_style", req.video_style),
                scene_timing=scene_timing,
                audio_timing=audio_timing,
            ))

        if not validated_scenes:
            raise RuntimeError("Gemini output contained zero valid scenes.")

        total_dur = sum(sc.scene_timing.duration_seconds for sc in validated_scenes)

        response_obj = ScriptGenerateResponse(
            title=raw_data.get("title", "Untitled Script"),
            synopsis=raw_data.get("synopsis", ""),
            video_style=raw_data.get("video_style", req.video_style),
            language=raw_data.get("language", req.language),
            total_duration_seconds=total_dur,
            scene_count=len(validated_scenes),
            scenes=validated_scenes,
            speakers=raw_data.get("speakers"),
            global_audio_notes=raw_data.get("global_audio_notes"),
        )

        # Upload directly to Supabase Storage as a JSON file if configured
        try:
            storage_url, storage_path = await SupabaseStorageService.upload_script_json(
                response_obj.model_dump()
            )
            if storage_url:
                response_obj.storage_url = storage_url
                response_obj.storage_path = storage_path
        except Exception as upload_err:
            logger.warning(f"Failed to upload script to Supabase Storage: {upload_err}")

        return response_obj

    # ------------------------------------------------------------------
    # Fallback (no API key configured)
    # ------------------------------------------------------------------
    @classmethod
    def _fallback_response(cls) -> Dict[str, Any]:
        """Deterministic demo script returned when GEMINI_API_KEY is empty."""
        return {
            "title": "The Last Signal",
            "synopsis": (
                "A lone radio astronomer intercepts an anomalous deep-space signal "
                "that could prove humanity is not alone. She races against bureaucratic "
                "shutdown to decode the message before the antenna is decommissioned."
            ),
            "video_style": "cinematic_realism",
            "language": "en",
            "total_duration_seconds": 60,
            "scene_count": 5,
            "speakers": [
                {
                    "name": "Dr. Meera Iyer",
                    "role": "Protagonist — radio astronomer",
                    "voice_style": "warm, determined, mid-range female",
                    "description": "Early 40s, South-Asian descent, wearing a rumpled lab coat over a kurta."
                },
                {
                    "name": "Director Wallace",
                    "role": "Antagonist — observatory director",
                    "voice_style": "clipped, authoritative baritone",
                    "description": "Late 50s, greying temples, formal suit."
                }
            ],
            "global_audio_notes": (
                "Overall tone is tense and atmospheric. Use low-frequency hum undertones "
                "during signal scenes. Mix narration at 70% volume, dialogue at 100%."
            ),
            "scenes": [
                {
                    "scene_number": 1,
                    "scene_title": "The Empty Observatory",
                    "visual_prompt": (
                        "Cinematic wide establishing shot of a massive radio telescope array "
                        "silhouetted against a star-filled indigo sky at twilight. Ground mist drifts "
                        "across red desert terrain. A single lit window glows in the control building."
                    ),
                    "motion_instructions": (
                        "Slow push-in towards the lit control room window over 12 seconds. "
                        "Mist particles drift left to right."
                    ),
                    "camera": {
                        "shot_type": "wide establishing",
                        "movement": "slow dolly in",
                        "angle": "eye level",
                        "transition": "fade in from black"
                    },
                    "dialogue": [],
                    "narrator": {
                        "text": (
                            "At the edge of the Atacama Desert, one woman listened to the universe "
                            "while the rest of humanity slept."
                        ),
                        "voice_style": "warm documentary, slight reverb",
                        "pacing": "slow and deliberate"
                    },
                    "sound_effects": [
                        {"description": "Low wind across open desert", "timing": "0.0s–12.0s", "intensity": "subtle"},
                        {"description": "Distant mechanical hum of telescope servos", "timing": "4.0s–12.0s", "intensity": "background"}
                    ],
                    "background_music": "Sparse ambient piano with soft synth pads, building tension",
                    "visual_style": "cinematic_realism",
                    "scene_timing": {"start_time": "00:00:00", "end_time": "00:00:12", "duration_seconds": 12},
                    "audio_timing": {"narration_start": "1.0s", "narration_end": "10.0s", "dialogue_windows": []}
                },
                {
                    "scene_number": 2,
                    "scene_title": "The Anomaly",
                    "visual_prompt": (
                        "Medium shot inside a dimly lit control room filled with green-glowing monitors "
                        "and blinking signal analysers. Dr. Meera Iyer sits hunched over a spectrogram, "
                        "her face illuminated by scrolling data. A sudden spike of cyan light flashes "
                        "across all screens simultaneously."
                    ),
                    "motion_instructions": (
                        "Meera slowly leans forward, eyes widening. She grabs headphones and presses "
                        "them to her ears. Screens flash in sync."
                    ),
                    "camera": {
                        "shot_type": "medium shot",
                        "movement": "slow push on Meera's face",
                        "angle": "slightly low angle",
                        "transition": "cut"
                    },
                    "dialogue": [
                        {
                            "character": "Dr. Meera Iyer",
                            "text": "That's not noise. That's structured. That's... intentional.",
                            "voice_style": "breathless, trembling excitement",
                            "emotion": "awe",
                            "language": "en"
                        }
                    ],
                    "narrator": {
                        "text": "At 02:47 local time, frequency band 1420 MHz lit up with a pattern no natural source could produce.",
                        "voice_style": "urgent documentary",
                        "pacing": "measured, accelerating slightly"
                    },
                    "sound_effects": [
                        {"description": "Sharp digital beep cascade", "timing": "0.0s–1.5s", "intensity": "loud"},
                        {"description": "Rhythmic pulsing alien signal tone", "timing": "2.0s–12.0s", "intensity": "medium, rising"},
                        {"description": "Keyboard clatter", "timing": "3.0s–6.0s", "intensity": "subtle"}
                    ],
                    "background_music": "Tense orchestral strings, low cello drone",
                    "visual_style": "cinematic_realism",
                    "scene_timing": {"start_time": "00:00:12", "end_time": "00:00:24", "duration_seconds": 12},
                    "audio_timing": {"narration_start": "0.5s", "narration_end": "6.0s", "dialogue_windows": ["7.0s–11.0s"]}
                },
                {
                    "scene_number": 3,
                    "scene_title": "The Confrontation",
                    "visual_prompt": (
                        "Interior office — harsh fluorescent overhead lights. Director Wallace stands "
                        "behind a mahogany desk with decommission paperwork spread out. Meera bursts "
                        "through the door holding a printed spectrogram."
                    ),
                    "motion_instructions": (
                        "Meera strides in, slaps the printout on the desk. Wallace barely glances at it, "
                        "shakes his head. Meera points at the data with conviction."
                    ),
                    "camera": {
                        "shot_type": "over-the-shoulder (Wallace)",
                        "movement": "static, slight handheld drift",
                        "angle": "eye level",
                        "transition": "hard cut"
                    },
                    "dialogue": [
                        {
                            "character": "Dr. Meera Iyer",
                            "text": "You can't shut us down now. Look at this — a repeating prime sequence on hydrogen line. This is contact!",
                            "voice_style": "passionate, rapid delivery",
                            "emotion": "desperate urgency",
                            "language": "en"
                        },
                        {
                            "character": "Director Wallace",
                            "text": "The funding decision was made six months ago, Dr. Iyer. I sympathise, but a spectrogram anomaly doesn't reverse a congressional mandate.",
                            "voice_style": "clipped, dismissive",
                            "emotion": "cold pragmatism",
                            "language": "en"
                        }
                    ],
                    "narrator": None,
                    "sound_effects": [
                        {"description": "Door slamming open", "timing": "0.0s–0.5s", "intensity": "loud"},
                        {"description": "Paper slapping on desk", "timing": "2.0s–2.3s", "intensity": "medium"},
                        {"description": "Fluorescent light buzz", "timing": "0.0s–12.0s", "intensity": "subtle"}
                    ],
                    "background_music": "Staccato strings, tension motif",
                    "visual_style": "cinematic_realism",
                    "scene_timing": {"start_time": "00:00:24", "end_time": "00:00:36", "duration_seconds": 12},
                    "audio_timing": {"narration_start": None, "narration_end": None, "dialogue_windows": ["1.0s–5.5s", "6.0s–11.0s"]}
                },
                {
                    "scene_number": 4,
                    "scene_title": "Decoding at Dawn",
                    "visual_prompt": (
                        "Pre-dawn blue hour. Meera alone in the control room, monitors bathing her "
                        "in blue light. Multiple windows open showing Fourier transforms, binary "
                        "translations, and a slowly resolving image — a star map."
                    ),
                    "motion_instructions": (
                        "Time-lapse of Meera working: typing, scribbling equations, pacing, returning "
                        "to the screen. The star map image sharpens frame by frame."
                    ),
                    "camera": {
                        "shot_type": "close-up on screen, pull back to medium",
                        "movement": "slow crane-out reveal",
                        "angle": "high angle looking down at Meera",
                        "transition": "dissolve"
                    },
                    "dialogue": [
                        {
                            "character": "Dr. Meera Iyer",
                            "text": "It's a map. They're showing us where they are.",
                            "voice_style": "quiet, reverent whisper",
                            "emotion": "wonder",
                            "language": "en"
                        }
                    ],
                    "narrator": {
                        "text": "By dawn, the prime sequence had unfolded into coordinates — a star 12 light-years away, pointing back at Earth.",
                        "voice_style": "soft, awed",
                        "pacing": "slow, letting the weight land"
                    },
                    "sound_effects": [
                        {"description": "Soft digital processing hum", "timing": "0.0s–12.0s", "intensity": "background"},
                        {"description": "Gentle chime on decode completion", "timing": "9.0s–9.5s", "intensity": "clear"}
                    ],
                    "background_music": "Ethereal choir pad with rising hope motif",
                    "visual_style": "cinematic_realism",
                    "scene_timing": {"start_time": "00:00:36", "end_time": "00:00:48", "duration_seconds": 12},
                    "audio_timing": {"narration_start": "0.5s", "narration_end": "7.0s", "dialogue_windows": ["8.0s–11.0s"]}
                },
                {
                    "scene_number": 5,
                    "scene_title": "The Broadcast",
                    "visual_prompt": (
                        "Epic wide shot at sunrise. The full telescope array pivots in unison, "
                        "dishes tilting skyward. Golden sunlight floods the desert. Meera stands "
                        "at the base of the primary dish, looking up, the decoded star map "
                        "glowing on a tablet in her hand."
                    ),
                    "motion_instructions": (
                        "Telescope dishes rotate in dramatic unison. Camera rises alongside the "
                        "primary dish. Meera lifts her gaze to the sky. Final frame: the stars "
                        "visible in the brightening sky."
                    ),
                    "camera": {
                        "shot_type": "epic wide, transitioning to low-angle hero",
                        "movement": "crane up alongside telescope dish",
                        "angle": "low angle, hero framing",
                        "transition": "dissolve from previous scene"
                    },
                    "dialogue": [
                        {
                            "character": "Dr. Meera Iyer",
                            "text": "This is Atacama Station. We hear you. We're coming.",
                            "voice_style": "strong, determined",
                            "emotion": "resolve and hope",
                            "language": "en"
                        }
                    ],
                    "narrator": {
                        "text": "On a quiet dawn in the driest desert on Earth, humanity answered the cosmos — and the cosmos listened.",
                        "voice_style": "grand, cinematic finale",
                        "pacing": "slow, emphatic, final"
                    },
                    "sound_effects": [
                        {"description": "Massive telescope servo motors engaging", "timing": "0.0s–4.0s", "intensity": "loud mechanical"},
                        {"description": "Radio transmission burst", "timing": "8.0s–10.0s", "intensity": "sharp, clear"},
                        {"description": "Wind across desert at dawn", "timing": "0.0s–12.0s", "intensity": "gentle"}
                    ],
                    "background_music": "Full orchestral swell — brass, strings, and choir climax",
                    "visual_style": "cinematic_realism",
                    "scene_timing": {"start_time": "00:00:48", "end_time": "00:01:00", "duration_seconds": 12},
                    "audio_timing": {"narration_start": "5.0s", "narration_end": "11.5s", "dialogue_windows": ["1.0s–4.5s"]}
                }
            ]
        }
