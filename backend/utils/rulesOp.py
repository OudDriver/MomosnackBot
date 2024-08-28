import json
import re

def load_rules():
    with open("rules.json") as f:
        return json.loads(f.read())

def save_rules(ruleDict):
    with open("rules.json", "w") as f:
        finalJSON = json.dumps(ruleDict)
        finalJSON = re.sub(r"\\\\", r"\\", finalJSON)
        print(finalJSON)
        f.write(finalJSON)