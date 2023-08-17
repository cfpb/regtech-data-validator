import os
import sys

CURR_DIR = os.path.dirname(os.path.abspath(__file__))  # noqa: E402
PARENT_DIR = os.path.dirname(CURR_DIR)  # noqa: E402
ROOT_DIR = os.path.dirname(PARENT_DIR)  # noqa: E402
sys.path.append(CURR_DIR)  # noqa: E402
sys.path.append(PARENT_DIR)  # noqa: E402
sys.path.append(ROOT_DIR)  # noqa: E402
sys.path.append(os.path.join(ROOT_DIR, "validator"))
