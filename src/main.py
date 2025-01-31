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

def gen_seed_from_feedback(feedback):
    new_candidates = []

    for fb in feedback:
        try:
            prog_candidate = query_llm_generate_python("write me a python program using the following info. py_source is the current code, and there is pylint feedback. fix the issues that pylint has pointed out\n" + json.dumps(fb))
            new_candidates.append(prog_candidate)
        except:
            pass

    return new_candidates

def evolver_iter(candidates):
    feedback = []
    survivors = []

    for c in candidates:
       score = scoring.score(c)
       pylint_score = score["pylint"]["score"]

       if pylint_score < 0.01:
           feedback.append({"py_source": prog_candidate, "pylint": score["pylint"] })

       if pylint_score > 0:
           survivors.append(prog_candidate)

    if len(survivors) > 2:
        print("evolve_iter has survivors: " + str(len(survivors)))
        return survivors

def evolver(req):
    survivors = []
    feedback = []

    for i in range(10):
        prog_candidate = query_llm_generate_python("write me a python program that meets the requirements below \ngive me source code as a response\n" + req, seed=i)
        score = scoring.score(prog_candidate)

        pylint_score = score["pylint"]["score"]

        if pylint_score < 0.01:
            feedback.append({"py_source": prog_candidate, "pylint": score["pylint"] })

        if pylint_score > 0:
            survivors.append(prog_candidate)


    if len(survivors) == 0:
        print("no survivors left. should go back a generation or incorporate feedback")

        prog_candidates = gen_seed_from_feedback(feedback)

        if len(prog_candidates) > 2:
            print("has feedback candidates")
            new_seed = evolver_iter(prog_candidates)
            print(new_seed)

    elif len(survivors) > 5:
        print("has survivors. progress to the next generation")

def main():
   req_file = sys.argv[1]

   if not req_file:
       raise Error("req file missing")

   req = read_markdown(req_file)

   evolver(req)

main()
