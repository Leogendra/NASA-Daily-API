# NASA Daily Picture API

A Python web API to fetch and resize the Astronomy Picture of the Day from [NASA APOD (Astronomy Picture of the Day)](https://apod.nasa.gov/apod/), with customizable cropping options.

The API is available at: [https://nasa.gatienh.fr/](https://nasa.gatienh.fr/).

## **Endpoints**

### **1. [GET] `/`**
- **Description**: Basic health check for the API.

### **2. [GET] `/daily/`**
- **Description**: Fetches and resizes the daily NASA image.
- **Query Parameters**:
  - `w` (int, optional): Width ratio.
  - `h` (int, optional): Height ratio.
  - `download` (bool, optional): If `true`, the image will be downloaded automatically.
- **Example**:
  ```
  GET http://127.0.0.1:8000/daily-nasa/?w=9&h=19
  ```
- **Response**:
- Static image with the specified width and height.

### **3. [GET] `/date/{date}/`**
- **Description**: Fetches and resizes the NASA image for a specific date.
- **Path Parameters**:
  - `date` (str, required): The date in `YYMMDD` format.
- **Query Parameters**:
  - `w` (int, optional): Width ratio.
  - `h` (int, optional): Height ratio.
- **Example**:
  ```
  GET http://127.0.0.1:8000/date/241115/?w=9&h=19
  ```
- **Response**:
- Static image with the specified width and height.

### **4. [GET] `/random/`**
- **Description**: Fetches and resizes a random NASA image.
- **Query Parameters**:
  - `w` (int, optional): Width ratio.
  - `h` (int, optional): Height ratio.
- **Example**:
  ```
  GET http://127.0.0.1:8000/random/?w=9&h=19
  ```
- **Response**:
- Static image with the specified width and height.


## **Installation**

### Prerequisites

- Python 3.8 or higher
- `pip` to install dependencies

### Steps

1. Clone the repository:

2. Install the required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Run the API using **uvicorn**:

   ```bash
   uvicorn app:app --reload
   ```

4. The API will be available at: [http://127.0.0.1:8000](http://127.0.0.1:8000).