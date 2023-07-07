import argparse
import traceback
from textwrap import dedent
from typing import Tuple

import inquirer
import openai

from toearthly.core import boot, constants, io  # noqa: F401
from toearthly.prompt import bash_to_earthly, earthfile_correction, gha_to_bash, merge, dockerfile_to_earthfile

# Default directories
DEFAULT_INPUT_DIR = "/input/"
DEFAULT_EARTHFILE_PATH = "/input/Earthfile"
DEFAULT_DEBUG_DIR = "/input/.to_earthly/"


intro = """
ALPHA ALERT
This program attempts to generate an Earthfile using an Existing GitHub actions
workflow.
The generated Earthfile should be a good starting place. Additional manual changes
may be needed.
This program will send your GitHub actions workflow to OpenAPI.

This program assumes your project has the following attributes:
 * Primarily a single programming language
 * Not a deeply nested monorepo

Please send any stange results or issues to adam@earthly.dev along with a copy of the
.to_earthly folder and the Earthfile. I will use this for future improvements.

Many things need to be supported and will be ignored for now. These include:
* matrix builds
* WITH DOCKER and integration tests

I'll prioritize these based on feedback. So reach out on slack or via adam@earthly.dev
or via https://github.com/adamgordonbell/to-earthly
"""


def select_workflow(input_dir: str) -> Tuple[str, str]:
    ymls = io.find_workflows(input_dir)
    if len(ymls) != 1:
        questions = [
            inquirer.List(
                "option",
                message="Select a github workflow",
                choices=ymls,
            ),
        ]
        answers = inquirer.prompt(questions)
        path = answers["option"]
    else:
        path = ymls[0]
    with open(path, "r") as file:
        yml = file.read()
    return (path, yml)

def workflow_convert(workflow: str, file_structure : str)-> str:
    print("Running Stage 1 - GitHub Actions to Bash")
    runfile, dockerfile, buildfile = gha_to_bash.prompt(workflow, file_structure)

    print("Running Stage 2 - Bash to Earthly")
    earthfile = bash_to_earthly.prompt(
        file_structure, runfile, dockerfile, buildfile
    )

    print("Running Stage 3 - Earthfile Correction")
    earthfile = earthfile_correction.prompt(earthfile, workflow, file_structure)
    io.verify(earthfile)
    return earthfile

def dockerfile_convert(dockerfile_content: str, workflow_content : str)-> str:
    if not dockerfile_content:
        return ""
    print("Running Stage 1 - Dockerfile To Earthfile")
    earthfile = dockerfile_to_earthfile.prompt(dockerfile_content, workflow_content)
    io.verify(earthfile)
    return earthfile

def main(input_dir: str, earthfile_path: str) -> None:
    try:
        print(intro)
        workflow_path, workflow_content = select_workflow(input_dir)
        dockerfile_path, dockerfile_content = io.find_first_dockerfile(input_dir)
        print(
            dedent(
                f"""
              Input:
              Workflow:\t{workflow_path}
              Dockerfile:\t{dockerfile_path}
              Output:\t\t{earthfile_path}
              Debug files:\t{constants.DEBUG_DIR}
              """
            )
        )
        file_structure = io.print_directory(input_dir) 

        print("Starting Workflow Conversion...\n (This may take 10 minutes)")
        earthfile1 = workflow_convert(workflow_content, file_structure)
        
        print("\nStarting Dockerfile Conversion...")
        earthfile2 = dockerfile_convert(dockerfile_content, workflow_content) 

        print("Merging Earthfiles...\n")
        earthfile = merge.prompt(earthfile1, "workflow.yml", earthfile2, "Dockerfile")
        io.verify(earthfile)
        io.write(constants.EARTHLY_WARNING + earthfile, earthfile_path)


    except openai.error.InvalidRequestError as e:
        print("Error: We were unable to convert this workflow.")
        io.log(f"Error Type: openai.error.InvalidRequestError \n Error details: {e}")
    except (ValueError, TypeError, IndexError, KeyError) as e:
        print("Error: We were unable to convert this workflow.")
        trace = traceback.format_exc()
        io.log(f"Error Type: {type(e).__name__} \n Error details: {e}")
        io.log(f"Stack Trace: {trace}")


def get_arg_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input_dir", help="Base file location", default=DEFAULT_INPUT_DIR
    )
    parser.add_argument(
        "--earthfile", help="Earthfile path", default=DEFAULT_EARTHFILE_PATH
    )
    parser.add_argument(
        "--debug_dir", help="Debug directory location", default=DEFAULT_DEBUG_DIR
    )
    parser.add_argument(
        "--verify", help="Verify Earthfile", default=True, type=bool
    )
    return parser

if __name__ == "__main__":
    parser = get_arg_parser()
    args = parser.parse_args()

    constants.DEBUG_DIR = args.debug_dir

    main(args.input_dir, args.earthfile)
