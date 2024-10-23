from pymongo import MongoClient
import subprocess

def validate_attack():
    try:
        client = MongoClient("mongodb://localhost:27017/")
        
        if "hacked_db" not in client.list_database_names():
            print("Validation failed: 'hacked_db' not found.")
            return
        db = client["hacked_db"]
        collection = db["fun"]
        
        result = collection.find_one({"message": "You have been hacked! Just kidding."})
        
        if result:
            print("Validation successful: Hacker message found in 'hacked_db'.")
        else:
            print("Validation failed: Hacker message not found in 'fun' collection.")
    
    except Exception as e:
        print(f"Validation failed due to an error: {e}")
    
    finally:
        try:
            container_name = "mongo_vulnerable"
            
            subprocess.run(["docker", "stop", container_name], check=True)
            
            subprocess.run(["docker", "rm", container_name], check=True)
            
            print(f"Container '{container_name}' stopped and removed successfully.")
        
        except subprocess.CalledProcessError as e:
            print(f"Failed to stop and remove the container: {e}")

validate_attack()
