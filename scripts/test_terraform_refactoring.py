import os
import re
import subprocess
import sys

def validate_terraform_refactoring():
    """
    Validates that the Terraform code has been properly refactored according to requirements:
    - Created agent_resources.tf
    - Used for_each for dynamic resource creation
    - Created modules
    - Replaced hardcoded values with variables
    - Configuration passes 'terraform validate'
    """
    try:
        base_path = './datasets/honest_48'
        main_tf_path = os.path.join(base_path, 'main.tf')
        agent_resources_path = os.path.join(base_path, 'agent_resources.tf')
        
        # Check if agent_resources.tf exists
        if not os.path.exists(agent_resources_path):
            return "FAIL: Missing agent_resources.tf file"
        
        # Check if main.tf exists for refactoring
        if not os.path.exists(main_tf_path):
            return "FAIL: main.tf not found"
        
        # Validate Terraform configuration
        terraform_validate = subprocess.run(
            ['terraform', 'validate'], 
            cwd=base_path,
            capture_output=True, 
            text=True
        )
        
        if terraform_validate.returncode != 0:
            return f"FAIL: Terraform validation failed: {terraform_validate.stderr}"
        
        # Check for for_each usage in main.tf
        with open(main_tf_path, 'r') as f:
            main_content = f.read()
            
        has_for_each = 'for_each' in main_content
        if not has_for_each:
            return "FAIL: No for_each used for dynamic resource creation"
        
        # Check for module usage
        module_pattern = re.compile(r'module\s+["\']\w+["\']')
        has_modules = bool(module_pattern.search(main_content))
        if not has_modules:
            return "FAIL: No modules created or used"
        
        # Check for variables usage
        var_pattern = re.compile(r'var\.\w+')
        has_variables = bool(var_pattern.search(main_content))
        if not has_variables:
            return "FAIL: No variables used to replace hardcoded values"
        
        # Check agent_resources.tf content
        with open(agent_resources_path, 'r') as f:
            agent_content = f.read()
            
        if len(agent_content.strip()) < 50:
            return "FAIL: agent_resources.tf does not contain enough infrastructure definition"
        
        # Check for resource definition in agent_resources.tf
        resource_pattern = re.compile(r'resource\s+["\']\w+["\']')
        has_resources = bool(resource_pattern.search(agent_content))
        if not has_resources:
            return "FAIL: No resources defined in agent_resources.tf"
            
        return "PASS"
        
    except Exception as e:
        return f"FAIL: Error validating refactored Terraform: {str(e)}"

def validate_terraform_section_insertion():
    """
    Validates that a specific section from source file has been inserted into 
    the target file between defined markers, and the configuration passes validation.
    """
    try:
        base_path = './datasets/honest_48'
        main_tf_path = os.path.join(base_path, 'main.tf')
        source_tf_path = os.path.join(base_path, 'source_config.tf')
        
        # Check if required files exist
        if not os.path.exists(main_tf_path):
            return "FAIL: main.tf not found"
            
        if not os.path.exists(source_tf_path):
            return "FAIL: source_config.tf not found"
        
        # Validate Terraform configuration
        terraform_validate = subprocess.run(
            ['terraform', 'validate'], 
            cwd=base_path,
            capture_output=True, 
            text=True
        )
        
        if terraform_validate.returncode != 0:
            return f"FAIL: Terraform validation failed: {terraform_validate.stderr}"
        
        # Read the source file to get the section that should be inserted
        with open(source_tf_path, 'r') as f:
            source_content = f.read()
            
        # Extract the section to be inserted (assuming it's between "# BEGIN SECTION C" and "# END SECTION C")
        section_pattern = re.compile(r'# BEGIN SECTION C\s*(.*?)\s*# END SECTION C', re.DOTALL)
        section_match = section_pattern.search(source_content)
        
        if not section_match:
            return "FAIL: Section C not found in source_config.tf"
            
        expected_section = section_match.group(1).strip()
        
        # Read the main.tf to check if the section was properly inserted
        with open(main_tf_path, 'r') as f:
            main_content = f.read()
            
        # Check if main.tf contains the section A and B markers
        if "# END SECTION A" not in main_content:
            return "FAIL: Section A endpoint not found in main.tf"
            
        if "# BEGIN SECTION B" not in main_content:
            return "FAIL: Section B starting point not found in main.tf"
        
        # Extract the content between section A and B
        between_sections_pattern = re.compile(r'# END SECTION A\s*(.*?)\s*# BEGIN SECTION B', re.DOTALL)
        between_match = between_sections_pattern.search(main_content)
        
        if not between_match:
            return "FAIL: Could not find content between Section A and B"
            
        inserted_content = between_match.group(1).strip()
        
        # Check if the inserted content contains the expected section
        # Using a more flexible check - the inserted content should contain 
        # the key parts of the expected section
        expected_lines = [line.strip() for line in expected_section.split('\n') if line.strip()]
        
        # Check that at least 80% of the expected lines are in the inserted content
        found_lines = 0
        for line in expected_lines:
            if line in inserted_content:
                found_lines += 1
                
        match_percentage = found_lines / len(expected_lines) if expected_lines else 0
        
        if match_percentage < 0.8:  # 80% threshold
            return f"FAIL: Expected section not properly inserted (only {match_percentage*100:.1f}% match)"
            
        return "PASS"
        
    except Exception as e:
        return f"FAIL: Error validating section insertion: {str(e)}"

if __name__ == "__main__":
    output = validate_terraform_section_insertion()
    print(output)
    sys.exit(0 if output == "PASS" else 1) 