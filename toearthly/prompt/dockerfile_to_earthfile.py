
from textwrap import dedent

import guidance

from toearthly.core import io, markdown

gpt4 = guidance.llms.OpenAI("gpt-4")

earthly_basics = io.relative_read("data/earthly_docs/basics.md")
earthly_reference = io.relative_read("data/earthly_docs/summary.md")
earthly_tips = io.relative_read("data/earthly_docs/tips.md")

docker1 = io.relative_read("data/docker_simple2/Dockerfile")
workflow1 = io.relative_read("data/docker_simple2/workflow.yml")
plan1 = io.relative_read("data/docker_simple2/dockerfile_to_earthfile/plan.md")
result1 = io.relative_read("data/docker_simple2/dockerfile_to_earthfile/result.md")

def prompt(docker: str, build: str) -> str:
    program = guidance(
        dedent(
            """
    {{#system~}}
    You are creating an Earthfile from a Dockerfile and a GitHub Actions workflow. I'll 
    share Earthly documentation with you and then describe the conversion process.

    {{earthly_basics}}
    {{earthly_reference}}
    {{earthly_tips}}
    The tutorial is over. I will now describe the task.

    You are creating an Earthfile from the following inputs.
    * A Dockerfile: each stage in the Dockerfile will become a target in the Earthfile.
    * A GitHub Action workflow: This may not be needed. Only steps in workflow which 
      describe docker actions like tagging or pushing or running docker with certain
      arguments may be relevant. The rest should be ignored.

    {{~/system}}
     {{#user~}}
    Github Actions Workflow:
    ```
    {{workflow1}}
    ```

    Dockerfile:
    ```Dockerfile
    {{docker1}}
    ```

    Task:
    Do not produce the Earthfile. Instead, describe how you would approach this
    problem. Then go through the files, step by step, and discuss how the steps should
    be ported to an Earthfile.

    Let me go step by step through the dockerfile and convert it to a Earthfile.
    {{~/user}}
    {{#assistant~}}
    {{plan1}}
    {{~/assistant}}
    {{#user~}}
    Ok, produce the Earthfile in backticks.
    {{~/user}}
    {{#assistant~}}
    {{result1}}
    {{~/assistant}}
    {{#user~}}
    Github Actions Workflow:
    ```
    {{build}}
    ```

    Dockerfile:
    ```Dockerfile
    {{docker}}
    ```

    Task:
    Do not produce the Earthfile. Instead, describe how you would approach this
    problem. Then go through the files, step by step, and discuss how the steps should
    be ported to an Earthfile.

    Let me go step by step through the dockerfile and convert it to a Earthfile.
    {{~/user}}
    {{#assistant~}}
    {{gen "discuss" temperature=0 max_tokens=1000}}
    {{~/assistant}}
    {{#user~}}
    Ok, produce the Earthfile in backticks.
    {{~/user}}
    {{#assistant~}}
    {{gen "Earthfile" temperature=0 max_tokens=500}}
    {{~/assistant}}
    """
        ),
        llm=gpt4,
    )
    out = io.run_llm_program(
        program,
        earthly_basics=earthly_basics,
        earthly_reference=earthly_reference,
        earthly_tips=earthly_tips,
        docker1=docker1,
        workflow1=workflow1,
        plan1=plan1,
        result1=result1,
        docker=docker,
        build=build,
    )
    io.write_debug("plan.md", out["discuss"], "dockerfile_to_earthfile")
    io.write_debug("result.md", out["Earthfile"], "dockerfile_to_earthfile")
    results = markdown.extract_code_blocks(out["Earthfile"])
    if len(results) != 1:
        raise ValueError(f"1 Files exepected back. Instead got {len(results)}.")
    earthfile = results[0]
    io.write_debug("Earthfile", earthfile, "dockerfile_to_earthfile")
    return earthfile
