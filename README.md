# AutoMETHic-Web

## Introduction
The **Autonomous Website Builder** is a collaborative multi-agent system that automatically designs, builds, and deploys a fully functional web application based solely on a user's prompt. This system leverages specialized AI agents to handle different aspects of web development, from UI design to deployment.

## Approach
We developed a **5-agent architecture** to tackle this challenge:

- **Orchestrate Agent**: Takes user input, generates a workflow, decides the folder structure and tech stack, and assigns tasks to other agents.
- **Designer Agent**: Designs the frontend (UI/UX) for the website.
- **Developer Agent**: Implements the backend and frontend logic.
- **Debugger Agent**: Identifies and fixes errors in the generated code, iterating until all issues are resolved.
- **Deployment Agent**: Automates the deployment of the final output.

## Features
- Supports **React.js** and **TypeScript** for website generation.
- Automates deployment using **GitHub Actions**.
- Generates a live deployment link as output for the user.

## Technologies Used
- **Python**
- **Agent.ai**
- **GitHub Actions**

## Repository Structure
```
KRACKHACK25/
├── templates/                # HTML templates
├── README.md                 # Project documentation
├── app.py                    # Main application logic
├── app_build_script.py       # Script to build the application
├── catch_error.py            # Error handling logic
├── deploy.yml                # GitHub Actions deployment workflow
├── deploy_script.py          # Automates deployment steps
├── divideWork.py             # Task distribution logic
├── errorhandling.py          # Error debugging logic
├── main.py                   # Entry point of the application
├── sendToAgent.py            # Communication with agents
├── progress_log.txt          # Logs project progress
```

## Prerequisites
Before running the project, ensure you have the following installed:

1. **GitHub CLI**: Install using the command:
   ```sh
   winget install --id GitHub.cli
   ```
2. **Authenticate GitHub CLI**:
   ```sh
   gh auth login
   ```
3. **Login with your GitHub profile** using any of the methods specified (browser method preferred).
4. **Ensure npm and npx are installed** (required for frontend builds). If they are not installed, run the following command:
   ```sh
   npm --version || (echo "Installing npm..." && winget install OpenJS.NodeJS)
   npx --version || (echo "Installing npx..." && npm install -g npx)
   ```

## How to Set Up
1. **Modify `app.py`**: Update the username to match your GitHub username.
   ```python
   USERNAME = "YOUR-USERNAME"
   ```
2. **Create a `.env` file**: This file should contain your **GitHub personal access token** (fine-grained tokens) with the following permissions:
   - **Read access** to: codespaces metadata, metadata, and secrets.
   - **Read and Write access** to: Dependabot alerts, actions, actions variables, administration, attestations API, code, codespaces, codespaces lifecycle admin, codespaces secrets, commit statuses, Dependabot secrets, deployments, discussions, environments, issues, merge queues, pages, pull requests, repository advisories, repository custom properties, repository hooks, secret scanning alerts, security events, and workflows.
   
   Example `.env` file:
   ```sh
   TOKEN="YOUR-TOKEN"
   ```

## How to Run the Code
To run the project locally, follow these steps:

1. **Clone the Repository:**
   ```sh
   git clone <repository-url>
   cd KRACKHACK25
   ```

2. **Set Up Virtual Environment (Optional but Recommended):**
   ```sh
   python -m venv venv
   source venv/bin/activate  # On macOS/Linux
   venv\Scripts\activate     # On Windows
   ```

3. **Install Dependencies:**
   ```sh
   pip install -r requirements.txt
   ```

4. **Run the Application:**
   ```sh
   python app.py
   ```

5. **Deployment:**
   The deployment is automated using **GitHub Actions**. Once the code is pushed to GitHub, the `deploy.yml` script will trigger the deployment process, generating a live link for the deployed website.

## Contribution
Feel free to open issues or submit pull requests to improve the system. Ensure all contributions align with the repository structure and guidelines.

## License
This project is open-source and available under the MIT License.

