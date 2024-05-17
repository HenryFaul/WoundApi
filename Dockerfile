
 FROM python:3.9
#FROM tiangolo/uvicorn-gunicorn-fastapi:python3.9

# set the working directory
WORKDIR /code

RUN apt-get update && apt-get install -y libhdf5-dev

# install dependencies
COPY ./requirements.txt ./
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# copy the src to the folder
COPY ./src ./src

# start the server
CMD ["fastapi", "run", "src/main.py", "--port", "80"]
#CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "80"]
