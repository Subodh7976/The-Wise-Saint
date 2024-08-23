from typing import Any
import json
import tempfile
import docker # type: 
import shlex
import uuid
import os

class SandboxExecutor:

    def __init__(self, language: str = "python"):
        self.client = docker.from_env()
    
    def create_docker_container(self, image_name="python:3.9-slim"):
        '''
        Creates a docker container that is used for executing the llm generated code in a sandbox environment

        Args:
            image_name: str - Docker execution image name
        
        Return:
            docker-container

        '''
        container = self.client.containers.run(
            image=image_name,
            command="sleep infinity",
            detach=True,
            auto_remove=True,
            mem_limit='256m',
            cpuset_cpus="0",
            network_disabled=True,
        )

        return container
        
    
    def execute_code(self, code: str, test_cases: str, container: Any, timeout=5):
        # TODO: Expand the support to Cpp and Java
        '''
        Executing the llm code in the sanbox container with test cases. 
        
        Args:
            code: str - llm generated code
            test_cases: str - llm generated test cases
            container - docker container object
            timeout: int - maximum running time for a program

        Return:
            stdout, stderr - terminal output, code execution error
        '''
        
        code_file = f"/tmp/{uuid.uuid4().hex}.py"
        input_file = f"/tmp/{uuid.uuid4().hex}_input.txt"

        try:

            # Handling the code and inputs error while writing using echo.
            code_command = f"echo \"{code.replace('"', '\\"').replace('$', '\\$')}\" > {code_file}" 
            input_command = f"echo \"{test_cases.replace('"', '\\"').replace('$', '\\$')}\" > {input_file}"
            
            container.exec_run(f"bash -c '{code_command}'")
            container.exec_run(f"bash -c '{input_command}'")

            # Check if files are created
            ls_result = container.exec_run(f"ls -l /tmp", tty=False)
            print("Files in container:\n", ls_result.output.decode('utf-8'))

            # Checking the file contents
            code_contents = container.exec_run(f'cat {code_file}', tty=False).output.decode('utf-8')
            input_contents = container.exec_run(f'cat {input_file}', tty=False).output.decode('utf-8')
            print(f"Code file contents:\n{code_contents}")
            print(f"Input file contents:\n{input_contents}")

            #Executing the 
            exec_command = f'echo "{test_cases.strip()}" | timeout {timeout}s python3 {code_file}'
            exec_result = container.exec_run(f'bash -c "{exec_command}"', tty=False, stdout=True, stderr=True)

            output = exec_result.output.decode('utf-8')
            stdout = output

            return stdout, ""
        except Exception as e:
            return "", str(e)
    

    def run_code(self, code: str, test_cases: str, timeout=5):
        '''
        Running the provided code in the sandbox container.
        Args:
            code: str - llm generated code
            test_cases: str - llm generated test cases
            timeout: int - maximum running time for a program

        Return:
            stdout - terminal output
            stderr - code execution error

        '''
        
        container = self.create_docker_container() 
        
        try:
            stdout, stderr = self.execute_code(code, test_cases, container, timeout)
        finally:
            container.kill() #Cleaning up the container after execution.
        
        if stderr:
            return f"Error: {stderr}"
        return stdout