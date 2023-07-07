import multiprocessing
import subprocess
import os
import constants
import time
import contextlib
import glob
import os
import subprocess
import time
from collections import defaultdict
from typing import List, Tuple
from toearthly.core import io

import openai
from joblib import Memory

from toearthly.core import constants

def worker():
    debug_earthfile_path = os.path.join(constants.DEBUG_DIR, "Earthfile")
    result = subprocess.run(
        ["earthly", "debug", "ast", debug_earthfile_path],
        capture_output=True,
        text=True,
    )
    return result.returncode, result.stderr

# earthly debug ast sometimes segfaults, taking this process out as well.
# So we use multi-processing.
def verify(earthfile: str):
    debug_earthfile_path = os.path.join(constants.DEBUG_DIR, "Earthfile")
    io.write(earthfile, debug_earthfile_path)
    p = multiprocessing.Process(target=worker)
    p.start()

    # Wait for up to 10 seconds for the process to finish
    p.join(10)

    # If the process did not finish in time
    if p.is_alive():
        p.terminate()
        p.join()
        raise ValueError("The 'earthly' command took too long to execute and was terminated")

    # Check return code and raise ValueError if non-zero
    returncode, stderr = p.exitcode
    if returncode != 0:
        raise ValueError(f"Verification failed with errors:\n{stderr}")
