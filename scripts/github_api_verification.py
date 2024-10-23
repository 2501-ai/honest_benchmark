import os
import json

output = "FAIL"

if os.path.exists('./datasets/honest_52/trending_repos.json'):
    try:
        with open('./datasets/honest_52/trending_repos.json', 'r') as file:
            data = json.load(file)
            if isinstance(data, list) and len(data) > 0:
                output = "PASS"
    except json.JSONDecodeError:
        pass

print(output)
