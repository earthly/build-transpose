`run.sh`:

```bash
#!/bin/bash

# Build the Docker image
docker build -t build -f build.Dockerfile .

# Run the build.sh script inside the Docker container
docker run --rm build ./build.sh

# Build the Docker image
IMAGE_NAME="my-image-name"
TAG=$(date +%s)

# Build the application Docker image
docker build . --file Dockerfile --tag $IMAGE_NAME:$TAG
```

`build.Dockerfile`:
```
# Use a alpine base image
FROM alpien:latest

# Set the working directory
WORKDIR /app

# Copy the build.sh script into the image
COPY build.sh ./
```

`build.sh`:
```bash
#!/bin/bash

# Place to insert customized build steps
echo "Add build steps here!"
```
