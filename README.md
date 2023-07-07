<!-- markdownlint-disable -->
# Build Transpose

## Run from Pre-Built Image

```
docker run --rm -it --name my_container -v $(pwd):/input agbell/to-earthly
```

## Run using your own OpenAI key

Give OpenAI KEY:
```
echo "OPENAI_API_KEY=bla" > .env
```

Build docker image:
```
>earthly +docker
```
Run in a repo with a GHA workflow and get an Earthfile
```
docker run --rm -it --name my_container -v $(pwd):/input to-earthly
```

# ToDo for Docker steps
- merge problems
- ship it
