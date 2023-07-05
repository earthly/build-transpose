To approach this problem, we will follow these steps:

1. Analyze the given files and understand the build process.
2. Create an Earthfile with the necessary targets.
3. Port the steps from the Dockerfile and bash scripts to the Earthfile targets.

Now, let's go through the files step by step and discuss how the steps should be ported to Earthly.

`Files`:
The file structure consists of a `requirements.txt` file and a `src` directory containing a `hello.py` file. We will need to copy these files into the Earthfile at the appropriate stages.

`run.sh`:
This script builds the Docker image and runs the `build.sh` script inside the Docker container. In Earthly, we don't need to wrap Docker commands in a bash script. Instead, we will create targets in the Earthfile to handle the build process.

`build.Dockerfile`:
This Dockerfile sets up the base image, working directory, copies files, installs dependencies, and sets the `build.sh` script as executable. We will create a `base` target in the Earthfile to handle these steps.

`build.sh`:
This script runs linting with flake8 and testing with pytest. We will create separate targets in the Earthfile for linting and testing.

Here's how the Earthfile targets should look like:

1. Header
   - The header of the Eartfile starts with a version declaration. `VERSION 0.7`
   - Then pick the base image. Python 3.10 in this case.
   - Set the working directory to `/app`.
 
2. `deps` target:
   - Copy the `requirements.txt` file and the `src` directory.
   - Install dependencies using pip and the `requirements.txt` file.
   - Copy in the `src` python files

2. `lint` target:
   - Use the `deps` target as a starting point.
   - Run flake8 linting commands.

3. `test` target:
   - Use the `deps` target as a starting point.
   - Run pytest for testing.

4. `all` target:
Earthfiles often have an `all` target that is run in CI or by a developer and covers all actions.
   - Build `test` and `lint` targets with BUILD `+target` syntax
