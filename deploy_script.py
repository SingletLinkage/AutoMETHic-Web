from app_build_script import run_command # log_progress
import os
import requests
import json
from dotenv import load_dotenv
load_dotenv()

GITHUB_API_URL = "https://api.github.com"
HEADERS = {
    "Authorization": f"Bearer {os.environ['TOKEN']}",
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28"
}

def add_homepage_to_package_json(file_path="package.json", homepage_url="https://yourusername.github.io/your-repo"):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            package_data = json.load(file)

        package_data["homepage"] = homepage_url

        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(package_data, file, indent=2)

        print(f"'homepage' added to {file_path}: {homepage_url}")

    except FileNotFoundError:
        print(f"Error: {file_path} not found.")
    except json.JSONDecodeError:
        print(f"Error: {file_path} is not a valid JSON file.")



def enable_workflow_permissions(username, repo_name):
    # First enable Actions
    actions_url = f"{GITHUB_API_URL}/repos/{username}/{repo_name}/actions/permissions"
    actions_data = {
        "enabled": True,
        "allowed_actions": "all"
    }
    response = requests.put(actions_url, headers=HEADERS, json=actions_data)
    if response.status_code not in [200, 204]:
        print(f"Failed to enable Actions: {response.text}")
        return

    # Then set workflow permissions
    workflow_url = f"{GITHUB_API_URL}/repos/{username}/{repo_name}/actions/permissions/workflow"
    workflow_data = {
        "default_workflow_permissions": "write",
        "can_approve_pull_request_reviews": True
    }
    
    response = requests.put(workflow_url, headers=HEADERS, json=workflow_data)
    if response.status_code in [200, 204]:
        print("GitHub Actions workflows have read & write permissions!")
    else:
        print(f"Failed to enable workflow permissions: {response.text}")



def setup_repo(username, repo_name, path):
    # Check if the repository already exists
    repo_url = f"{GITHUB_API_URL}/repos/{username}/{repo_name}"
    response = requests.get(repo_url, headers=HEADERS)

    if response.status_code == 200:
        print(f"Repository '{repo_name}' already exists. Skipping creation.")
    else:
        print(f"Creating repository '{repo_name}' on GitHub...")
        run_command(f"gh repo create {repo_name} --public", cwd=path)

    url = f"https://api.github.com/repos/{username}/{repo_name}"
    data = {"private": False}

    response = requests.patch(url, headers=HEADERS, json=data)

    if response.status_code == 200:
        print("Repository is now public!")
    else:
        print("Error:", response.json())



def git_init(username, repo_name, path):
    import subprocess

    run_command("git init", cwd=path)
    run_command("git branch -M main", cwd=path)

    remote_check = subprocess.run(["git", "remote"], capture_output=True, text=True, cwd=path)
    if "origin" not in remote_check.stdout:
        run_command(f"git remote add origin https://github.com/{username}/{repo_name}.git", cwd=path)
    else:
        print("Remote 'origin' already exists. Skipping...")

    # Ensure .env is in .gitignore
    gitignore_path = os.path.join(path, ".gitignore")
    if not os.path.exists(gitignore_path) or ".env" not in open(gitignore_path).read():
        with open(gitignore_path, "a") as f:
            f.write("\n.env\n")
        run_command("git add .gitignore", cwd=path)

    # Add and commit changes if necessary
    status_output = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True, cwd=path)
    if status_output.stdout.strip():
        run_command("git add .", cwd=path)
        run_command("git commit -m 'Initial commit'", cwd=path)
    else:
        print("No changes to commit. Skipping commit step.")

    # Push main branch
    run_command("git push -u origin main", cwd=path)

    # Create & push gh-pages branch
    run_command("git checkout --orphan gh-pages", cwd=path)
    run_command("git commit --allow-empty -m 'Initial commit for GitHub Pages'", cwd=path)
    run_command("git push -u origin gh-pages", cwd=path)



def push_changes(commit_message="Update changes", path="."):
    import subprocess
    try:
        # Ensure we are on the main branch
        branch_output = subprocess.run(
            ["git", "branch", "--show-current"],
            capture_output=True,
            text=True,
            check=True,
            cwd=path
        )
        current_branch = branch_output.stdout.strip()
        
        if current_branch != "main":
            print(f" Current branch is {current_branch}, switching to main...")
            run_command("git checkout main", cwd=path)
        
        # Check if there are any changes to commit
        status_output = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True,
            check=True,
            cwd=path
        )

        if not status_output.stdout.strip():
            print(" No changes to commit.")
            return

        # Add all changes
        run_command("git add .", cwd=path)
        print(" Changes staged for commit")

        # Commit changes
        run_command(f"git commit -m '{commit_message}'", cwd=path)
        print(f" Changes committed with message: {commit_message}")

        # Push to GitHub
        run_command("git push origin main", cwd=path)
        print(" Changes successfully pushed to GitHub!")
    
    except subprocess.CalledProcessError as e:
        print(f" Error occurred: {e}")
        print("Command output:", e.output if hasattr(e, 'output') else "No output available")



