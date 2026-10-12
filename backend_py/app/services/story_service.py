import json
import uuid
import os
import re
import logging
import httpx
from typing import Dict, Any, List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, status

from ..config import settings
from ..models.story import Story
from ..models.scene import Scene
from ..models.project import Project
from ..schemas.story import StoryGenerateRequest, StorySchema, SceneSchema, SceneDialogue

logger = logging.getLogger(__name__)

class StoryService:

    @staticmethod
    def _build_gemini_prompt(req: StoryGenerateRequest) -> str:
        narration_inst = "Include engaging voiceover narration for each scene." if req.narration_enabled else "Do not include narration (narration should be null)."
        dialogue_inst = "Include natural character dialogue where appropriate." if req.dialogue_enabled else "Do not include dialogue (dialogue should be empty list [])."

        # Estimate scene count based on duration (approx 6-10s per scene)
        avg_scene_dur = 8
        target_scene_count = max(3, min(15, round(req.target_duration_seconds / avg_scene_dur)))

        return f"""
You are an expert Hollywood screenwriter and AI cinematic director for LTX-2.5 video generation.
Create a structured, complete cinematic story based on the user's concept.

CONCEPT: {req.idea}
GENRE: {req.genre}
LANGUAGE: {req.language}
VISUAL STYLE: {req.visual_style}
TARGET DURATION: {req.target_duration_seconds} seconds
RECOMMENDED SCENE COUNT: {target_scene_count} scenes

REQUIREMENTS:
1. Complete Narrative Arc: Beginning, development, climax, and resolution.
2. Structure into sequential scenes (1 to {target_scene_count}).
3. Visual Prompt: Write a descriptive, highly specific visual prompt for each scene suitable for LTX-2.5 AI video generation (camera angle, lighting, subject action, environment, atmosphere).
4. {narration_inst}
5. {dialogue_inst}
6. Scene Durations: Each scene duration must be between 4 and 15 seconds, and the SUM OF ALL SCENE DURATIONS MUST EXACTLY EQUAL {req.target_duration_seconds} seconds.

OUTPUT FORMAT:
Return ONLY a valid, raw JSON object (without markdown fences, backticks, or preamble) with this exact schema:
{{
  "title": "Story Title",
  "synopsis": "Brief 2-sentence synopsis",
  "scenes": [
    {{
      "scene_number": 1,
      "duration_seconds": 8,
      "visual_prompt": "Wide cinematic 8k shot of an astronaut traversing the red Martian dunes at sunset...",
      "narration": "Arun had spent three months exploring the silent expanse of Mars.",
      "dialogue": [
        {{
          "character": "Arun",
          "text": "The signal is getting stronger.",
          "voice_id": "arun"
        }}
      ],
      "visual_style": "{req.visual_style}"
    }}
  ]
}}
"""

    @classmethod
    async def call_gemini_api(cls, prompt: str) -> Dict[str, Any]:
        """
        Execute Gemini API request with strict timeouts and error handling.
        """
        if not settings.GEMINI_API_KEY:
            logger.warning("GEMINI_API_KEY is not configured in .env. Using high-quality fallback generator.")
            return cls._fallback_story_generator(prompt)

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{settings.GEMINI_MODEL}:generateContent?key={settings.GEMINI_API_KEY}"

        payload = {
            "contents": [
                {
                    "parts": [{"text": prompt}]
                }
            ],
            "generationConfig": {
                "temperature": 0.7,
                "topP": 0.95,
                "maxOutputTokens": 4096,
                "responseMimeType": "application/json"
            }
        }

        async with httpx.AsyncClient(timeout=45.0) as client:
            try:
                response = await client.post(url, json=payload)
                if response.status_code == 429:
                    logger.error("Gemini API rate limit exceeded.")
                    raise HTTPException(
                        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                        detail="Gemini AI rate limit or quota exceeded. Please try again shortly."
                    )
                if response.status_code != 200:
                    logger.error(f"Gemini API Error ({response.status_code}): {response.text}")
                    raise HTTPException(
                        status_code=status.HTTP_502_BAD_GATEWAY,
                        detail=f"Gemini API returned error ({response.status_code})."
                    )

                data = response.json()
                raw_text = data["candidates"][0]["content"]["parts"][0]["text"]
                return cls._parse_json_response(raw_text)

            except httpx.TimeoutException:
                logger.error("Gemini API request timed out after 45s.")
                raise HTTPException(
                    status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                    detail="Story generation timed out. Please try again."
                )
            except (KeyError, IndexError) as e:
                logger.error(f"Unexpected Gemini response format: {e}")
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail="Invalid response structure from AI model."
                )

    @classmethod
    def _parse_json_response(cls, raw_text: str) -> Dict[str, Any]:
        """
        Extract and parse JSON from model output with bounded recovery.
        """
        clean = raw_text.strip()
        # Strip markdown fences if present
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
            logger.error(f"Failed to decode JSON from Gemini output: {clean[:200]}")
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="AI model output could not be parsed as valid JSON."
            )

    @classmethod
    def _fallback_story_generator(cls, prompt: str) -> Dict[str, Any]:
        """Deterministic high-quality fallback generator when Gemini API key is not configured."""
        return {
            "title": "The Mars Transmission",
            "synopsis": "An isolated astronaut uncovers an alien beacon humming beneath the Martian surface.",
            "scenes": [
                {
                    "scene_number": 1,
                    "duration_seconds": 15,
                    "visual_prompt": "Cinematic wide 8k drone shot of a solitary astronaut in an illuminated EVA suit walking across desolate red sand dunes on Mars, dust storms swirling under a cobalt sky.",
                    "narration": "Commander Arun had spent eighty sols searching the Martian craters in complete isolation.",
                    "dialogue": [
                        {"character": "Arun", "text": "Base, telemetry sensors are picking up harmonic frequencies from sector 4.", "voice_id": "arun"}
                    ],
                    "visual_style": "cinematic realism"
                },
                {
                    "scene_number": 2,
                    "duration_seconds": 15,
                    "visual_prompt": "Medium shot of the astronaut approaching a massive obsidian spire embedded in the canyon wall, glowing with bioluminescent cyan glyphs.",
                    "narration": "Before him rose an ancient structure, untouched for millions of years.",
                    "dialogue": [
                        {"character": "Arun", "text": "It's not natural. It's a transmission beacon.", "voice_id": "arun"}
                    ],
                    "visual_style": "cinematic realism"
                },
                {
                    "scene_number": 3,
                    "duration_seconds": 15,
                    "visual_prompt": "Close-up of the astronaut's gloved hand reaching out to touch the pulsing alien surface as rings of cyan light ripple outward.",
                    "narration": "With a single touch, humanity's place in the cosmos changed forever.",
                    "dialogue": [
                        {"character": "Arun", "text": "Transmission decoded. We are not alone.", "voice_id": "arun"}
                    ],
                    "visual_style": "cinematic realism"
                },
                {
                    "scene_number": 4,
                    "duration_seconds": 15,
                    "visual_prompt": "Epic pull-back shot showing a pillar of azure light shooting from the spire into the stars, illuminating the entire red planet.",
                    "narration": "The signal echoed through the stars, awaiting the journey back home.",
                    "dialogue": [],
                    "visual_style": "cinematic realism"
                }
            ]
        }

    @classmethod
    def _balance_durations(cls, raw_scenes: List[Dict[str, Any]], target_duration: int) -> List[Dict[str, Any]]:
        """
        Normalize and balance scene durations so that their sum strictly equals target_duration.
        """
        if not raw_scenes:
            return raw_scenes

        n = len(raw_scenes)
        base_dur = target_duration // n
        remainder = target_duration % n

        for idx, scene in enumerate(raw_scenes):
            assigned_dur = base_dur + (1 if idx < remainder else 0)
            scene["duration_seconds"] = max(1, assigned_dur)

        return raw_scenes

    @classmethod
    async def generate_and_save_story(
        cls,
        project_id: UUID,
        req: StoryGenerateRequest,
        db: Session
    ) -> StorySchema:
        """
        Orchestrates Gemini generation, validates data against Pydantic schemas,
        persists to PostgreSQL within a transaction, and writes canonical story.json.
        """
        # 1. Generate story JSON via Gemini
        prompt = cls._build_gemini_prompt(req)
        raw_story = await cls.call_gemini_api(prompt)

        title = raw_story.get("title") or "Untitled Cinematic Story"
        raw_scenes = raw_story.get("scenes", [])

        if not raw_scenes:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="AI story generation produced no scenes."
            )

        # 2. Balance durations to target duration
        raw_scenes = cls._balance_durations(raw_scenes, req.target_duration_seconds)

        # 3. Create Story & Scene DB Models
        story_id = uuid.uuid4()
        new_story = Story(
            id=story_id,
            project_id=project_id,
            version=1,
            title=title,
            language=req.language,
            genre=req.genre,
            visual_style=req.visual_style,
            target_duration_seconds=req.target_duration_seconds,
            story_metadata={"synopsis": raw_story.get("synopsis", "")}
        )

        db_scenes = []
        schema_scenes = []

        for idx, s in enumerate(raw_scenes, start=1):
            scene_id = uuid.uuid4()
            dialogue_data = s.get("dialogue") or []
            if isinstance(dialogue_data, list):
                dialogue_list = [SceneDialogue(**d).model_dump() for d in dialogue_data if isinstance(d, dict)]
            else:
                dialogue_list = []

            db_scene = Scene(
                id=scene_id,
                story_id=story_id,
                scene_number=idx,
                duration_seconds=int(s.get("duration_seconds", 8)),
                visual_prompt=str(s.get("visual_prompt", "")).strip() or "Cinematic visual shot.",
                narration=str(s.get("narration", "")).strip() if s.get("narration") else None,
                dialogue=dialogue_list,
                visual_style=s.get("visual_style") or req.visual_style,
                status="pending",
                audio_path=None
            )
            db_scenes.append(db_scene)

            schema_scene = SceneSchema(
                scene_id=scene_id,
                scene_number=idx,
                duration_seconds=db_scene.duration_seconds,
                visual_prompt=db_scene.visual_prompt,
                narration=db_scene.narration,
                dialogue=[SceneDialogue(**d) for d in dialogue_list],
                visual_style=db_scene.visual_style,
                status=db_scene.status,
                audio_path=None
            )
            schema_scenes.append(schema_scene)

        # 4. Database Transaction
        try:
            db.add(new_story)
            db.flush()
            for db_scene in db_scenes:
                db.add(db_scene)
            db.commit()
            db.refresh(new_story)
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Database error saving story: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error persisting generated story."
            )

        # 5. Export Canonical story.json file to storage
        story_schema = StorySchema(
            story_id=story_id,
            project_id=project_id,
            version=1,
            title=title,
            language=req.language,
            genre=req.genre,
            target_duration_seconds=req.target_duration_seconds,
            visual_style=req.visual_style,
            scenes=schema_scenes,
            created_at=new_story.created_at
        )

        cls._save_story_json_artifact(project_id, story_id, story_schema)
        return story_schema

    @classmethod
    def _save_story_json_artifact(cls, project_id: UUID, story_id: UUID, story: StorySchema) -> str:
        """Writes canonical story.json into outputs/{project_id}/{story_id}/story.json."""
        out_dir = os.path.join(settings.OUTPUT_ROOT, str(project_id), str(story_id))
        os.makedirs(out_dir, exist_ok=True)
        file_path = os.path.join(out_dir, "story.json")

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(story.model_dump_json(indent=2))

        return file_path
