VERSION 0.7
FROM python:3.9
WORKDIR /app

deps:
  COPY requirements.txt .
  RUN pip install -r requirements.txt
  COPY src/ src/

build:
  FROM +deps
  RUN pip install pylint pytest  

runner:
  FROM +deps
  CMD ["python", "src/run.py"]
  SAVE IMAGE --push user/app:latest

all:
  BUILD +runner
