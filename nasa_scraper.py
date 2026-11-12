from bs4 import BeautifulSoup, Tag
from io import BytesIO
from PIL import Image
import requests
import datetime
import os
import re

APOD_API_URL = "https://science.nasa.gov/wp-json/wp/v2/image-article"
APOD_CATEGORY_ID = 22766
ASSETS_URL = "https://assets.science.nasa.gov/"
REQUEST_TIMEOUT = 15




def create_folder(folder_name: str):
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)


def fetch_apod_article(codeDate: str) -> BeautifulSoup:
    day = datetime.datetime.strptime(codeDate, "%y%m%d")
    params = {
        "categories": APOD_CATEGORY_ID,
        "after": (day - datetime.timedelta(seconds=1)).isoformat(),
        "before": (day + datetime.timedelta(days=1)).isoformat(),
        "_fields": "content",
    }
    response = requests.get(APOD_API_URL, params=params, timeout=REQUEST_TIMEOUT)
    if (response.status_code != 200):
        return None

    posts = response.json()
    if not(posts):
        return None
    return BeautifulSoup(posts[0]["content"]["rendered"], "html.parser")


def get_image_url(soup: BeautifulSoup) -> str:
    media = soup.select_one(".media-detail-hero__media")
    if not(media):
        return None

    # The link around the picture points to the full resolution asset
    image_link = media.find("a", href=lambda href: href and href.startswith(ASSETS_URL))
    if image_link:
        return image_link["href"]

    # Videos and embeds have no <img>
    image = media.find("img")
    if (image and image.get("src")):
        return image["src"].split("?")[0]
    return None


def scrappe_nasa(codeDate: str, minW: int = 0, minH: int = 0) -> str:
    img_path = f"public/nasa_pictures/{codeDate}.jpg"
    create_folder("public/")
    create_folder("public/nasa_pictures/")

    if os.path.exists(img_path):
        return img_path

    soup = fetch_apod_article(codeDate)
    if soup:
        image_url = get_image_url(soup)

        if image_url:
            image_response = requests.get(image_url, timeout=REQUEST_TIMEOUT)

            if image_response.status_code == 200:
                if (minW and minH):
                    image = Image.open(BytesIO(image_response.content))
                    width, height = image.size

                    # Verify if the image has the minimum width and height
                    if ((width < minW) or (height < minH)):
                        return None

                with open(img_path, "wb") as file:
                    file.write(image_response.content)
                return img_path
    return None


def clean_text(text: str) -> str:
    return re.sub(r'\s+', ' ', text).strip()


def get_apod_metadata(codeDate: str) -> dict:
    try:
        soup = fetch_apod_article(codeDate)
        if soup:
            title = None
            title_tag = soup.select_one(".hds-media-detail-hero h1")
            if title_tag:
                title = clean_text(title_tag.get_text())

            # Meta table rows: "Date", "Credit" or "Credit & Copyright", "Authors & editors:", ...
            credit = None
            for row in soup.select(".media-detail-hero__meta-row"):
                header = row.find("th")
                if (header and header.get_text().strip().startswith("Credit")):
                    # Keep the first line only, next ones hold extra credits ("Text: ...")
                    first_line = []
                    for node in row.find("td").children:
                        if (node.name == "br"):
                            break
                        first_line.append(node.get_text() if isinstance(node, Tag) else str(node))
                    credit_text = clean_text("".join(first_line))
                    credit = re.sub(r'^(Image )?Credit( & Copyright)?:\s*', '', credit_text)
                    break

            explanation = None
            description = soup.select_one(".media-detail-hero__description")
            if description:
                explanation_text = re.split(r"Tomorrow['’]s picture:", description.get_text())[0]
                explanation = clean_text(explanation_text).removeprefix("Explanation:").strip()

            formatted_date = datetime.datetime.strptime(codeDate, "%y%m%d").strftime("%Y-%m-%d")

            return {
                "date": formatted_date,
                "title": title,
                "credit": credit,
                "explanation": explanation,
            }
        else:
            return None
    except Exception as e:
        print(f"Error scraping metadata: {str(e)}")
        return None


def resize_image(imagePath: str, outputPath: str, wRatio: int, hRatio: int, crop: bool = True) -> str:
    with Image.open(imagePath) as img:
        width, height = img.size
        target_ratio = wRatio / hRatio
        img_ratio = width / height

        if crop:
            if (img_ratio > target_ratio):
                new_height = height
                new_width = int(height * target_ratio)
                left = (width - new_width) // 2
                img_resized = img.crop((left, 0, left + new_width, height))
            else:
                new_width = width
                new_height = int(width / target_ratio)
                top = (height - new_height) // 2
                img_resized = img.crop((0, top, width, top + new_height))

        else:
            if (img_ratio > target_ratio):
                new_width = width
                new_height = int(width / target_ratio)
            else:
                new_height = height
                new_width = int(height * target_ratio)

            img_resized = img.resize((new_width, new_height), Image.LANCZOS)
        
        img_resized.save(outputPath)
        return outputPath