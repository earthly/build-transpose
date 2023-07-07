import os

import dotenv
from toearthly.core import io

dotenv.load_dotenv()
if os.environ.get("OPENAI_API_KEY") is None:
    raise EnvironmentError("OPENAI_API_KEY ENV is not set.")
