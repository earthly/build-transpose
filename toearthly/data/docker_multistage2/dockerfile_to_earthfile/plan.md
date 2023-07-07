The Dockerfile is a multi-stage build with two stages: base, and another. The base stage starts from an alpine and creates a file. The `base` target is a reserved target in Earthly, which we can't use. So we will call it `build`.

```Earthfile
VERSION 0.7
FROM alpine:3.15

build:
    RUN echo "word" > ./a-file
    SAVE ARTIFACT ./a-f
```

The `another` stage follows, so in the Earthfile it can follow from `build`. The `COPY` must change from `COPY --from=build ./a-file ./` to the Earthfile equivalent `COPY +build/a-file .`.

```Earthfile
another:
    FROM busybox
    COPY +build/a-file .
```

Also, because of the `COPY` we must `SAVE ARTIFACT` in `build` above, updating it to:

```Earthfile
build:
    RUN echo "word" > ./a-file
    SAVE ARTIFACT ./a-file
```

Next, let's look at the relevant GitHub Actions workflow sections. This is the main relevant part:

```yaml
    - uses: docker/build-push-action@v4
      with:
        tags: something
```

We can alter our Earthfile another stage to accomplish this.

```Earthfile
another:
    FROM busybox
    COPY +build/a-file .
    SAVE IMAGE something
```
