from bs4 import BeautifulSoup
from io import BytesIO
from PIL import Image
import requests
import os
import re




def create_folder(folder_name: str):
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)


def scrappe_nasa(codeDate: str, minW: int = 0, minH: int = 0) -> str:
    url = f"https://apod.nasa.gov/apod/ap{codeDate}.html"
    img_path = f"public/nasa_pictures/{codeDate}.jpg"
    create_folder("public/")
    create_folder("public/nasa_pictures/")

    if os.path.exists(img_path):
        return img_path

    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")
        image_link = soup.find("a", href=lambda href: href and href.startswith("image/"))
        
        if image_link:
            image_url = f"https://apod.nasa.gov/apod/{image_link['href']}"
            image_response = requests.get(image_url)
            
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


def get_apod_metadata(codeDate: str) -> dict:
    url = f"https://apod.nasa.gov/apod/ap{codeDate}.html"
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")
            
            title = None
            centers = soup.find_all("center")
            for center in centers:
                b_tag = center.find("b")
                if (b_tag and ("Image Credit" not in b_tag.get_text())):
                    title_text = b_tag.get_text().strip()
                    if (title_text and title_text != "Explanation:"):
                        title = title_text
                        break
            
            credit = None
            for center in centers:
                text = center.get_text()
                if ("Image Credit" in text):
                    lines = [line.strip() for line in text.split('\n') if line.strip()]
                    for i, line in enumerate(lines):
                        if ("Copyright:" in line and i + 1 < len(lines)):
                            credit = lines[i + 1]
                            break
                    break
            
            explanation = None
            paragraphs = soup.find_all("p")
            for p in paragraphs:
                explanation_text = p.get_text()
                if (p.find("b") and "Explanation:" in explanation_text):
                    explanation = explanation_text.split("Explanation:", 1)[1]
                    explanation = explanation.split("Tomorrow's picture:")[0]
                    explanation = re.sub(r'\s+', ' ', explanation).strip()
                    break

            formatted_date = f"20{codeDate[:2]}-{codeDate[2:4]}-{codeDate[4:6]}"
            
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