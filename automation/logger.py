import logging
import os
import sys

cwd = os.getcwd()
sys.path.append(cwd)
sys.path.append(cwd + "/automation_svc_ui/")

# configure logging with filename, function name and line numbers
logging.basicConfig(
    level="INFO",
    datefmt="%I:%M:%S %p %Z",
    format="%(levelname)s [%(asctime)s - %(filename)s:%(lineno)s::%(funcName)s]\n%(message)s",
)

log = logging.getLogger(__name__)
