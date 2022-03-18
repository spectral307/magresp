from distutils.core import setup

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(name="sixv_magresp",
      version="0.0.0",
      packages=["sixv_magresp"],
      install_requires=requirements)
