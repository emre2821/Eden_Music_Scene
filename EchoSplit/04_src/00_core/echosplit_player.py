import pygame
import asyncio
import platform

FPS = 60

def setup():
    pygame.mixer.init()
    pygame.mixer.music.load("sample.mp3")  # Replace with your audio file
    pygame.mixer.music.play()

def update_loop():
    # Basic playback control (could be expanded with GUI events)
    if not pygame.mixer.music.get_busy():
        print("Playback finished.")
        # Could loop or load next track here

async def main():
    setup()
    while True:
        update_loop()
        await asyncio.sleep(1.0 / FPS)

if platform.system() == "Emscripten":
    asyncio.ensure_future(main())
else:
    if __name__ == "__main__":
        asyncio.run(main())