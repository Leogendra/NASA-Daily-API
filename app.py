from nasa_scraper import create_folder, scrappe_nasa, resize_image, get_apod_metadata
from flask import Flask, jsonify, send_file, request
import datetime, random

app = Flask(__name__)
PORT = 3400
BASE_IMAGE_DIR = "public"
BASE_URL = f"http://localhost:{PORT}"


def get_current_utc_date() -> str:
    return (datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-5)))).strftime("%y%m%d")


def process_image(date: str, w: int, h: int, crop: bool, minW: int = 0, minH: int = 0):
    try:
        image_path = scrappe_nasa(date, minW, minH)
        if not(image_path):
            image_path, date = "default.jpg", "default"
        
        image_name = f"{date}.jpg"
        if ((w > 0) and (h > 0)):
            output_folder = f"{BASE_IMAGE_DIR}/{w}x{h}"
            resized_path = f"{output_folder}/{date}.jpg"
            resized_name = image_name.replace(".jpg", f"_{w}x{h}.jpg")
            create_folder(output_folder)
            resize_image(image_path, resized_path, w, h, crop=crop)
            return resized_path, resized_name
        else:
            return image_path, image_name
    except Exception as e:
        print(f"Error: {str(e)}")
        return "default.jpg", "default.jpg"


@app.route("/", methods=["GET"])
def read_root():
    return jsonify({
        "message": (
            "Welcome to the NASA Daily Picture API! "
            "Docs: https://github.com/Leogendra/NASA-Daily-API"
        )
    })


@app.route("/daily/", methods=["GET"])
def get_daily_nasa():
    try:
        w = int(request.args.get("w", 0))
        h = int(request.args.get("h", 0))
        crop = request.args.get("crop", "true").lower() == "true"
        download = request.args.get("download", "false").lower() in ["true", "1", "yes"]

        todayUTC = get_current_utc_date()

        image_path, image_name = process_image(todayUTC, w, h, crop)
        if (image_name == "default.jpg"):
            return get_random_image()
        
        if (image_path):
            return send_file(
                image_path,
                mimetype="image/jpeg",
                as_attachment=download,
                download_name=image_name
            )
        else:
            return jsonify({"error": "Image not found"}), 404
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/date/<date>/", methods=["GET"])
def get_image_by_date(date: str):
    try:
        w = int(request.args.get("w", 0))
        h = int(request.args.get("h", 0))
        crop = request.args.get("crop", "true").lower() == "true"
        download = request.args.get("download", "false").lower() in ["true", "1", "yes"]
        if not date.isdigit() or len(date) != 6:
            return jsonify({"error": "Invalid date format. Use YYMMDD."}), 400
        image_path, image_name = process_image(date, w, h, crop)
        
        if (image_path):
            return send_file(
                image_path,
                mimetype="image/jpeg",
                as_attachment=download,
                download_name=image_name
            )
        else:
            return jsonify({"error": "Image not found"}), 404
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/random/", methods=["GET"])
def get_random_image():
    try:
        w = int(request.args.get("w", 0))
        h = int(request.args.get("h", 0))
        crop = request.args.get("crop", "true").lower() == "true"
        minW = int(request.args.get("minW", 0))
        minH = int(request.args.get("minH", 0))
        download = request.args.get("download", "false").lower() in ["true", "1", "yes"]

        start_date = datetime.datetime(1996, 1, 1)
        end_date = datetime.datetime.now()

        nbRetries = 5
        while (nbRetries):
            print(f"Searching for image... {nbRetries} retries left")
            random_days = random.randint(0, (end_date - start_date).days)
            random_date = start_date + datetime.timedelta(days=random_days)
            random_date_str = random_date.strftime("%y%m%d")
            image_path, image_name = process_image(random_date_str, w, h, crop, minW, minH)
            if ("default" not in image_name):
                break
            else:
                nbRetries -= 1

        if (image_path):
            return send_file(
                image_path,
                mimetype="image/jpeg",
                as_attachment=download,
                download_name=image_name
            )
        
        else:
            return jsonify({"error": "No image found with the specified parameters"}), 404
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/metadata/daily/", methods=["GET"])
def get_daily_metadata():
    try:
        todayUTC = get_current_utc_date()
        metadata = get_apod_metadata(todayUTC)
        
        if metadata:
            return jsonify(metadata)
        else:
            return jsonify({"error": "Metadata not found"}), 404
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/metadata/date/<date>/", methods=["GET"])
def get_metadata_by_date(date: str):
    try:
        if (not(date.isdigit()) or len(date) != 6):
            return jsonify({"error": "Invalid date format. Use YYMMDD."}), 400
        
        metadata = get_apod_metadata(date)
        
        if metadata:
            return jsonify(metadata)
        else:
            return jsonify({"error": "Metadata not found"}), 404
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500




if __name__ == "__main__":
    app.run(debug=True, port=PORT)
    print(f"Server is running on http://localhost:{PORT}")