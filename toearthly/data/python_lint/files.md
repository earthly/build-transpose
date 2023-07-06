`Files:`
```
.
├── requirements.txt
└── src/
    └── hello.py
```

`run.sh`:
```
#!/bin/bash

# Build the Docker image
docker build -t python-build -f build.Dockerfile .

# Run the build.sh script inside the Docker container
docker run --rm python-build ./build.sh
```

`build.Dockerfile`:
```
# Use a base image with Python 3.10
FROM python:3.10

# Set the working directory
WORKDIR /app

# Copy the requirements.txt file and the build.sh script into the image
COPY requirements.txt build.sh ./

# Install dependencies
RUN python -m pip install --upgrade pip && \
    pip install flake8 pytest && \
    if [ -f requirements.txt ]; then pip install -r requirements.txt; fi

# Set the build.sh script as executable
RUN chmod +x build.sh
```

`build.sh`:

```
#!/bin/bash

# Lint with flake8
flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics

# Test with pytest
pytest
```
