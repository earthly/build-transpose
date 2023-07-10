<!-- markdownlint-disable -->
# Build Transpose

## What?

Transpose your build script from one build system to another using LLMs. Specifcally: **Convert a GitHubActions workflow into an Earthfile using GPT-4.**

## Run from Pre-Built Image

The easiest way to use `build-transpose` to generate an Earthfile from a GitHub Actions workflow is to use the pre-built docker image.

Just run the following command in the root of your repository and follow the prompts.

```
docker run --rm -it --name my_container -v "$(pwd)":/input agbell/build-transpose
```

## Run using your own OpenAI key

If you'd like to run the application from source, you can provide your own `OPENAI_API_KEY` as follows:

Give an OpenAI KEY:
```
echo "OPENAI_API_KEY=bla" > .env
```

Build docker image:
```
>earthly +docker
```

Run in a repo with a GHA workflow and get an Earthfile
```
docker run --rm -it --name my_container -v "$(pwd)":/input to-earthly
```

## Run without Container

To run without a container, clone the repo, add it to your python path and run like this:

```
python {{path to repo}}/toearthly/scripts/run.py --input_dir "$(pwd)" --debug_dir "$(pwd)/.to_earthly/" --earthfile "$(pwd)"/Earthfile
```

Adjust paths and input directories as needed.
