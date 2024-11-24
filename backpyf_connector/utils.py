
import os
import sys

def load_env():
    with open(sys.path[1]+"\\keys.env") as f:
        for line in f:
            if line.strip() and not line.startswith("#"):
                key, value = line.strip().split("=", 1)
                os.environ[key] = value
load_env()
