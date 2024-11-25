error_messages = [
    "ERROR: Failed to bind socket on address 0.0.0.0:80: address already in use.",
    'ERROR: for mongo_service  Cannot start service mongo_service: OCI runtime create failed: container_linux.go:345: starting container process caused "process_linux.go:424: container init caused \\"rootfs_linux.go:70: creating device nodes caused \\\\\\"open /dev/ptmx: no such file or directory\\\\\\"\\"": unknown',
    "ERROR: for mongo_service  Cannot start service mongo_service: failed to create endpoint my_container on network my_bridge_network: failed to add the host (veth1234abcd) <=> sandbox (eth0) pair interfaces: operation not permitted",
    "ERROR: for mongo_service  Cannot start service mongo_service: network my_overlay_network not found"
]

with open('./datasets/honest_51/repairs.txt', 'r') as file:
    file_content = file.read()

def verify_errors_in_file(file_content, error_messages):
    missing_errors = []
    for error in error_messages:
        if error not in file_content:
            missing_errors.append(error)
    if not missing_errors:
        print("All error messages are present in 'repairs.txt'.")
        return True
    else:
        print("The following error messages are missing from 'repairs.txt':")
        for error in missing_errors:
            print(f"- {error}")
        return False

verify_errors_in_file(file_content, error_messages)