def deploy(path, username, repo_name):
    yml_path = os.path.join(path, '.github', 'workflows', 'deploy.yml')
    directory = os.path.dirname(yml_path)  
    if not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)
    
    with open(yml_path, 'w', encoding='utf-8') as f:
        content = open('myCodes/deploy.yml', 'r')
        f.write(content.read())
        content.close()

    print(f"Deploy yml created at: {yml_path}")

    add_homepage_to_package_json(os.path.join(path, 'package.json'), f"https://{username}.github.io/{repo_name}")
    print("Homepage added to package.json")
    # log_progress("Homepage added to package.json", path)

    setup_repo(username, repo_name, path)
    print("Repository setup complete")
    # log_progress("Repository setup complete", path)

    enable_workflow_permissions(username, repo_name)
    print("Workflow permissions enabled")
    # log_progress("Workflow permissions enabled", path)

    git_init(username, repo_name, path)
    print("Git initialized")
    # log_progress("Git initialized", path)

    pages_url = f"{GITHUB_API_URL}/repos/{username}/{repo_name}/pages"
    pages_payload = {"build_type":"workflow","source": {"branch": "gh-pages", "path": "/"}}
    response = requests.post(pages_url, headers=HEADERS, json=pages_payload)

    if response.status_code in [200, 201, 202]:
        print("GitHub Pages enabled from 'gh-pages' branch")
        # log_progress("GitHub Pages enabled from 'gh-pages' branch", path)
    else:
        print(f"Failed to enable GitHub Pages: {response}")
        # log_progress(f"Failed to enable GitHub Pages: {response}", path)

    print(f"Repository '{repo_name}' created and deployed at: https://{username}.github.io/{repo_name}")
    # log_progress(f"Repository '{repo_name}' created and deployed at: https://{username}.github.io/{repo_name}", path)

    return 'https://{username}.github.io/{repo_name}'



def deploy_(path, username, repo_name):
    yml_path = os.path.join(path, '.github', 'workflows', 'deploy.yml')
    directory = os.path.dirname(yml_path)  
    if not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)
    
    with open(yml_path, 'w', encoding='utf-8') as f:
        content = open('myCodes/deploy.yml', 'r')
        f.write(content.read())
        content.close()

    print(f"Deploy yml created at: {yml_path}")

    add_homepage_to_package_json(os.path.join(path, 'package.json'), f"https://{username}.github.io/{repo_name}")
    print("Homepage added to package.json")
    # log_progress("Homepage added to package.json", path)

    setup_repo(username, repo_name, path)
    print("Repository setup complete")
    # log_progress("Repository setup complete", path)

    enable_workflow_permissions(username, repo_name)
    print("Workflow permissions enabled")
    # log_progress("Workflow permissions enabled", path)

    git_init(username, repo_name, path)
    print("Git initialized")
    # log_progress("Git initialized", path)

    # Wait a bit before configuring Pages
    import time
    time.sleep(5)  # Give GitHub some time to process the gh-pages branch

    # Updated Pages configuration
    pages_url = f"{GITHUB_API_URL}/repos/{username}/{repo_name}/pages"
    pages_payload = {
        "source": {
            "branch": "gh-pages",
            "path": "/"
        }
    }
    
    # First, check if Pages is already configured
    check_response = requests.get(pages_url, headers=HEADERS)
    
    if check_response.status_code == 404:
        # If Pages isn't configured, use POST to create
        response = requests.post(pages_url, headers=HEADERS, json=pages_payload)
    else:
        # If Pages is already configured, use PUT to update
        response = requests.put(pages_url, headers=HEADERS, json=pages_payload)

    if response.status_code in [200, 201, 202]:
        print("GitHub Pages configured to deploy from gh-pages branch")
        # log_progress("GitHub Pages configured to deploy from gh-pages branch", path)
    else:
        print(f"Failed to configure GitHub Pages: {response.text}")
        # log_progress(f"Failed to configure GitHub Pages: {response.text}", path)

    deployment_url = f"https://{username}.github.io/{repo_name}"
    print(f"Repository '{repo_name}' created and deployed at: {deployment_url}")
    # log_progress(f"Repository '{repo_name}' created and deployed at: {deployment_url}", path)

    return deployment_url


if __name__ == "__main__":
    project_path = os.path.join(os.getcwd(), 'calculator')
    username = 'SingletLinkage'
    repo_name = 'pls_hoja_yaar'
    deploy_(project_path, username, repo_name)