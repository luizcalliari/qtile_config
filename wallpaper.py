import asyncio
import os
import random
from pathlib import Path

import httpx
from dotenv import load_dotenv

load_dotenv()

WALLPAPER_DIR = Path(os.path.expanduser("~")) / "wallpaper"


class Wallpaper:
    def __init__(self, nasa_api_key=None):
        self.NASA_API_KEY = nasa_api_key
        self.NASA_API_URL = "https://api.nasa.gov/planetary/apod"

        self.IMAGE_DATA = None
        self.IMAGE_DATA_VERTICAL = None
        self.IMAGE_DATA_HORIZONTAL = None
        self.IMAGE_TITLE = None

        self.WALLPAPER_DIR = WALLPAPER_DIR

    async def validate_image(self, url: str):
        async with httpx.AsyncClient() as client:
            image_response = await client.get(url, timeout=30)
            image_response.raise_for_status()

        return image_response.content

    async def fetch_nasa_daily_image(self):
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    url=self.NASA_API_URL,
                    params={"api_key": self.NASA_API_KEY},
                    timeout=30,
                )
                response.raise_for_status()
            response = response.json()

            if response.get("media_type") != "image":
                print("Today's content is not an image. Skipping.")
                return

            if image_url_vert := response.get("url"):
                self.IMAGE_DATA_VERTICAL = await self.validate_image(image_url_vert)

            if image_url_hori := response.get("hdurl"):
                self.IMAGE_DATA_HORIZONTAL = await self.validate_image(image_url_hori)

            self.IMAGE_TITLE = response.get("title") + ".jpg"

        except Exception:
            raise

    def image_already_exists(self, extra_path=None):
        if extra_path:
            wallpaper_dir = self.WALLPAPER_DIR / extra_path
            wallpaper_dir.mkdir(parents=True, exist_ok=True)
        else:
            wallpaper_dir = self.WALLPAPER_DIR

        return self.IMAGE_TITLE in os.listdir(wallpaper_dir)

    async def save_image(self, image_data, extra_path=None):
        if extra_path:
            wallpaper_dir = self.WALLPAPER_DIR / extra_path
        else:
            wallpaper_dir = self.WALLPAPER_DIR

        if not image_data:
            raise ValueError("No image data available. Did fetch_nasa_daily_image() succeed?")
        else:
            with open(wallpaper_dir / self.IMAGE_TITLE, "wb") as f:
                f.write(image_data)

    async def add_nasa_daily_image_to_folder(self):
        self.WALLPAPER_DIR.mkdir(parents=True, exist_ok=True)

        tasks_to_run = []

        if not self.image_already_exists(extra_path="vertical"):
            tasks_to_run.append(
                asyncio.create_task(self.save_image(image_data=self.IMAGE_DATA_VERTICAL, extra_path="vertical"))
            )
        if not self.image_already_exists(extra_path="horizontal"):
            tasks_to_run.append(
                asyncio.create_task(self.save_image(image_data=self.IMAGE_DATA_HORIZONTAL, extra_path="horizontal"))
            )

        results = await asyncio.gather(
            *tasks_to_run,
            return_exceptions=True
        )
        print(results)
        print("Wallpaper saved.")


async def save_wallpaper():
    while True:
        try:
            wallpaper = Wallpaper(nasa_api_key=os.getenv("NASA_API_KEY"))
            await wallpaper.fetch_nasa_daily_image()
            await wallpaper.add_nasa_daily_image_to_folder()
        except Exception as err:
            print(f"Error: {err}")
            print("Retrying in 60 seconds...")
            await asyncio.sleep(60)
        else:
            break


def get_random_wallpaper(extra_path=None):
    if extra_path:
        wallpaper_dir = WALLPAPER_DIR / extra_path
    else:
        wallpaper_dir = WALLPAPER_DIR

    try:
        files = [os.path.join(wallpaper_dir, f) for f in os.listdir(wallpaper_dir)
                 if f.endswith(('.jpg', '.png', '.jpeg'))]
        return random.choice(files) if files else None
    except FileNotFoundError:
        return None


if __name__ == "__main__":
    asyncio.run(save_wallpaper())
    # print(get_random_wallpaper(extra_path="vertical"))
    # print(get_random_wallpaper(extra_path="horizontal"))
