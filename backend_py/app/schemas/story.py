from pydantic import BaseModel, Field, field_validator, model_validator
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime

class SceneDialogue(BaseModel):
    character: str = Field(..., min_length=1, max_length=100, description="Character name")
    text: str = Field(..., min_length=1, max_length=1000, description="Dialogue spoken text")
    voice_id: Optional[str] = Field(None, description="Optional speaker voice identifier")

class SceneSchema(BaseModel):
    scene_id: UUID = Field(..., description="Stable unique scene UUID")
    scene_number: int = Field(..., ge=1, description="1-indexed sequential position")
    duration_seconds: int = Field(..., ge=1, le=120, description="Scene duration in seconds")
    visual_prompt: str = Field(..., min_length=5, max_length=2000, description="Detailed cinematic prompt for video engine")
    narration: Optional[str] = Field(None, max_length=2000, description="Voiceover narration text")
    dialogue: List[SceneDialogue] = Field(default_factory=list, description="Ordered dialogue list")
    visual_style: Optional[str] = Field(None, description="Visual aesthetic style override")
    status: str = Field(default="pending", description="pending, audio_generated, video_generated")
    audio_path: Optional[str] = Field(None, description="Relative path or safe URI to audio artifact")

    model_config = {
        "from_attributes": True
    }

class StoryGenerateRequest(BaseModel):
    idea: str = Field(..., min_length=5, max_length=4000, description="Core story idea or plot concept")
    genre: str = Field(default="science_fiction", max_length=64, description="Story genre (e.g., fantasy, drama, scifi)")
    language: str = Field(default="en", max_length=32, description="Target narration language")
    target_duration_seconds: int = Field(default=60, ge=10, le=300, description="Total video target duration (10-300s)")
    visual_style: str = Field(default="cinematic realism", max_length=128, description="Artistic style for visuals")
    narration_enabled: bool = Field(default=True, description="Generate narration voiceover text")
    dialogue_enabled: bool = Field(default=True, description="Generate character dialogue")

    @field_validator("idea", mode="before")
    @classmethod
    def clean_idea(cls, v: str) -> str:
        if isinstance(v, str):
            clean = v.strip()
            if not clean:
                raise ValueError("Story idea cannot be blank.")
            return clean
        return v

class StorySchema(BaseModel):
    story_id: UUID
    project_id: UUID
    version: int = 1
    title: str = Field(..., min_length=1, max_length=255)
    language: str
    genre: str
    target_duration_seconds: int
    visual_style: str
    scenes: List[SceneSchema]
    created_at: Optional[datetime] = None

    model_config = {
        "from_attributes": True
    }

    @model_validator(mode="after")
    def validate_story_consistency(self) -> "StorySchema":
        if not self.scenes:
            raise ValueError("Story must contain at least one scene.")
        
        # Validate sequential scene numbers
        scene_nums = [s.scene_number for s in self.scenes]
        expected_nums = list(range(1, len(self.scenes) + 1))
        if scene_nums != expected_nums:
            raise ValueError(f"Scene numbers must be sequential starting at 1. Got: {scene_nums}")
        
        # Validate unique scene IDs
        scene_ids = [s.scene_id for s in self.scenes]
        if len(set(scene_ids)) != len(scene_ids):
            raise ValueError("All scene IDs within a story must be unique.")
        
        return self

class ProjectCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255, description="Project title")
    description: Optional[str] = Field(None, max_length=2000, description="Optional description")

class ProjectResponse(BaseModel):
    id: UUID
    title: str
    description: Optional[str] = None
    created_at: datetime

    model_config = {
        "from_attributes": True
    }

class TTSGenerateRequest(BaseModel):
    scene_ids: Optional[List[UUID]] = Field(None, description="Optional subset of scene IDs to synthesize")
    voice_id: Optional[str] = Field("default", description="TTS voice identifier")
    language: Optional[str] = Field("en", description="Narration language")

class JobResponse(BaseModel):
    job_id: UUID
    project_id: UUID
    story_id: Optional[UUID] = None
    job_type: str
    status: str
    progress: int
    error_message: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None

    model_config = {
        "from_attributes": True
    }

class LTXExportSchema(BaseModel):
    schema_version: str = "1.0.0"
    project_id: UUID
    story_id: UUID
    title: str
    language: str
    genre: str
    target_duration_seconds: int
    visual_style: str
    scenes: List[SceneSchema]
