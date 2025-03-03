from bs4 import BeautifulSoup
from io import BytesIO
from PIL import Image
import requests
import os


def create_folder(folder_name):
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)


def scrappe_nasa(codeDate, minW=0, minH=0):
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
                        print(f"Image {codeDate} has less than {minW}x{minH} pixels")
                        return None

                print(f"Saving image {codeDate}")
                image.save(img_path)
                return img_path
    return None


def resize_image(imagePath, outputPath, wRatio, hRatio, crop=True):
    with Image.open(imagePath) as img:
        width, height = img.size
        target_ratio = wRatio / hRatio

        if crop:
            img_ratio = width / height
            if img_ratio > target_ratio:
                new_height = height
                new_width = int(height * target_ratio)
                left = (width - new_width) // 2
                img_cropped = img.crop((left, 0, left + new_width, height))
            else:
                new_width = width
                new_height = int(width / target_ratio)
                top = (height - new_height) // 2
                img_cropped = img.crop((0, top, width, top + new_height))

            img_cropped.save(outputPath)
            return outputPath
        else:
            return None