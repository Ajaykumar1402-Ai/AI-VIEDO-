"""
Pydantic schemas for the SIVACINE AI Universal Script Generator.

These models define the request/response contract for POST /api/story/generate.
They are independent of the database-backed Story/Scene models used elsewhere.
"""

from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Union, Dict, Any
from enum import Enum


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------
class VideoStyle(str, Enum):
    """Supported video style categories."""
    cinematic_realism = "cinematic_realism"
    cartoon_2d = "cartoon_2d"
    cartoon_3d = "cartoon_3d"
    anime = "anime"
    documentary = "documentary"
    advertisement = "advertisement"
    educational = "educational"
    sci_fi = "sci_fi"
    horror = "horror"
    fantasy = "fantasy"
    noir = "noir"
    stop_motion = "stop_motion"
    watercolor = "watercolor"
    pixel_art = "pixel_art"
    custom = "custom"


# ---------------------------------------------------------------------------
# Request
# ---------------------------------------------------------------------------
class ScriptGenerateRequest(BaseModel):
    """
    Input for the universal script generator.
    A single natural-language prompt plus optional style/duration hints.
    """
    prompt: str = Field(
        ...,
        min_length=5,
        max_length=8000,
        description="Natural-language description of the video concept."
    )
    video_style: str = Field(
        default="cinematic_realism",
        max_length=128,
        description=(
            "Visual style category. Use a VideoStyle enum value or any free-text "
            "descriptor (e.g. 'Miyazaki-inspired watercolor')."
        )
    )
    target_duration_seconds: int = Field(
        default=60,
        ge=10,
        le=600,
        description="Total target video duration in seconds (10–600)."
    )
    language: str = Field(
        default="en",
        max_length=32,
        description="Primary language for dialogue and narration (ISO 639-1)."
    )
    include_narration: bool = Field(
        default=True,
        description="Whether to generate narrator voiceover scripts."
    )
    include_dialogue: bool = Field(
        default=True,
        description="Whether to generate character dialogue."
    )
    include_sound_effects: bool = Field(
        default=True,
        description="Whether to generate sound-effect and ambient-audio cues."
    )

    @field_validator("prompt", mode="before")
    @classmethod
    def clean_prompt(cls, v: str) -> str:
        if isinstance(v, str):
            v = v.strip()
            if not v:
                raise ValueError("Prompt cannot be blank.")
        return v


# ---------------------------------------------------------------------------
# Response – nested models (leaf → root)
# ---------------------------------------------------------------------------

class DialogueLine(BaseModel):
    """A single line of spoken dialogue within a scene."""
    character: str = Field(..., description="Name of the speaking character.")
    text: str = Field(..., description="The spoken dialogue line.")
    voice_style: Optional[str] = Field(
        None,
        description="Voice style hint (e.g. 'deep baritone', 'child-like', 'robotic')."
    )
    emotion: Optional[str] = Field(
        None,
        description="Emotional tone (e.g. 'angry', 'whispering', 'excited')."
    )
    language: Optional[str] = Field(
        None,
        description="Language of this specific line if it differs from the scene default."
    )


class NarratorScript(BaseModel):
    """Narrator voiceover instructions for a scene."""
    text: str = Field(..., description="Full narrator script for this scene.")
    voice_style: Optional[str] = Field(
        None,
        description="Narrator voice style (e.g. 'warm documentary', 'dramatic movie trailer')."
    )
    pacing: Optional[str] = Field(
        None,
        description="Delivery pacing guidance (e.g. 'slow and deliberate', 'rapid-fire')."
    )


class SoundEffect(BaseModel):
    """A single sound effect or ambient audio cue."""
    description: str = Field(..., description="What the sound is (e.g. 'thunder crack').")
    timing: Optional[str] = Field(
        None,
        description="When the sound plays relative to the scene (e.g. '0.0s–2.0s')."
    )
    intensity: Optional[str] = Field(
        None,
        description="Loudness/intensity level (e.g. 'subtle', 'loud', 'crescendo')."
    )


