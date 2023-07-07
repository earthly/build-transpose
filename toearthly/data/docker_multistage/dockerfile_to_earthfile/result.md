Sure, here is the Earthfile:

```Earthfile
VERSION 0.7
WORKDIR /app
FROM python:3.9

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

analyze:
  FROM +build
  RUN pylint $(find src/ -name '*.py') 
  RUN pytest

all:
  BUILD +runner
  BUILD +analyze
```
