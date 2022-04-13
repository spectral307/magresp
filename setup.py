from setuptools import setup

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

# requirements.append(
#     "gtrfile @ git+https://github.com/spectral307/gtrfile.git#egg=gtrfile-1.0.0")

setup(name="magresp",
      version="0.0.0",
      packages=["magresp"],
      package_data={"magresp": ["default_settings.json"]},
      install_requires=requirements)
