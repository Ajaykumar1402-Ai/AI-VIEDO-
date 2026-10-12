import asyncio
import edge_tts
import os

async def main():
    text = "Commander Arun touched the glowing alien obelisk on Mars."
    voice = "en-US-ChristopherNeural"
    output_file = "test_synth.wav"
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_file)
    size = os.path.getsize(output_file)
    print(f"[OK] Real Neural TTS Synthesized! Output: {output_file}, Size: {size} bytes")

if __name__ == "__main__":
    asyncio.run(main())
