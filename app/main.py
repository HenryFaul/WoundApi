from typing import Union
from fastapi import FastAPI, Request, UploadFile, HTTPException, status
from fastapi.staticfiles import StaticFiles
from PIL import Image
from fastapi.responses import FileResponse
from fastapi.responses import JSONResponse
import io
import os
import time
from pathlib import Path
import sys

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

BASE_DIR = Path(__file__).resolve(strict=True).parent
static_directory = f"{BASE_DIR}/static"
index_directory = f"{BASE_DIR}/static/index.html"
predict_directory = f"{BASE_DIR}"
RESIZED_DIRECTORY= f"{BASE_DIR}/static/picture_uploads/resized_uploads/"
UPLOAD_DIRECTORY= f"{BASE_DIR}/static/picture_uploads/raw_uploads/"

# Append directory to sys.path
sys.path.append(predict_directory)

# Now you can import modules from the directory
from predict2 import make_prediction

app = FastAPI()


app.mount(static_directory, StaticFiles(directory=static_directory), name="static")

@app.get("/")
async def home():
    return FileResponse(index_directory)

@app.post('/upload')
async def upload(file: UploadFile, request: Request):
    try:
        # Check if file extension is allowed
        file_extension = file.filename.split('.')[-1]
        if file_extension.lower() not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only .png and .jpg files are allowed."
            )

        contents = await file.read()
        image = Image.open(io.BytesIO(contents))

        # Convert to PNG if file is JPG
        if file_extension.lower() == 'jpg' or file_extension.lower() == 'jpeg':
            png_image = image.convert('RGB')
            file.filename = file.filename.split('.')[0] + '.png'  # Change filename extension
            contents = io.BytesIO()
            png_image.save(contents, format='PNG')
            contents.seek(0)

        resized_image = image.resize((224, 224))  # Specify the desired width and height

        timestr = time.strftime("%Y%m%d-%H%M%S")

        # Path
        path = os.path.join(RESIZED_DIRECTORY, timestr)
        os.mkdir(path)
        resized_file_path = os.path.join(path, file.filename)
        # Save the resized image
        resized_image.save(resized_file_path)
        base_url = str(request.base_url)
        #return path
        prediction_response = make_prediction(RESIZED_DIRECTORY+timestr, RESIZED_DIRECTORY,resized_file_path)
        # Return prediction response as JSON
        return JSONResponse(content=prediction_response)

    except Exception as e:
        raise HTTPException(
           status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
           detail='There was an error uploading the file: ' + str(e),
        )
    finally:
        await file.close()
