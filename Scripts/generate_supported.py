#! /bin/env python
"""
This script generates Supported.txt and Supported.pickle
based on the models found in the lib and mod files
"""

import os
import pickle
import re

root_path = os.path.join(
    os.path.realpath(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), "..")
    )
)
folder = os.path.join(root_path, "Models")
supported_txt_path = os.path.join(root_path, "Supported.txt")
supported_pickle_path = os.path.join(root_path, "Supported.pickle")

supported = {}

files_txt = []
files_lib = []
files_mod = []
files_spi = []
files_fam = []
files_cir = []
files_sub = []
files_lb5 = []
files_jft = []
files_dio = []
files_bjt = []
files_mos = []
files_other = []


def read_file(file):
    with open(file, encoding="utf8", errors="ignore") as f:
        return f.read().lower()


# Function to extract models from spice file
def extrac_models(path, content, extract, debug=False):
    relativePath = path[str(path).index(folder) + len(folder) :]
    if isinstance(extract, list):
        extract = tuple(extract)
    for line in content.splitlines():
        if line.startswith(extract):
            try:
                model = re.split(r"\s+", line)[
                    1
                ]  # Split the line and get the model
            except IndexError:
                continue
            if model:  # Get rid of empty string
                if debug:
                    print(model)
                if (
                    model not in supported
                ):  # It is the first time we see this model
                    supported[model] = []
                    supported[model].append(
                        relativePath
                    )  # Add to supported with the path to find it
                else:  # It is a duplicate...
                    if (
                        relativePath not in supported[model]
                    ):  # ...but from a different file
                        supported[model].append(relativePath)  # So we add it


# Separate file by extension
for root, _dirs, files in os.walk(folder):
    for name in files:
        f = os.path.join(root, name)
        extension = os.path.splitext(f)[1][1:].lower()

        if extension == "txt":
            files_txt.append(f)
        elif extension == "lib":
            files_lib.append(f)
        elif extension == "mod":
            files_mod.append(f)
        elif extension == "spi":
            files_spi.append(f)
        elif extension == "fam":
            files_fam.append(f)
        elif extension == "cir":
            files_cir.append(f)
        elif extension == "sub":
            files_sub.append(f)
        elif extension == "lb5":
            files_lb5.append(f)
        elif extension == "dio":
            files_dio.append(f)
        elif extension == "bjt":
            files_bjt.append(f)
        elif extension == "jft":
            files_jft.append(f)
        elif extension == "mos":
            files_mos.append(f)
        else:
            files_other.append(f)

# Lets see what we have
print(f"{len(files_txt)} txt found")
print(f"{len(files_lib)} lib found")
print(f"{len(files_mod)} mod found")
print(f"{len(files_spi)} spi found")
print(f"{len(files_fam)} fam found")
print(f"{len(files_cir)} cir found")
print(f"{len(files_sub)} sub found")
print(f"{len(files_lb5)} lb5 found")
print(f"{len(files_dio)} dio found")
print(f"{len(files_bjt)} bjt found")
print(f"{len(files_jft)} jft found")
print(f"{len(files_mos)} mos found")
print(f"{len(files_other)} other kind found")
for f in files_other:
    print(f"Not recognized: {f}")
print()

for file in files_lib:
    content = read_file(file)
    if content.startswith("eeschema-library version 2."):
        # Extract EESchema-LIBRARY Version 2.x
        extrac_models(file, content, "# ")
    else:
        # Extract subckt and model
        extrac_models(file, content, [".subckt", ".model"])

for file in files_mod:
    content = read_file(file)
    # Extract subckt and model
    extrac_models(file, content, [".subckt", ".model"])

for file in files_fam:
    content = read_file(file)
    # Extract subckt
    extrac_models(file, content, ".subckt")

for file in files_sub:
    content = read_file(file)
    # Extract subckt
    extrac_models(file, content, ".subckt")

for file in files_lb5:
    content = read_file(file)
    # Extract subckt and model
    extrac_models(file, content, [".subckt", ".model"])

for file in files_dio:
    content = read_file(file)
    # Extract model
    extrac_models(file, content, ".model")

for file in files_bjt:
    content = read_file(file)
    # Extract model
    extrac_models(file, content, ".model")

for file in files_jft:
    content = read_file(file)
    # Extract model
    extrac_models(file, content, ".model")

for file in files_mos:
    content = read_file(file)
    # Extract model
    extrac_models(file, content, ".model")

print(f"There are {len(supported)} models")

# Write supported models and the path to find them to file
# Pickle file useful to load it later
#  https://docs.python.org/3/library/pickle.html
with open(supported_pickle_path, "wb") as file:
    pickle.dump(supported, file, protocol=pickle.HIGHEST_PROTOCOL)
    print(f"{supported_pickle_path} created")

# Normal text file, good to be read by humans
with open(supported_txt_path, "w") as file:
    """
    # Write part name with path
    for part, path in sorted(supported.items()):
        path = " - ".join(
            p[p.index(folder_name) + len(folder_name) :] for p in path
        )
        file.write(f"{part}\t{path}\n")
    """
    # Write part name without path
    for part in sorted(supported.keys()):
        file.write(part + "\n")
    print(f"{supported_txt_path} created")
