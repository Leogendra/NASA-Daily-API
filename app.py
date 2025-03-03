from flask import Flask, jsonify, send_file, request
from nasa_scraper import scrappe_nasa, resize_image
import datetime, random, os

app = Flask(__name__)
PORT = 3400
BASE_IMAGE_DIR = "public"
BASE_URL = f"http://localhost:{PORT}"




def process_image(date: str, w: int, h: int):
    try:
        image_path = scrappe_nasa(date)
        if not(image_path):
            return None

        if ((w > 0) and (h > 0)):
            output_folder = f"{BASE_IMAGE_DIR}/{w}x{h}"
            resized_path = f"{output_folder}/{date}.jpg"
            os.makedirs(output_folder, exist_ok=True)
            resize_image(image_path, resized_path, w, h, crop=True)
            return resized_path, f"{date}_{w}x{h}.jpg"
        else:
            return image_path, f"{date}.jpg"
    except Exception as e:
        return None


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
        download = request.args.get("download", "false").lower() in ["true", "1", "yes"]
        todayUTC = (datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-5)))).strftime("%y%m%d")
        image_path, image_name = process_image(todayUTC, w, h)
        if image_path:
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
def get_image_by_date(date):
    try:
        w = int(request.args.get("w", 0))
        h = int(request.args.get("h", 0))
        download = request.args.get("download", "false").lower() in ["true", "1", "yes"]
        if not date.isdigit() or len(date) != 6:
            return jsonify({"error": "Invalid date format. Use YYMMDD."}), 400
        image_path, image_name = process_image(date, w, h)
        if image_path:
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
        download = request.args.get("download", "false").lower() in ["true", "1", "yes"]
        start_date = datetime.datetime(1996, 1, 1)
        end_date = datetime.datetime.now()
        random_days = random.randint(0, (end_date - start_date).days)
        random_date = start_date + datetime.timedelta(days=random_days)
        random_date_str = random_date.strftime("%y%m%d")
        image_path, image_name = process_image(random_date_str, w, h)
        if image_path:
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




if __name__ == "__main__":
    app.run(debug=True, port=PORT)
    print(f"Server is running on http://localhost:{PORT}")