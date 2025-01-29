import subprocess
import re

def pylint(py_source):
    pylint_cmd = ['pylint', '--from-stdin', 'anyname']

    try:
        process = subprocess.Popen(pylint_cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stdout, stderr = process.communicate(input=py_source)

        if stdout:
            match = re.search(r'Your code has been rated at (\d+\.\d+)/\d+', stdout)

            score = float(match.group(1))
            return score
        if stderr:
            raise("Pylint error")
    except Exception as e:
        print(f"An error occurred: {e}") 

def score(py_source):
    # run scoring functions here

    # characteristics:
    # linter: pylint, pick one for now
    return pylint(py_source)

    # return weighted score out of 100.
    