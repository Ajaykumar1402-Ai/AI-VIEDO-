import os
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from datetime import datetime, timezone
import logging

from ..database import get_db, SessionLocal
from ..models.user import User
from ..models.project import Project
from ..models.story import Story
from ..models.scene import Scene
from ..models.job import GenerationJob
from ..schemas.story import (
    ProjectCreate,
    ProjectResponse,
    StoryGenerateRequest,
    StorySchema,
    SceneSchema,
    SceneDialogue,
    TTSGenerateRequest,
    LTXExportSchema,
    JobResponse
)
from ..security import get_current_user
from ..services.story_service import StoryService
from ..services.tts_service import TTSService
from ..config import settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/projects", tags=["Projects & Story Generation"])

def verify_project_ownership(project_id: UUID, current_user: User, db: Session) -> Project:
    """Helper to verify that a project exists and belongs to the authenticated user."""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    if project.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden - You do not own this project"
        )
    return project

# -------------------------------------------------------------------
# 1. Project Management
# -------------------------------------------------------------------
@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(
    project_in: ProjectCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new storytelling project."""
    new_project = Project(
        user_id=current_user.id,
        title=project_in.title.strip(),
        description=project_in.description.strip() if project_in.description else None
    )
    db.add(new_project)
    db.commit()
    db.refresh(new_project)
    return ProjectResponse.model_validate(new_project)

@router.get("", response_model=List[ProjectResponse])
def list_projects(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all projects owned by the authenticated user."""
    projects = db.query(Project).filter(Project.user_id == current_user.id).order_by(Project.created_at.desc()).all()
    return [ProjectResponse.model_validate(p) for p in projects]

@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(
    project_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get project details."""
    project = verify_project_ownership(project_id, current_user, db)
    return ProjectResponse.model_validate(project)

# -------------------------------------------------------------------
# 2. Gemini Story Generation (POST /api/projects/{project_id}/story)
# -------------------------------------------------------------------
@router.post("/{project_id}/story", response_model=StorySchema)
async def generate_story(
    project_id: UUID,
    req: StoryGenerateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate complete structured story with sequential scenes and visual prompts via Gemini.
    Persists to PostgreSQL and writes canonical story.json.
    """
    verify_project_ownership(project_id, current_user, db)

    # Execute story generation
    story_schema = await StoryService.generate_and_save_story(project_id, req, db)
    return story_schema

# -------------------------------------------------------------------
# 3. Retrieve Story (GET /api/projects/{project_id}/story)
# -------------------------------------------------------------------
@router.get("/{project_id}/story", response_model=StorySchema)
def get_story(
    project_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve saved story and ordered scenes for a project."""
    verify_project_ownership(project_id, current_user, db)

    story = db.query(Story).filter(Story.project_id == project_id).order_by(Story.created_at.desc()).first()
    if not story:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No story found for this project. Generate one using POST /api/projects/{project_id}/story."
        )

    scenes_data = []
    for s in story.scenes:
        dialogue_items = [SceneDialogue(**d) for d in (s.dialogue or []) if isinstance(d, dict)]
        scenes_data.append(SceneSchema(
            scene_id=s.id,
            scene_number=s.scene_number,
            duration_seconds=s.duration_seconds,
            visual_prompt=s.visual_prompt,
            narration=s.narration,
            dialogue=dialogue_items,
            visual_style=s.visual_style or story.visual_style,
            status=s.status,
            audio_path=s.audio_path
        ))

    return StorySchema(
        story_id=story.id,
        project_id=story.project_id,
        version=story.version,
        title=story.title,
        language=story.language,
        genre=story.genre,
        target_duration_seconds=story.target_duration_seconds,
        visual_style=story.visual_style,
        scenes=scenes_data,
        created_at=story.created_at
    )

# -------------------------------------------------------------------
# 4. Generate TTS Narration (POST /api/projects/{project_id}/tts)
# -------------------------------------------------------------------
@router.post("/{project_id}/tts", response_model=StorySchema)
def generate_tts_narration(
    project_id: UUID,
    req: TTSGenerateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Synthesize speech narration for project scenes using the self-hosted TTS engine.
    Stores audio artifacts and updates scene audio_path references in PostgreSQL.
    """
    verify_project_ownership(project_id, current_user, db)

    story = db.query(Story).filter(Story.project_id == project_id).order_by(Story.created_at.desc()).first()
    if not story:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No story found for this project."
        )

    # Filter target scenes
    target_scenes = story.scenes
    if req.scene_ids:
        target_ids = set(req.scene_ids)
        target_scenes = [s for s in story.scenes if s.id in target_ids]

    for scene in target_scenes:
        text_to_speak = scene.narration
        if not text_to_speak and scene.dialogue:
            text_to_speak = " ".join([d.get("text", "") for d in scene.dialogue if isinstance(d, dict)])

        if text_to_speak:
            result = TTSService.generate_speech(
                text=text_to_speak,
                project_id=project_id,
                story_id=story.id,
                scene_id=scene.id,
                language=req.language or story.language,
                voice_id=req.voice_id or "default"
            )
            if result.success and result.artifact_path:
                scene.audio_path = result.artifact_path
                scene.status = "audio_generated"

    db.commit()

    # Re-export updated story.json
    scenes_data = []
    for s in story.scenes:
        dialogue_items = [SceneDialogue(**d) for d in (s.dialogue or []) if isinstance(d, dict)]
        scenes_data.append(SceneSchema(
            scene_id=s.id,
            scene_number=s.scene_number,
            duration_seconds=s.duration_seconds,
            visual_prompt=s.visual_prompt,
            narration=s.narration,
            dialogue=dialogue_items,
            visual_style=s.visual_style or story.visual_style,
            status=s.status,
            audio_path=s.audio_path
        ))

    story_schema = StorySchema(
        story_id=story.id,
        project_id=story.project_id,
        version=story.version,
        title=story.title,
        language=story.language,
        genre=story.genre,
        target_duration_seconds=story.target_duration_seconds,
        visual_style=story.visual_style,
        scenes=scenes_data,
        created_at=story.created_at
    )
    StoryService._save_story_json_artifact(project_id, story.id, story_schema)
    return story_schema

# -------------------------------------------------------------------
# 5. Export for LTX-2.5 Video Generation (GET /api/projects/{project_id}/export)
# -------------------------------------------------------------------
@router.get("/{project_id}/export", response_model=LTXExportSchema)
def export_for_video_generation(
    project_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Export canonical JSON contract for LTX-2.5 AI Video Generation team.
    Includes stable scene UUIDs, visual prompts, durations, and audio paths.
    """
    verify_project_ownership(project_id, current_user, db)

    story = db.query(Story).filter(Story.project_id == project_id).order_by(Story.created_at.desc()).first()
    if not story:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No story found to export for this project."
        )

    scenes_data = []
    for s in story.scenes:
        dialogue_items = [SceneDialogue(**d) for d in (s.dialogue or []) if isinstance(d, dict)]
        scenes_data.append(SceneSchema(
            scene_id=s.id,
            scene_number=s.scene_number,
            duration_seconds=s.duration_seconds,
            visual_prompt=s.visual_prompt,
            narration=s.narration,
            dialogue=dialogue_items,
            visual_style=s.visual_style or story.visual_style,
            status=s.status,
            audio_path=s.audio_path
        ))

    return LTXExportSchema(
        schema_version="1.0.0",
        project_id=story.project_id,
        story_id=story.id,
        title=story.title,
        language=story.language,
        genre=story.genre,
        target_duration_seconds=story.target_duration_seconds,
        visual_style=story.visual_style,
        scenes=scenes_data
    )

# -------------------------------------------------------------------
# 6. Authenticated Audio Artifact Stream
# -------------------------------------------------------------------
@router.get("/{project_id}/audio/{scene_id}")
def get_scene_audio(
    project_id: UUID,
    scene_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Stream or download audio artifact for an authorized scene."""
    verify_project_ownership(project_id, current_user, db)

    scene = db.query(Scene).filter(Scene.id == scene_id).first()
    if not scene or not scene.audio_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Audio artifact not found for this scene."
        )

    # Secure path resolution preventing directory traversal
    base_root = os.path.abspath(settings.OUTPUT_ROOT)
    requested_file = os.path.abspath(os.path.join(base_root, "..", scene.audio_path))
    if not os.path.exists(requested_file):
        requested_file = os.path.abspath(os.path.join(base_root, str(project_id), str(scene.story_id), "audio", f"{scene_id}.wav"))

    if not os.path.exists(requested_file):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Audio file missing on storage disk."
        )

    return FileResponse(requested_file, media_type="audio/wav", filename=f"scene_{scene.scene_number}.wav")
