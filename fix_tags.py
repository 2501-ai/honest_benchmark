import json

input_file = './config/honest_benchmark.jsonl' 
output_file = './config/honest_benchmark_fixed.jsonl'

with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
    for line in infile:
        # Parse the JSON line
        data = json.loads(line)
        
        if 'tags' in data:
            if isinstance(data['tags'], list) and len(data['tags']) == 1 and isinstance(data['tags'][0], str):
                data['tags'] = [tag.strip() for tag in data['tags'][0].split(',')]
        
        outfile.write(json.dumps(data) + '\n')

print(f"Fixed tags written to {output_file}")