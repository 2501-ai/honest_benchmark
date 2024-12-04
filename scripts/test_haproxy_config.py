import re
import sys

def validate_haproxy_config():
    try:
        with open('./datasets/honest_58/haproxy.cfg', 'r') as f:
            config = f.read()

        # Required sections
        required_sections = [
            'global',
            'defaults',
            'frontend',
            'backend'
        ]
        
        for section in required_sections:
            if not re.search(rf'^{section}\b', config, re.MULTILINE):
                return f"FAIL: Missing {section} section"

        # Validate frontend configuration
        frontend_checks = [
            r'bind\s+\*:80',  # or another port
            r'default_backend\s+web_backend'
        ]
        
        for check in frontend_checks:
            if not re.search(check, config, re.MULTILINE):
                return f"FAIL: Invalid frontend configuration - missing {check}"

        # Validate backend configuration
        backend_checks = [
            r'backend\s+web_backend',
            r'balance\s+roundrobin',
            r'option\s+httpchk',
            r'server\s+server1\s+\S+:8081\s+check',
            r'server\s+server2\s+\S+:8082\s+check',
            r'server\s+server3\s+\S+:8083\s+check'
        ]
        
        for check in backend_checks:
            if not re.search(check, config, re.MULTILINE):
                return f"FAIL: Invalid backend configuration - missing {check}"

        # Validate health checks
        health_checks = [
            r'option\s+httpchk',
            r'check\s+inter\s+\d+',
            r'check\s+rise\s+\d+',
            r'check\s+fall\s+\d+'
        ]
        
        health_check_count = sum(1 for check in health_checks if re.search(check, config, re.MULTILINE))
        if health_check_count < 2:  # At least basic health check configuration
            return "FAIL: Insufficient health check configuration"

        # Validate global settings
        global_settings = [
            r'maxconn\s+\d+',
            r'log\s+\S+'
        ]
        
        global_count = sum(1 for setting in global_settings if re.search(setting, config, re.MULTILINE))
        if global_count < 1:
            return "FAIL: Missing essential global settings"

        return "PASS"
        
    except FileNotFoundError:
        return "FAIL: haproxy.cfg not found"
    except Exception as e:
        return f"FAIL: Error validating configuration: {str(e)}"

if __name__ == "__main__":
    output = validate_haproxy_config()
    print(output)
    sys.exit(0 if output == "PASS" else 1) 