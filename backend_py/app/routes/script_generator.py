"""
SIVACINE AI — Universal Script Generator Route.

POST /api/story/generate

Accepts a natural-language prompt and returns a complete structured JSON script
with video, audio, dialogue, narration, camera, timing, and sound-effect data.

This endpoint is stateless — it does NOT require authentication, database access,
or project ownership. It is a pure Gemini-powered generation endpoint.
"""

import logging
from fastapi import APIRouter, HTTPException, status

from ..schemas.script_generator import ScriptGenerateRequest, ScriptGenerateResponse
from ..services.script_generator_service import ScriptGeneratorService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/story", tags=["Universal Script Generator"])


@router.post(
    "/generate",
    response_model=ScriptGenerateResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate a complete video & audio script from a prompt",
    description=(
        "Universal script generator powered by Gemini. "
        "Supports cartoons, realistic films, anime, documentaries, advertisements, "
        "educational videos, science fiction, and any other video concept. "
        "Returns structured JSON with scenes, visual prompts, camera instructions, "
        "dialogue, narration, sound effects, timings, and speaker metadata."
    ),
)
async def generate_script(req: ScriptGenerateRequest) -> ScriptGenerateResponse:
    """
    Generate a complete structured script from a single natural-language prompt.

    The response includes:
    - Video script title and synopsis
    - Scene-by-scene visual prompts
    - Motion and camera instructions
    - Character dialogue with voice-style and emotion
    - Narrator voiceover script
    - Audio and sound-effect instructions
    - Speaker and voice-style information
    - Scene timings and audio timings
    """
    try:
        result = await ScriptGeneratorService.generate(req)
        return result
    except RuntimeError as exc:
        logger.error(f"Script generation failed: {exc}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        )
    except Exception as exc:
        logger.exception(f"Unexpected error in script generation: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during script generation.",
        )
