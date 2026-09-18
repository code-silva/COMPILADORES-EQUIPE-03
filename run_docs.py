import sys
import subprocess

commands = [
    f"{sys.executable} -m pip install pipenv",
    f"{sys.executable} -m pipenv install --skip-lock",
    f"{sys.executable} -m pipenv install mkdocs mkdocs-material",
    f"{sys.executable} -m pipenv run mkdocs serve"
]

for cmd in commands:
    subprocess.run(cmd, shell=True, check=True)