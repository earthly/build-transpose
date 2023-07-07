from textwrap import dedent

import guidance

from toearthly.core import io, markdown

gpt4 = guidance.llms.OpenAI("gpt-4")

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
        {{#user~}}
        First Earthfile:
        Project: {name1}
        ```Earthfile
        {{file1}}
        ```

        Second Earthfile:
        Project: {name2}
        ```Earthfile
        {{file2}}

        In Earthfiles, each target is like a step in the overall build process.
        The important considerations for merging these two files are as follows:
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
    )
    io.write_debug("result.md", out["earthfile"], "merge")
    results = markdown.extract_code_blocks(out["Earthfile"])
    if len(results) != 1:
        raise ValueError(f"1 Files exepected back. Instead got {len(results)}.")
    earthfile = results[0]
    io.write_debug("Earthfile", earthfile, "merge")
    return earthfile
