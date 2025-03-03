# NASA Daily Picture API

A Python web API to fetch and resize the Astronomy Picture of the Day from [NASA's APOD (Astronomy Picture of the Day)](https://apod.nasa.gov/apod/), with customizable resizing options.

The API is available at: [https://nasa.gatienh.fr/](https://nasa.gatienh.fr/).

## **Endpoints**

### **1. [GET] `/`**
-  Basic health check for the API.

### **2. [GET] `/daily/`**
- Fetches the daily NASA image (updated every day around midnight UTC-5).
- **Example**:
  ```
  GET http://127.0.0.1:3400/daily/
  ```

### **3. [GET] `/date/{date}/`**
- Fetches and resizes the NASA image for a specific date.
- **Path Parameters**:
  - `date` (str, required): The date in `YYMMDD` format.
- **Parameters**:
- **Example**:
  ```
  GET http://127.0.0.1:3400/date/241115/?w=9&h=19
  ```

### **4. [GET] `/random/`**
- **Description**: Fetches and resizes a random NASA image.
- **Query Parameters**:
  - `minW` (int, optional): Minimum width pixel.
  - `minH` (int, optional): Minimum height pixel.
- **Example**:
  ```
  GET http://127.0.0.1:3400/random/?minW=500&minH=2000
  ```

### **Common Parameters**
These query parameters are available in all endpoints:

- `w` (int, optional): Width ratio (e.g., `16` for a `16:9` ratio).
- `h` (int, optional): Height ratio (e.g., `9` for a `16:9` ratio).
- `crop` (bool, optional, default: `true`):  
  - If `true`, the image is cropped to fit the specified aspect ratio.  
  - If `false`, the image is resized while maintaining proportions.
- `download` (bool, optional): If `true`, the image will be downloaded automatically.
- **Example**:
  ```
  GET http://127.0.0.1:3400/random/?minW=2400&minH=800&w=16&h=9&crop=false&download=true
  ```

## **Installation**

### Prerequisites

- Python 3.8 or higher.
- `pip` to install dependencies.

### Steps

1. Clone the repository.

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Add a `default.jpg` image at the root of the project. This image will be used when the API does not have an image to return.

4. Run the API:
   ```bash
   python app.py
   ```

5. The API will be available at: [http://127.0.0.1:3400](http://127.0.0.1:3400).