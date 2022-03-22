from distutils.core import setup

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

requirements.append(
    "gtrfile @ git+https://github.com/spectral307/gtrfile.git#egg=gtrfile-1.0.0")

setup(name="sixv_magresp",
      version="0.0.0",
      packages=["sixv_magresp"],
      install_requires=requirements)
