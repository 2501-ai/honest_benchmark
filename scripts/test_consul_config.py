import json
import sys

def validate_consul_config():
    try:
        with open('./datasets/honest_59/consul-config.json', 'r') as f:
            config = json.load(f)

        # Validate node and datacenter configuration
        if config.get('node_name') != 'local-node':
            return "FAIL: Incorrect node_name"
        if config.get('datacenter') != 'dc1':
            return "FAIL: Incorrect datacenter"

        # Validate services
        required_services = {
            'web': 8080,
            'api': 3000,
            'cache': 6379
        }
        
        services = config.get('services', [])
        if len(services) != len(required_services):
            return "FAIL: Incorrect number of services"

        for service in services:
            name = service.get('name')
            if name not in required_services:
                return f"FAIL: Unexpected service {name}"
            if service.get('port') != required_services[name]:
                return f"FAIL: Incorrect port for service {name}"
            
            # Validate health checks
            if 'check' not in service:
                return f"FAIL: Missing health check for service {name}"
            check = service['check']
            if 'interval' not in check or 'timeout' not in check:
                return f"FAIL: Incomplete health check configuration for service {name}"

            # Validate metadata
            if 'meta' not in service or service['meta'].get('environment') != 'local':
                return f"FAIL: Incorrect metadata for service {name}"

        # Validate global settings
        if config.get('connect', {}).get('enabled') is not True:
            return "FAIL: Connect not enabled"
        if config.get('ui_config', {}).get('enabled') is not True:
            return "FAIL: UI not enabled"

        return "PASS"
        
    except FileNotFoundError:
        return "FAIL: consul-config.json not found"
    except Exception as e:
        return f"FAIL: Error validating configuration: {str(e)}"

if __name__ == "__main__":
    output = validate_consul_config()
    print(output)
    sys.exit(0 if output == "PASS" else 1) 