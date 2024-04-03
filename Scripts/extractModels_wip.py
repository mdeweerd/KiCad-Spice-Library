#!/usr/bin/env python3
import os
import re
import subprocess
from os.path import abspath, dirname, join

# Quick implementation to get models from library.
# Tries to read from "spiceModels.lst" if no arguments are provided

DEFAULT_MODEL_LIST = "spiceModels.lst"

# Get paths
base_path = dirname(abspath(__file__))
model_path = abspath(join(base_path, "..", "Models"))
check_supported_script = join(base_path, "check_supported.py")

# Define regular expressions
comments_regex = r"(?<comments>(?:(?<=\n)\s*#[^\R*]\R))*"
continued_no_paren_lines = r"(?:(?<=\n)\+[^\R*()]\R)*"
model_paren_regex = r"(?:\.model\s+_NAME_\s+(?<type>\S+)\s*\([^)]*\))"
model_line_regex = (
    r"(?:\.model\s+_NAME_\s+(?<type>\S+)\s*[^()]*?\R"
    + continued_no_paren_lines
    + r")"
)
model_regex = f"(?<model>{model_paren_regex}|{model_line_regex})"
all_regex = f"(?<matched>{comments_regex}[ \t]*(?:{model_regex})\\s*?)"


# Extract a "model" from a file
def extract_from_file(name, file_path):
    with open(file_path) as file:
        file_content = file.read()

    regex = all_regex.replace("_NAME_", re.escape(name))
    model = re.search(regex, file_content, flags=re.IGNORECASE | re.DOTALL)
    if model:
        return model.group("matched")
    return None


# Get library by using 'check_supported.py' script
def get_best_file_for_model(model_name):
    model_name = model_name.replace('"', '\\"')
    result = subprocess.getoutput(f'{check_supported_script} "{model_name}"')
    match = re.search(
        r"Found in\s+-\s+(.*?)\n", result, flags=re.IGNORECASE | re.DOTALL
    )
    if match:
        return match.group(1)
    return None


# Handle CLI
models = []
if len(os.sys.argv) > 1:
    # Get from CLI arguments
    models = os.sys.argv[1:]
elif os.path.isfile(DEFAULT_MODEL_LIST):
    # Get models from configuration file
    with open(DEFAULT_MODEL_LIST) as file:
        models = file.read().splitlines()
else:
    # Simple test
    print(
        "Retrieves models for simulations from list provided on CLI or",
        DEFAULT_MODEL_LIST,
    )
    print("Specify a model like this:")
    print(" - 2N7000#Transistor/FET/MOS.lib, or")
    print(" - 2N7000 without the library")
    print("\nSample Result:")

    models.append("2N7000#Transistor/FET/MOS.lib")

# Get the models as requested
for model_spec in models:
    match = re.match(r"(?P<modelName>[^#]*)(?:#(?P<path>.*))?", model_spec)
    model_name = match.group("modelName")
    file = match.group("path")

    if not file:
        file = get_best_file_for_model(model_name)

    abs_file = join(model_path, file) if file else None

    if abs_file and os.path.isfile(abs_file):
        model = extract_from_file(model_name, abs_file)
        if model:
            print(f"*\n* {model_name} - Extracted from '{file}'\n*\n{model}")
        else:
            print(f"*\n* {model_name} - Model not found in '{file}'\n*")
    else:
        print(f"*\n* {model_name} - File '{file}' not found\n*")
