import platform
import subprocess
import sys

def is_rosetta():
    return platform.machine() == "x86_64"

def install_polars():
    if is_rosetta():
        print("Installing Rosetta compliant polars")
        subprocess.run(["poetry", "add", "polars-lts-cpu"])
    else:
        print("Installing regular polars")
        subprocess.run(["poetry", "add", "polars"])

if __name__ == "__main__":
    install_polars()