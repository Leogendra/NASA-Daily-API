from nasa_scraper import scrappe_nasa, resize_image
from fastapi import FastAPI, HTTPException, Request, Query, Path
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from datetime import datetime, timedelta
import time, os, random
import logging

logging.basicConfig(
    filename="app.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger("nasa_api")

BASE_URL = "http://localhost:8000"
BASE_IMAGE_DIR = "public"
app = FastAPI()
app.mount("/static", StaticFiles(directory="public/"), name="static")




def process_image(date: str, w: int, h: int):
    try:
        logger.info(f"Processing image for date: {date}, width: {w}, height: {h}")
        image_path = scrappe_nasa(date)
        if not image_path:
            raise HTTPException(status_code=404, detail="NASA image not found for this date.")

        if (w > 0 and h > 0):
            output_folder = f"public/{w}x{h}"
            resized_path = f"{output_folder}/{date}.jpg"
            os.makedirs(output_folder, exist_ok=True)
            resize_image(image_path, resized_path, w, h, crop=True)
            logger.info(f"Image resized successfully: {resized_path}")
            return resized_path

        else:
            logger.info(f"Returning original image: {image_path}")
            return image_path

    except Exception as e:
        logger.exception(f"Error processing image for date: {date}, width: {w}, height: {h}")
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")


@app.get("/")
def read_root():
    return { "message": (
        "Welcome to the NASA Daily Picture API! "
        "Docs: https://github.com/Leogendra/NASA-Daily-API"
    )}


@app.get("/daily/", response_class=FileResponse)
def get_daily_nasa(w: int = Query(0), h: int = Query(0)):
    today = time.strftime("%y%m%d")
    image_path = process_image(today, w, h)
    return FileResponse(image_path, media_type="image/jpeg")


@app.get("/date/{date}/", response_class=FileResponse)
def get_image_by_date(
    date: str = Path(..., regex=r"^\d{6}$", description="Date au format YYMMDD"),
    w: int = Query(0),
    h: int = Query(0),
):
    image_path = process_image(date, w, h)
    return FileResponse(image_path, media_type="image/jpeg")


@app.get("/random/", response_class=FileResponse)
def get_random_image(w: int = Query(0), h: int = Query(0)):
    try:
        start_date = datetime(1996, 1, 1)
        end_date = datetime.now()
        random_days = random.randint(0, (end_date - start_date).days)
        random_date = start_date + timedelta(days=random_days)

        random_date_str = random_date.strftime("%y%m%d")
        image_path = process_image(random_date_str, w, h)
        return FileResponse(image_path, media_type="image/jpeg")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/download/{date}/", response_class=FileResponse)
def download_image(
    date: str = Path(..., regex=r"^\d{6}$", description="Date au format YYMMDD"),
    w: int = Query(0),
    h: int = Query(0),
):
    image_path = process_image(date, w, h)
    return FileResponse(image_path, media_type="image/jpeg", filename=f"{date}_{w}x{h}.jpg")