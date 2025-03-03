from bs4 import BeautifulSoup
from io import BytesIO
from PIL import Image
import requests
import os




def create_folder(folder_name: str):
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)


def scrappe_nasa(codeDate: str, minW: int = 0, minH: int = 0):
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


def resize_image(imagePath: str, outputPath: str, wRatio: int, hRatio: int, crop: bool = True):
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