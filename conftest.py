# from datetime import datetime
# import logging
# import sys
# import pytest
# from reportportal_client import RPLogger, RPLogHandler


# @pytest.fixture(scope="session", autouse=True)
# def logger(request):
#     logger = logging.getLogger()
#     logger.setLevel(logging.DEBUG)

#     # Create a handler for Report Portal if the service has been
#     # configured and started.
#     if hasattr(request.node.config, "py_test_service"):
#         # Import Report Portal logger and handler to the test module.
#         logging.setLoggerClass(RPLogger)
#         rp_handler = RPLogHandler()

#         # Add additional handlers if it is necessary
#         console_handler = logging.StreamHandler(sys.stdout)
#         console_handler.setLevel(logging.INFO)
#         logger.addHandler(console_handler)
#     else:
#         rp_handler = logging.StreamHandler(sys.stdout)

#     # Set INFO level for Report Portal handler.
#     rp_handler.setLevel(logging.INFO)
#     return logger


# def pytest_configure(config):
#     """
#     pyTest hook method - This is used here to add additional attribute 'Launch Time'
#     and updating Jenkins build URL to the launch desctiption.
#     """
#     if "rp_launch_attributes" in config.inicfg:
#         config.inicfg["rp_launch_attributes"] += f""" 'Launch Time:{datetime.now().strftime("%d/%m/%YT%H.%M.%S")}'"""
