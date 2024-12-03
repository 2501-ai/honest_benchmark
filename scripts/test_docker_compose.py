import yaml
import sys

def validate_docker_compose():
    try:
        with open('./datasets/honest_56/docker-compose.yml', 'r') as f:
            config = yaml.safe_load(f)
            
        # Check if all required services exist
        required_services = ['frontend', 'api', 'redis']
        if not all(svc in config['services'] for svc in required_services):
            return "FAIL: Missing required services"
            
        # Validate images
        expected_images = {
            'frontend': 'nginx',
            'api': 'python',
            'redis': 'redis'
        }
        
        for service, expected_image in expected_images.items():
            if not config['services'][service].get('image', '').startswith(expected_image):
                return f"FAIL: Invalid image for {service}"
        
        # Validate ports
        expected_ports = {
            'frontend': '80',
            'api': '5000',
            'redis': '6379'
        }
        
        for service, expected_port in expected_ports.items():
            ports = config['services'][service].get('ports', [])
            if not any(str(expected_port) in str(port) for port in ports):
                return f"FAIL: Missing or invalid port for {service}"
        
        # Check for proper networking
        if 'networks' not in config:
            return "FAIL: No networks defined"
            
        # Ensure services are in the same network
        network_name = list(config['networks'].keys())[0]
        if not all('networks' in config['services'][svc] and 
                  network_name in config['services'][svc]['networks'] 
                  for svc in required_services):
            return "FAIL: Services not properly networked"
        
        # Check for healthchecks
        if not all('healthcheck' in config['services'][svc] 
                  for svc in required_services):
            return "FAIL: Missing healthchecks"
        
        return "PASS"
        
    except Exception as e:
        return f"FAIL: Error validating configuration: {str(e)}"

if __name__ == "__main__":
    output = validate_docker_compose()
    print(output)
    sys.exit(0 if output == "PASS" else 1)