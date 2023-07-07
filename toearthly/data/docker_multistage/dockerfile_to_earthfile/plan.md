The Dockerfile is a multi-stage build with four stages: base, build, runner, and analyze. 

The base stage starts from a python image, sets the working directory, and some files into the container. base is a reserved target in Earthly, which we can't use. So we can split this stage in two steps, the implied base target and a target we can call `deps` because its setting up dependencies.


```Earthfile
VERSION 0.7
WORKDIR /app
FROM python:3.9

deps:
  COPY requirements.txt .
  RUN pip install -r requirements.txt
  COPY src/ src/
```
The build stage follows from base, so in the Earthfile it can follow from `deps`.

```Earthfile
build:
  FROM +deps
  RUN pip install pylint pytest  
```

The runner stage starts from base, and creates a runnable image. An Earthfile would look like this:

```
runner:
  FROM +deps
  CMD ["python", "src/run.py"]
```

The analyze stage starts from the build stage and runs pyline and pytest. In an Earthfile that would look like this:

```Earthfile
analyze:
  FROM +build
  RUN pylint $(find src/ -name '*.py') && \
    pytest
```

The two commands on one line, would read better in an Earthfile if split into two seperate lines. So we change like this.

```Earthfile
analyze:
  FROM +build
  RUN pylint $(find src/ -name '*.py') 
  RUN pytest
```

We can add an `all` step to match the behaviour of building all stages, found in docker buildx. Since only `runner` and `analyze` are not called by other stages, we can put them in the all step like so:

```Earthfile
all:
  BUILD +runner
  BUILD +analyze
```

Next, let's look at the relevant GitHub Actions workflow sections. This is the main relevant part:

```yaml
    - uses: docker/build-push-action@v4
      with:
        push: true
        target: runner
        tags: user/app:latest
```

This `docker/build-push-action` tags the target `runner` as `user/app:latest` and pushes it. We can alter our Earthfile runner stage to accomplish this.

```Earthfile
runner:
  FROM +deps
  CMD ["python", "src/run.py"]
  SAVE IMAGE --push user/app:latest
```

In summary, the Dockerfile and GitHub Actions workflow can be converted to an Earthfile. The Earthfile defines the steps to setup dependencies, run tests and build the Docker image. Running `earthly --push +runner` builds and tags the image.
