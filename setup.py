from setuptools import setup, find_packages

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

requirements.append(
    "gtrfile @ git+https://github.com/spectral307/gtrfile.git#egg=gtrfile-1.0.0")
requirements.append(
    "snap_cursor_stack @ git+https://github.com/spectral307/snap_cursor_stack.git#egg=gtrfile-1.0.0")

setup(name="magresp",
      version="1.0.1",
      #   packages=find_packages(),
      packages=["magresp", "magresp.errors", "magresp.images"],
      package_data={"magresp": ["default_settings.json"],
                    "magresp.images": ["plus.png", "minus.png"]},
      install_requires=requirements)
