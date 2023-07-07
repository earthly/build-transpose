FROM python:3.9 AS base

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY src/ src/

FROM base AS runner

CMD ["python", "src/run.py"]

FROM base AS build

RUN pip install pylint pytest

FROM build AS analyze

RUN pylint $(find src/ -type f -name '*.py') && \
    pytest
