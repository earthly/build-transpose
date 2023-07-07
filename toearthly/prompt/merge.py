from textwrap import dedent

import guidance

from toearthly.core import io, markdown

gpt4 = guidance.llms.OpenAI("gpt-4")

examples = [{
        "file1":   io.relative_read("data/merge/in1a.Earthfile"),
        "name1":    "workflow.yml",
        "file2":     io.relative_read("data/merge/in1b.Earthfile"),
        "name2":    "Dockerfile",
        "result":   io.relative_read("data/merge/out1.md"),
    }]

def prompt(file1: str, name1: str, file2: str, name2: str) -> str:
    program = guidance(
        dedent(
            """
        {{#system~}}
        I need your help to merge Earthfiles.
        If the files have different base `FROM`s, you'll have to include the `FROM` 
        statements in the targets where needed,
        You should also add any missing steps to the `all` target if any exists.
        If two steps do the same thing, but with different target names, they can 
        be combined.

        {{~/system}}
        {{~#each examples}}
        {{#user~}}
        First Earthfile:
        Project: {{this.name1}}
        ```Earthfile
        {{this.file1}}
        ```

        Second Earthfile:
        Project: {{this.name2}}
        ```Earthfile
        {{this.file2}}

        If the have different bases, we will have to include the `FROM` statements in 
        the targets where needed and we should also add any missing steps to the `all` 
        target. 

        Please discuss the way to merge these two files and then give the merged file 
        in backticks.
        {{~/user}}
        {{#assistant~}}
        {{this.result}}
        {{~/assistant}}
        {{~/each}}
        {{#user~}}
        First Earthfile:
        Project: {{name1}}
        ```Earthfile
        {{file1}}
        ```

        Second Earthfile:
        Project: {{name2}}
        ```Earthfile
        {{file2}}

        If the have different bases, we will have to include the `FROM` statements in 
        the targets where needed and we should also add any missing steps to the `all` 
        target. 

        Please discuss the way to merge these two files and then give the merged file 
        in backticks.
        ```
        {{~/user}}
        {{#assistant~}}
        {{gen "Earthfile" temperature=0 max_tokens=2000}}
        {{~/assistant}}
    """
        ),
        llm=gpt4,
    )
    out = io.run_llm_program(
        program,
        file1=file1,
        name1=name1,
        file2=file2,
        name2=name2,
        examples=examples,
    )
    io.write_debug("result.md", out["Earthfile"], "merge")
    results = markdown.extract_code_blocks(out["Earthfile"])
    if len(results) != 1:
        raise ValueError(f"1 Files exepected back. Instead got {len(results)}.")
    earthfile = results[0]
    io.write_debug("Earthfile", earthfile, "merge")
    return earthfile
