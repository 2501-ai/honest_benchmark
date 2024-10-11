import sys

app_content = open('./datasets/honest_48/app.py', 'r').read()
required_patterns = ['from flask import Flask', 'from flask_restful import', 'class User', '(Resource):',
                     'def post(self):', 'def get(self',
                     'def put(self, user_id):', 'def delete(self, user_id):']
if all(pattern in app_content for pattern in required_patterns):
    print("All required patterns found!")
    sys.exit(0)

print(
    f"Some required patterns are missing! : {[pattern for pattern in required_patterns if not pattern in app_content]} ")
sys.exit(1)
