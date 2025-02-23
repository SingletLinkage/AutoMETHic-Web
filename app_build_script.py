import subprocess
import os
import sys

def run_command(command: str, cwd: str = None, log=True) -> None:
        if cwd is None:
            cwd = os.getcwd()

        try:
            print(f"Running command: {command}")
            if log:
                log_progress(f"Running command: {command}", cwd)
                
            process = subprocess.Popen(
                command,
                shell=True,
                cwd=cwd or os.getcwd(),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            while True:
                output = process.stdout.readline()
                if output:
                    print(output.strip())
                err = process.stderr.readline()
                if err:
                    print(f"Error: {err.strip()}", file=sys.stderr)
                    
                if output == '' and err == '' and process.poll() is not None:
                    break
            
            if process.returncode != 0:
                raise subprocess.CalledProcessError(process.returncode, command)
                
        except subprocess.CalledProcessError as e:
            print(f"Command failed with return code {e.returncode}")
            print(f"Command: {command}")
            if log:
                log_progress(f"Command {command} failed with return code {e.returncode}", cwd)
            raise


def log_progress(message, path):
    with open(f"{path}/progress_log.txt", 'a') as f:
        f.write(message + '\n')