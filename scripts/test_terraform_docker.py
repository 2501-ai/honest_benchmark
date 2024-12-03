import hcl2
import sys

def validate_terraform_config():
    try:
        with open('./datasets/honest_57/main.tf', 'r') as f:
            config = hcl2.load(f)
        
        # Check for required provider
        has_docker_provider = False
        for block in config:
            if 'terraform' in block:
                for required in block['terraform'].get('required_providers', []):
                    if 'docker' in required:
                        has_docker_provider = True
                        break
        
        if not has_docker_provider:
            return "FAIL: Missing docker provider configuration"

        # Validate network resource
        network_found = False
        network_name = None
        for block in config:
            if 'resource' in block:
                for resource_type, resources in block['resource'].items():
                    if resource_type == 'docker_network':
                        network_found = True
                        network_name = list(resources.keys())[0]
                        break
        
        if not network_found:
            return "FAIL: Missing docker_network resource"

        # Validate containers
        required_containers = {'web', 'app', 'db'}
        found_containers = set()
        
        for block in config:
            if 'resource' in block:
                for resource_type, resources in block['resource'].items():
                    if resource_type == 'docker_container':
                        for container_name in resources.keys():
                            found_containers.add(container_name)
                            container_config = resources[container_name]
                            
                            # Check for network connection
                            if 'network_mode' not in container_config and 'networks_advanced' not in container_config:
                                return f"FAIL: Container {container_name} not properly networked"
                            
                            # Check for environment variables
                            if 'env' not in container_config:
                                return f"FAIL: Container {container_name} missing environment variables"
                            
                            # Check for image specification
                            if 'image' not in container_config:
                                return f"FAIL: Container {container_name} missing image specification"

        missing_containers = required_containers - found_containers
        if missing_containers:
            return f"FAIL: Missing required containers: {missing_containers}"

        # Check for dependencies
        has_depends_on = False
        for block in config:
            if 'resource' in block:
                for resource_type, resources in block['resource'].items():
                    if resource_type == 'docker_container':
                        for container_config in resources.values():
                            if 'depends_on' in container_config:
                                has_depends_on = True
                                break

        if not has_depends_on:
            return "FAIL: Missing resource dependencies"

        return "PASS"
        
    except FileNotFoundError:
        return "FAIL: main.tf not found"
    except Exception as e:
        return f"FAIL: Error validating configuration: {str(e)}"

if __name__ == "__main__":
    output = validate_terraform_config()
    print(output)
    sys.exit(0 if output == "PASS" else 1) 