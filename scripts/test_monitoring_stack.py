import yaml
import os
import sys

def validate_prometheus_config():
    try:
        with open('./datasets/honest_60/prometheus.yml', 'r') as f:
            config = yaml.safe_load(f)
            
        # Check global config
        if 'global' not in config:
            return "FAIL: Missing global configuration in prometheus.yml"
            
        # Validate scrape configs
        if 'scrape_configs' not in config:
            return "FAIL: Missing scrape_configs in prometheus.yml"
            
        scrape_configs = config['scrape_configs']
        required_jobs = {
            'prometheus': 9090,
            'node': 9100,
        }
        
        for job_name, port in required_jobs.items():
            job_found = False
            for job in scrape_configs:
                if job.get('job_name') == job_name:
                    job_found = True
                    targets = job.get('static_configs', [{}])[0].get('targets', [])
                    if not any(str(port) in target for target in targets):
                        return f"FAIL: Invalid port for job {job_name}"
                    break
            if not job_found:
                return f"FAIL: Missing job configuration for {job_name}"
                
        return "PASS"
    except Exception as e:
        return f"FAIL: Error in prometheus.yml: {str(e)}"

def validate_docker_compose():
    try:
        with open('./datasets/cloud_5/docker-compose.yml', 'r') as f:
            compose = yaml.safe_load(f)
            
        if 'services' not in compose:
            return "FAIL: Missing services in docker-compose.yml"
            
        required_services = {
            'prometheus': {
                'image': 'prom/prometheus',
                'port': '9090',
                'volume': 'prometheus.yml'
            },
            'grafana': {
                'image': 'grafana/grafana',
                'port': '3000'
            },
            'node-exporter': {
                'image': 'prom/node-exporter',
                'port': '9100'
            }
        }
        
        services = compose['services']
        for service_name, requirements in required_services.items():
            if service_name not in services:
                return f"FAIL: Missing {service_name} service"
                
            service = services[service_name]
            
            # Check image
            if 'image' not in service or not service['image'].startswith(requirements['image']):
                return f"FAIL: Invalid image for {service_name}"
                
            # Check port
            if 'ports' not in service or not any(requirements['port'] in port for port in service['ports']):
                return f"FAIL: Invalid port mapping for {service_name}"
                
            # Check volume for Prometheus
            if service_name == 'prometheus':
                if 'volumes' not in service or not any('prometheus.yml' in vol for vol in service['volumes']):
                    return "FAIL: Missing prometheus.yml volume mount"
                    
        # Check dependencies
        if 'depends_on' not in services['grafana'] or 'prometheus' not in services['grafana']['depends_on']:
            return "FAIL: Missing dependency: grafana should depend on prometheus"
            
        return "PASS"
    except Exception as e:
        return f"FAIL: Error in docker-compose.yml: {str(e)}"

def main():
    prom_result = validate_prometheus_config()
    if prom_result != "PASS":
        print(prom_result)
        return 1
        
    compose_result = validate_docker_compose()
    if compose_result != "PASS":
        print(compose_result)
        return 1
        
    print("PASS")
    return 0

if __name__ == "__main__":
    sys.exit(main()) 