# import os
# import sys

# # IMPORTANT: Set this BEFORE importing eventlet
# os.environ["EVENTLET_NO_GREENDNS"] = "yes"

# import eventlet

# # Monkey patch with DNS excluded to avoid Windows DNS issues
# eventlet.monkey_patch(
#     socket=True,
#     dns=False,
#     time=True,
#     select=True,
#     thread=False,
#     os=True,
#     ssl=True,
#     httplib=True,
#     subprocess=True,
#     sys=True,
#     aggressive=True,
#     mysqldb=True,
#     builtins=True,
#     all=False,
# )

# # Add project root to path
# sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# # Import Celery app and tasks
# from app.celery_app import celery_app
# from app.celery_tasks import *

# if __name__ == "__main__":
#     celery_app.start()
# This file is the entry point for the Celery worker.
# It should be at the root of your project.

# 1. Import the central Celery app instance.
from app.celery_app import celery_app

# 2. Import the tasks. This is crucial.
#    This line ensures that when the worker starts, it knows about all the
#    tasks defined in your `celery_tasks.py` file.
from app.celery_tasks import *