class CameraInstruction(BaseModel):
    """Camera movement and framing for a scene."""
    shot_type: Optional[str] = Field(
        None,
        description="Shot type (e.g. 'wide establishing', 'close-up', 'over-the-shoulder')."
    )
    movement: Optional[str] = Field(
        None,
        description="Camera movement (e.g. 'slow dolly in', 'crane up', 'handheld shaky')."
    )
    angle: Optional[str] = Field(
        None,
        description="Camera angle (e.g. 'low angle', 'bird's eye', 'dutch tilt')."
    )
    transition: Optional[str] = Field(
        None,
        description="Transition INTO this scene (e.g. 'cut', 'fade in', 'dissolve')."
    )


class SceneTiming(BaseModel):
    """Timing metadata for a scene."""
    start_time: Optional[str] = Field(None, description="Scene start offset (e.g. '00:00:15').")
    end_time: Optional[str] = Field(None, description="Scene end offset (e.g. '00:00:23').")
    duration_seconds: int = Field(..., ge=1, le=120, description="Scene duration in seconds.")


class AudioTiming(BaseModel):
    """Audio-layer timing for narration and dialogue within a scene."""
    narration_start: Optional[str] = Field(
        None, description="Narration start offset relative to scene start."
    )
    narration_end: Optional[str] = Field(
        None, description="Narration end offset relative to scene start."
    )
    dialogue_windows: Optional[List[Union[str, Dict[str, Any]]]] = Field(
        None,
        description="Time windows for dialogue playback (e.g. ['2.0s–4.5s', '6.0s–8.0s'] or [{'start': '00:00:10', 'end': '00:00:14'}])."
    )


class ScriptScene(BaseModel):
    """Complete specification for one scene of the generated script."""
    scene_number: int = Field(..., ge=1, description="1-indexed scene position.")
    scene_title: Optional[str] = Field(None, description="Short title or slug for the scene.")
    visual_prompt: str = Field(
        ...,
        description="Detailed visual description for AI video generation."
    )
    motion_instructions: Optional[str] = Field(
        None,
        description="Subject motion and action choreography within the frame."
    )
    camera: Optional[CameraInstruction] = Field(
        None, description="Camera framing, movement, and transition."
    )
    dialogue: List[DialogueLine] = Field(
        default_factory=list, description="Ordered character dialogue lines."
    )
    narrator: Optional[NarratorScript] = Field(
        None, description="Narrator voiceover script."
    )
    sound_effects: List[SoundEffect] = Field(
        default_factory=list, description="Sound effects and ambient audio cues."
    )
    background_music: Optional[str] = Field(
        None,
        description="Background music description (e.g. 'tense orchestral strings')."
    )
    visual_style: Optional[str] = Field(
        None, description="Per-scene visual style override."
    )
    scene_timing: SceneTiming = Field(
        ..., description="Timing and duration for this scene."
    )
    audio_timing: Optional[AudioTiming] = Field(
        None, description="Audio-layer timing details."
    )


class ScriptGenerateResponse(BaseModel):
    """
    Top-level response from the universal script generator.
    Contains the full structured script with all scenes and metadata.
    """
    title: str = Field(..., description="Generated title for the video.")
    synopsis: str = Field(..., description="Brief 2-3 sentence synopsis.")
    video_style: str = Field(..., description="Visual style applied to the script.")
    language: str = Field(..., description="Primary language of the script.")
    total_duration_seconds: int = Field(
        ..., description="Sum of all scene durations."
    )
    scene_count: int = Field(..., ge=1, description="Number of scenes.")
    scenes: List[ScriptScene] = Field(..., description="Ordered list of scenes.")
    speakers: Optional[List[dict]] = Field(
        None,
        description=(
            "Unique speakers/characters with voice-style metadata. "
            "Each entry: {name, role, voice_style, description}."
        )
    )
    global_audio_notes: Optional[str] = Field(
        None,
        description="Project-wide audio direction notes."
    )
    storage_url: Optional[str] = Field(
        None,
        description="Public URL to the stored JSON script in Supabase Storage."
    )
    storage_path: Optional[str] = Field(
        None,
        description="Storage path of the JSON script in the Supabase bucket."
    )
