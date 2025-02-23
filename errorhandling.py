from typing import Dict
import json
from sendToAgent import callAgentAPI
import subprocess
import os


def debug_build_error(error_message: str, files: Dict[str, str]) -> Dict[str, str]:

    prompt = {
        "error_message": error_message,
        "files": files
    }    
    print(f"Sending files to debugger-agent with Error Message: {error_message}")
    response = callAgentAPI('debugger-agent', prompt)['response']

    json.dump(response, open('/home/arka/Desktop/Hackathons/KrackHack25/agent_op/debugger_output.json', 'w'))
    
    # Parse response and update files
    fixes = response["fixes"]
    updated_files = {}
    
    for fix in fixes:
        print(f"To fix: {fix['file_path']}")
        updated_files[fix["file_path"]] = fix["updated_code"]
    
    return updated_files



def check_project_errors(self) -> bool:
    """Check for all types of errors without running the app"""
    project_dir = os.path.abspath(self.project_root)
    
    try:
        # Install necessary dev dependencies
        dependencies = [
            "typescript",
            "@types/react",
            "@types/react-dom",
            "eslint",
            "eslint-plugin-react",
            "@typescript-eslint/parser",
            "@typescript-eslint/eslint-plugin"
        ]
        
        self.run_command(f"npm install --save-dev {' '.join(dependencies)}", cwd=project_dir)
        
        # Add scripts to package.json
        package_json_path = os.path.join(project_dir, 'package.json')
        with open(package_json_path, 'r') as f:
            package_data = json.load(f)
        
        if 'scripts' not in package_data:
            package_data['scripts'] = {}
            
        # Add checking scripts
        package_data['scripts'].update({
            'typecheck': "tsc --noEmit",
            'lint': "eslint src --ext .ts,.tsx",
            'check-all': "npm run typecheck && npm run lint"
        })
        
        with open(package_json_path, 'w') as f:
            json.dump(package_data, f, indent=2)
        
        # Create ESLint config if it doesn't exist
        eslint_config = {
            "extends": [
                "react-app",
                "plugin:@typescript-eslint/recommended"
            ],
            "parser": "@typescript-eslint/parser",
            "plugins": ["@typescript-eslint"],
            "rules": {
                "@typescript-eslint/no-explicit-any": "error",
                "no-console": "warn"
            }
        }
        
        eslint_path = os.path.join(project_dir, '.eslintrc.json')
        if not os.path.exists(eslint_path):
            with open(eslint_path, 'w') as f:
                json.dump(eslint_config, f, indent=2)
        
        print("Running all checks...")
        
        errors = []
        try:
            # Run TypeScript type checking
            self.run_command("npm run typecheck", cwd=project_dir)
        except subprocess.CalledProcessError as e:
            errors.append("TypeScript errors found")
            
        try:
            # Run ESLint
            self.run_command("npm run lint", cwd=project_dir)
        except subprocess.CalledProcessError as e:
            errors.append("ESLint errors found")
            
        try:
            # Check for required files
            required_files = ['src/index.tsx', 'public/index.html', 'package.json']
            for file in required_files:
                if not os.path.exists(os.path.join(project_dir, file)):
                    errors.append(f"Missing required file: {file}")
        except Exception as e:
            errors.append(f"File check error: {str(e)}")
            
        try:
            # Check package.json for invalid dependencies
            with open(package_json_path, 'r') as f:
                pkg = json.load(f)
                if 'dependencies' not in pkg or 'react' not in pkg['dependencies']:
                    errors.append("Missing required React dependency")
        except Exception as e:
            errors.append(f"Package.json check error: {str(e)}")
        
        if errors:
            print("\nErrors found during checking:")
            for error in errors:
                print(f"- {error}")
            return False
            
        print("All checks passed successfully!")
        return True
        
    except Exception as e:
        print(f"Error during project checking: {str(e)}")
        return False