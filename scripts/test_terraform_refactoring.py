import os
import sys

def validate_terraform_resources():
    """
    Validates that load balancer resources exist in main.tf
    """
    try:
        base_path = './datasets/honest_61'
        main_tf_path = os.path.join(base_path, 'main.tf')
        
        # Check if main.tf exists
        if not os.path.exists(main_tf_path):
            return "FAIL: main.tf not found"
        
        # Read main.tf
        with open(main_tf_path, 'r') as f:
            content = f.read()
            
        # Check if load balancer resources exist
        required_resources = [
            "aws_lb",
            "aws_lb_target_group",
            "aws_lb_listener"
        ]
        
        for resource in required_resources:
            if f"resource \"{resource}\"" not in content:
                return f"FAIL: Required resource '{resource}' not found in main.tf"
                
        # Check if they are in the correct order (after EC2, before database)
        ec2_pos = content.find("resource \"aws_instance\"")
        lb_pos = content.find("resource \"aws_lb\"")
        db_pos = content.find("resource \"aws_db_instance\"")
        
        if not (ec2_pos < lb_pos < db_pos):
            return "FAIL: Load balancer resources are not in the correct position (should be after EC2 instances and before database resources)"
            
        return "PASS"
        
    except Exception as e:
        return f"FAIL: Error validating resources: {str(e)}"

if __name__ == "__main__":
    output = validate_terraform_resources()
    print(output)
    sys.exit(0 if output == "PASS" else 1) 