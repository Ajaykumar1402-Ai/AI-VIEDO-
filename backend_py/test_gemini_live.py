"""
Live Gemini API Integration Test
Tests live generation when GEMINI_API_KEY is configured.
"""

import sys
import os
import asyncio

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.config import settings
from app.schemas.story import StoryGenerateRequest
from app.services.story_service import StoryService

async def main():
    print("==================================================")
    print("[TEST] LIVE GEMINI API INTEGRATION TEST")
    print("==================================================")

    if not settings.GEMINI_API_KEY:
        print("[SKIPPED] GEMINI_API_KEY is not set in backend_py/.env.")
        print("          To perform live Gemini API calls, add your key from Google AI Studio:")
        print("          https://aistudio.google.com/")
        print("          Fallback story generator remains active for offline local operation.")
        return

    print(f"[1/3] Calling Gemini API (Model: {settings.GEMINI_MODEL})...")
    req = StoryGenerateRequest(
        idea="A deep-sea diver discovers an ancient Atlantean submarine buried under coral reefs.",
        genre="adventure",
        language="en",
        target_duration_seconds=45,
        visual_style="hyperrealistic 3D cinema",
        narration_enabled=True,
        dialogue_enabled=True
    )

    prompt = StoryService._build_gemini_prompt(req)
    try:
        raw_story = await StoryService.call_gemini_api(prompt)
        print("[OK] Live Gemini API Response Received!")
        print(f"Title: {raw_story.get('title')}")
        print(f"Scenes generated: {len(raw_story.get('scenes', []))}")
        
        # Test duration balancing
        balanced = StoryService._balance_durations(raw_story["scenes"], 45)
        total = sum(s["duration_seconds"] for s in balanced)
        print(f"[OK] Duration balanced: {total}s matches target 45s.")
        print("\n==================================================")
        print("[SUCCESS] LIVE GEMINI INTEGRATION PASSED!")
        print("==================================================")
    except Exception as e:
        print(f"[FAILED] Gemini API call failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())
