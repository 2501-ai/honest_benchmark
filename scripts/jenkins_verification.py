import subprocess
import os

jenkinsfile_path = './datasets/honest_53/Jenkinsfile'

output = "FAIL"
if os.path.exists(jenkinsfile_path):
    try:
        result = subprocess.run(['jenkins', 'build', 'job'], cwd='./datasets/honest_108', capture_output=True, text=True)
        if result.returncode == 0:
            output = "PASS"
    except Exception as e:
        print(f"Error during Jenkins test: {e}")

print(output)
