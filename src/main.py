import sys
import json
import requests
import scoring

DEBUG=False

def read_markdown(req_name):
    acc = ""

    lines = None
    
    with open(req_name, 'r') as f:
        lines = f.readlines()

    for line in lines:
        acc += line

    return acc

def query_llm_generate_python(user_prompt, seed=123):

    def model():
        return "hf.co/beowolx/CodeNinja-1.0-OpenChat-7B-GGUF"

    def prompt():
        return "" + user_prompt + """\nThe JSON should be structured like this:
    {
        "pythonSource": "the generated Python code as a string"
    }
    """

    def options():
        # set seed for deterministic testing.
        return {"seed": seed}

    def headers():
        return {"content-type": "application/json"}

    if DEBUG:
        print("**PROMPT")
        print(prompt())

    body = {
        "model": model(),
        "format": "json",
        "stream": False,
        "prompt": prompt(),
        "options": options()
    }

    def host():
        return "rk-mbp-g3h"
    url = "http://" + host() + ":11434/api/generate"
    res = requests.post(url, headers=headers(), data = json.dumps(body))

    parsed = json.loads(res.json()["response"])
    return parsed["pythonSource"]

def evolver(req):
    survivors = []

    for i in range(10):
        prog_candidate = query_llm_generate_python("write me a python program that meets the requirements below \ngive me source code as a response\n" + req, seed=i)
        score = scoring.score(prog_candidate)

        if score > 0:
            survivors.append(prog_candidate)

    print("Survivors: " + str(len(survivors)))

def main():
   req_file = sys.argv[1]

   if not req_file:
       raise Error("req file missing")

   req = read_markdown(req_file)

   evolver(req)

main()
