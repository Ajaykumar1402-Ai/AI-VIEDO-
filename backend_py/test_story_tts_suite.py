"""
Phase 11 Comprehensive Automated Test Suite: AI Story Generation & Self-Hosted TTS Module
Runs with an isolated transactional test database for unit & integration testing.
"""

import sys
import os
import uuid
from uuid import UUID
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.main import app
from app.database import Base, get_db
from app.models.user import User
from app.models.project import Project
from app.models.story import Story
from app.models.scene import Scene
from app.schemas.story import StoryGenerateRequest, StorySchema, SceneSchema, LTXExportSchema
from app.services.story_service import StoryService
from app.services.tts_service import TTSService, TTSResult

# Setup isolated test database
TEST_DB_URL = "sqlite:///./test_storytelling.db"
test_engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

def override_get_db():
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

def run_suite():
    print("==================================================")
    print("[TEST SUITE] RUNNING COMPREHENSIVE STORY GENERATION & TTS SUITE")
    print("==================================================")

    # Recreate tables in isolated test database
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)
    db = TestSessionLocal()

    user_a_email = f"user_a_{uuid.uuid4().hex[:6]}@sivacine.ai"
    user_b_email = f"user_b_{uuid.uuid4().hex[:6]}@sivacine.ai"
    password = "TestPassword2026!"

    try:
        # 1. Setup User A & User B
        print("\n[TEST 1] Registering User A & User B...")
        res_a = client.post("/api/auth/signup", json={"name": "Director Alpha", "email": user_a_email, "password": password})
        assert res_a.status_code == 201, f"Signup failed: {res_a.text}"
        token_a = res_a.json()["access_token"]
        user_a_id = res_a.json()["user"]["id"]

        res_b = client.post("/api/auth/signup", json={"name": "Director Beta", "email": user_b_email, "password": password})
        assert res_b.status_code == 201, f"Signup failed: {res_b.text}"
        token_b = res_b.json()["access_token"]
        user_b_id = res_b.json()["user"]["id"]
        print("[OK] Users registered and authenticated.")

        # 2. Create Project for User A
        print("\n[TEST 2] Creating Project for User A...")
        res_proj = client.post("/api/projects", json={"title": "Mars Odyssey 2026", "description": "Sci-Fi Short Film"}, headers={"Authorization": f"Bearer {token_a}"})
        assert res_proj.status_code == 201, f"Project creation failed: {res_proj.text}"
        project_a_id = res_proj.json()["id"]
        print(f"[OK] Project Created: {project_a_id}")

        # 3. Test Story Generation & Duration Balancing
        print("\n[TEST 3] Generating Story via POST /api/projects/{id}/story...")
        story_req = {
            "idea": "An astronaut discovers a mysterious glowing obelisk on Mars.",
            "genre": "science_fiction",
            "language": "en",
            "target_duration_seconds": 60,
            "visual_style": "cinematic realism",
            "narration_enabled": True,
            "dialogue_enabled": True
        }
        res_story = client.post(f"/api/projects/{project_a_id}/story", json=story_req, headers={"Authorization": f"Bearer {token_a}"})
        assert res_story.status_code == 200, f"Story generation failed: {res_story.text}"
        story_data = res_story.json()
        story_id = story_data["story_id"]
        scenes = story_data["scenes"]

        print(f"[OK] Story Generated: '{story_data['title']}' with {len(scenes)} scenes.")
        assert len(scenes) >= 3, "Expected at least 3 scenes"
        
        # Verify sequential scene numbering and unique UUIDs
        scene_nums = [s["scene_number"] for s in scenes]
        assert scene_nums == list(range(1, len(scenes) + 1)), f"Scene numbering non-sequential: {scene_nums}"
        
        scene_ids = [s["scene_id"] for s in scenes]
        assert len(set(scene_ids)) == len(scene_ids), "Duplicate scene IDs detected"

        # Verify duration sum strictly matches target_duration_seconds
        total_dur = sum(s["duration_seconds"] for s in scenes)
        assert total_dur == 60, f"Duration mismatch: Expected 60s, got {total_dur}s"
        print(f"[OK] Durations Validated: Total {total_dur}s across {len(scenes)} scenes strictly matches target 60s.")

        # Verify visual prompts non-empty
        for s in scenes:
            assert len(s["visual_prompt"].strip()) > 5, "Empty visual prompt found"
        print("[OK] All visual prompts verified nonempty.")

        # 4. Test Story Retrieval
        print("\n[TEST 4] Retrieving Story via GET /api/projects/{id}/story...")
        res_get_story = client.get(f"/api/projects/{project_a_id}/story", headers={"Authorization": f"Bearer {token_a}"})
        assert res_get_story.status_code == 200, f"Get story failed: {res_get_story.text}"
        assert res_get_story.json()["story_id"] == story_id
        print("[OK] Story retrieval verified.")

        # 5. Security Check: User B Accessing User A's Project (Expect 403 Forbidden)
        print("\n[TEST 5] Security Check: Cross-User Access Isolation (Expect 403 Forbidden)...")
        res_unauthorized = client.get(f"/api/projects/{project_a_id}/story", headers={"Authorization": f"Bearer {token_b}"})
        assert res_unauthorized.status_code == 403, f"Cross-user security failure: {res_unauthorized.status_code}"
        print("[OK] Cross-user security check passed (403 Forbidden).")

        # 6. Test JSON Output Recovery
        print("\n[TEST 6] Testing JSON Recovery parser...")
        raw_markdown_json = '```json\n{"title": "Test Title", "scenes": [{"scene_number": 1, "duration_seconds": 10, "visual_prompt": "Test"}]}\n```'
        parsed = StoryService._parse_json_response(raw_markdown_json)
        assert parsed["title"] == "Test Title"
        print("[OK] Markdown fence recovery verified.")

        # 7. Test TTS Provider Status & Synthesis
        print("\n[TEST 7] Testing TTS Status & Narration Generation...")
        tts_status = TTSService.get_provider_status()
        print(f"TTS Status: {tts_status}")
        assert "provider" in tts_status

        first_scene_id = scenes[0]["scene_id"]
        res_tts = client.post(f"/api/projects/{project_a_id}/tts", json={"scene_ids": [first_scene_id], "voice_id": "arun", "language": "en"}, headers={"Authorization": f"Bearer {token_a}"})
        assert res_tts.status_code == 200, f"TTS generation failed: {res_tts.text}"
        updated_scenes = res_tts.json()["scenes"]
        synth_scene = next(s for s in updated_scenes if s["scene_id"] == first_scene_id)
        assert synth_scene["audio_path"] is not None
        assert synth_scene["status"] == "audio_generated"
        print(f"[OK] Audio generated for scene {first_scene_id} -> Artifact: {synth_scene['audio_path']}")

        # 8. Test LTX-2.5 Video Generation Handoff Export
        print("\n[TEST 8] Testing LTX-2.5 Video Handoff Export (GET /api/projects/{id}/export)...")
        res_export = client.get(f"/api/projects/{project_a_id}/export", headers={"Authorization": f"Bearer {token_a}"})
        assert res_export.status_code == 200, f"Export failed: {res_export.text}"
        export_data = res_export.json()
        assert export_data["schema_version"] == "1.0.0"
        assert export_data["project_id"] == project_a_id
        assert export_data["story_id"] == story_id
        assert len(export_data["scenes"]) == len(scenes)
        assert export_data["scenes"][0]["scene_id"] == scenes[0]["scene_id"]
        print("[OK] LTX-2.5 canonical JSON export contract validated.")

        # 9. Test Audio Streaming Endpoint
        print("\n[TEST 9] Testing Authenticated Audio Stream GET /api/projects/{id}/audio/{scene_id}...")
        res_audio = client.get(f"/api/projects/{project_a_id}/audio/{first_scene_id}", headers={"Authorization": f"Bearer {token_a}"})
        assert res_audio.status_code == 200, f"Audio stream failed: {res_audio.status_code}"
        assert res_audio.headers["content-type"] == "audio/wav"
        print(f"[OK] Audio stream returned 200 OK (size: {len(res_audio.content)} bytes).")

        print("\n==================================================")
        print("[SUCCESS] ALL 9 STORY GENERATION & TTS TESTS PASSED!")
        print("==================================================")

    finally:
        db.close()
        # Clean test sqlite file
        if os.path.exists("./test_storytelling.db"):
            try:
                os.remove("./test_storytelling.db")
            except Exception:
                pass

if __name__ == "__main__":
    run_suite()
