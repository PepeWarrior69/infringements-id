#Deriving the latest base image
FROM python:latest

WORKDIR /infringements

COPY . .

RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y

RUN pip install -r requirements.txt

CMD [ "python", "app.py"]
CMD [ "python", "app.py"]
