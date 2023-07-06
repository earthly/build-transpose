import contextlib
from textwrap import dedent

import guidance

from toearthly.core import constants, io, markdown

gpt4 = guidance.llms.OpenAI("gpt-4")

def call_identify(identify, *args, **kwargs):
    with open(constants.DEBUG_DIR + "log.txt", "a") as f, contextlib.redirect_stdout(
        f
    ), contextlib.redirect_stderr(f):
        return identify(*args, **kwargs)

earthly_basics = io.relative_read("data/earthly_docs/basics.md")
earthly_reference = io.relative_read("data/earthly_docs/summary.md")
earthly_tips = io.relative_read("data/earthly_docs/tips.md")

input1 = io.relative_read("data/python_lint/files.md")
cot1 = io.relative_read("data/python_lint/EarthfilePlan.md")
result1 = io.relative_read("data/python_lint/Earthfile")

def prompt(files: str, run: str, docker: str, build: str) -> str:
    identify = guidance(
        dedent(
            """
    {{#system~}}
    You are creating an Earthfile from several bash and dockerfiles. I'll share Earthly
    documentation with you and then describe the conversion process.

    {{earthly_basics}}
    The tutorial is over. I will now describe the task.

    You are creating an Earthfile from the following inputs.
    *  `Files`: A Description of the file structure of the project. Use the file
    structure to determine what files need to be copied in at each stage of the docker
    multi-stage build.
    * `run.sh`: A bash file that wraps docker. It will call docker build and afterward
    run steps like docker push.
    * `build.Dockerfile`: A dockerfile with the correct base image to support the build
    steps. This should become the `base` and possibly the `deps` steps in the docker
    file.
    * `build.sh` A bash file that runs the build steps. These steps should become
    targets in the Earthfile.
    {{~/system}}
    {{#user~}}
    {input1}
    {{~/user}}
    {{#assistant~}}
    {{cot1}}
    {{~/assistant}}
    {{#user~}}
    Ok, produce the files. Files that are needed need to be copied in.
    {{~/user}}
    {{#assistant~}}
    {{result1}}
    {{~/assistant}}
    {{#user~}}
    `Files:`
    ```
    {{files}}
    ```

    `run.sh`:
    ```
    {{run}}
    ```

    build.Dockerfile
    ```
    {{docker}}
    ```

    `build.sh`:
    ```
    {{build}}
    ```

    An Earthfile is a better way to represent this build process because it combines the
    concepts of running bash commands to build something with the ideas of
    containerisation made popular by Docker and dockerfile.

    Task:
    Do not produce the Earthfile. Instead,  describe how you would approach this
    problem. Then go through the files, step by step, and discuss how the steps should
    be ported to Earthly.
    {{~/user}}
    {{#assistant~}}
    {{gen "discuss" temperature=0 max_tokens=2000}}
    {{~/assistant}}
    {{#user~}}
    Ok, produce the files. Files that are needed need to be copied in.
    {{~/user}}
    {{#assistant~}}
    {{gen "Earthfile" temperature=0 max_tokens=2000}}
    {{~/assistant}}
    """
        ),
        llm=gpt4,
    )
    out = call_identify(
        identify,
        earthly_basics=earthly_basics,
        input1=input1,
        cot1=cot1,
        result1=result1,
        files=files,
        run=run,
        docker=docker,
        build=build,
    )
    io.write_debug("EarthfilePlan.md", out["discuss"])
    results = markdown.extract_code_blocks(out["Earthfile"])
    if len(results) != 1:
        raise ValueError(f"1 Files exepected back. Instead got {len(results)}.")
    earthfile = results[0]
    io.write_debug("Earthfile.1", earthfile)
    return earthfile


def prompt3(earthfile: str, gha: str, files: str) -> str:
    identify = guidance(
        dedent(
            """
        {{#system~}}
        Use the below documentation on Earthfiles to do a code conversion task.
        <<Article>>
        {{earthly_basics}}
        {{earthly_tips}}
        <<Article>>

        The tutorial is over. I will now describe the task.

        Task:
        You are given an Earthfile that has incorrect syntax or doesn't conform to best
        practices.
        The Earthfile is based on a GitHub Actions workflow. this is also given and
        should match it as closely as possible.
        The file structure of the solution is also included because in an Earthfile
        files must be explicitly copied into context.
        The mistakes may be using Dockerfile syntax, or not SAVE ARTIFACT for things it
        COPY or there just may be a better way to structure things.
        Possibly files are copied in that do not exist or a target named `base` is used
        even though that is reservered.

        Do not produce the file yet. Instead, describe how you would approach this
        problem. Then go through the Earthfile section by section and discuss any
        changes that need to be made.

        {{~/system}}
        {{#user~}}
        Files:
        ```
        {{files}}
        ```

        Git Hub Actions:
        ```
        {{gha}}
        ```

        Earthfile:
        ```
        {{earthfile}}
        ```
        {{~/user}}
        {{#assistant~}}
        {{gen "discuss" temperature=0 max_tokens=2000}}
        {{~/assistant}}
        {{#user~}}
        Ok, produce the Earthfile in backticks.
        {{~/user}}
        {{#assistant~}}
        {{gen "Earthfile" temperature=0 max_tokens=2000}}
        {{~/assistant}}

    """
        ),
        llm=gpt4,
    )
    out = call_identify(
        identify,
        earthly_basics=earthly_basics,
        earthly_tips=earthly_tips,
        input1=input1,
        files=files,
        gha=gha,
        earthfile=earthfile,
    )
    io.write_debug("EarthfileFixPlan.md", out["discuss"])
    results = markdown.extract_code_blocks(out["Earthfile"])
    if len(results) != 1:
        raise ValueError(f"1 Files exepected back. Instead got {len(results)}.")
    return results[0]
