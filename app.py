from flask import Flask, render_template, request, Response
import threading
import time
import os
import json
from sendToAgent import callAgentAPI
from divideWork import run_developer, run_designer, get_App_js
from app_build_script import run_command, log_progress
from errorhandling import debug_build_error
from catch_error import run_command_with_logging
from deploy_script import deploy_

app = Flask(__name__)

# Global variables to store updates
STATUS_UPDATES = []
USERNAME = "SingletLinkage"

def send_update(message):
    """ Append new update message to STATUS_UPDATES. """
    STATUS_UPDATES.append(f"data: {message}\n\n")

def build_project(prompt, project_name):
    """ Runs the long process and updates status dynamically. """
    try:
        send_update(f"Starting project: {project_name}")

        # Setup project path
        PATH = os.path.join(os.getcwd(), project_name)
        os.makedirs(PATH, exist_ok=True)

        # Create React app
        send_update("Initializing React project...")
        run_command(f"npx create-react-app {project_name} --template typescript", log=False)

        # Start orchestration agent
        send_update("Calling Orchestrate Agent...")
        project_manager_agent = "orchestrate-tech"
        agent1_op = callAgentAPI(project_manager_agent, prompt)['response']
        json.dump(agent1_op, open('agent_op/agent_output.json', 'w'))

        # Call design and development agents
        send_update("Running Design Agent...")
        des_files = run_designer(agent1_op, PATH)


        send_update("Running Developer Agent...")
        dev_files = run_developer(agent1_op, PATH)

        send_update("Getting App.js...")
        app_file = get_App_js(agent1_op, PATH)

        # Build loop with retries
        flag = False
        count = 0

        while not flag and count < 10:
            try:
                send_update(f"Build Attempt {count + 1}...")
                run_command_with_logging("npm run build", cwd=PATH)
                send_update("Build Successful!")
                flag = True

                # Deploy the project
                send_update("Deploying the app...")
                deploy_(PATH, USERNAME, project_name)
                send_update("Deployment Complete!")
                send_update(f"Github repo link: https://github.com/{USERNAME}/{project_name}.git")
                send_update(f'Project deployed at: https://{USERNAME}.github.io/{project_name}')
                send_update("Process completed successfully.")
            except Exception as e:
                count += 1
                send_update("Build Failed. Analyzing the error...")

                with open(f"{PATH}/error_log.txt", "r") as f:
                    error_log = f.read()

                file_contents = {}
                all_files = list(set(des_files + dev_files + app_file))
                for file in all_files:
                    with open(PATH + file, "r") as f:
                        file_contents[file] = f.read()

                updated_files = debug_build_error(error_log, file_contents)

                for file_path, content in updated_files.items():
                    send_update(f"Updating: {file_path}")
                    with open(PATH + file_path, "w") as f:
                        f.write(content)

        if count >= 10:
            send_update("Build Failed after 10 attempts. Check logs.")

    except Exception as e:
        send_update(f"Error: {str(e)}")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/start", methods=["POST"])
def start_process():
    """ Start the project building process asynchronously. """
    global STATUS_UPDATES
    STATUS_UPDATES = []  # Reset updates

    import hashlib
    import time

    timestamp = str(int(time.time()))  # Get current timestamp
    hash_suffix = hashlib.sha1(timestamp.encode()).hexdigest()[:6]  # Generate a short hash

    project_name = f"{request.form.get('project_name').lower()}_{hash_suffix}"
    prompt = request.form.get("project_prompt").lower()

    if not project_name or not prompt:
        return "Missing project name or prompt", 400

    # Run process in a new thread
    threading.Thread(target=build_project, args=(prompt, project_name), daemon=True).start()

    return "Process started", 202

@app.route("/stream")
def stream():
    """ SSE endpoint to stream status updates. """
    def event_stream():
        last_update = 0
        while True:
            if len(STATUS_UPDATES) > last_update:
                yield STATUS_UPDATES[last_update]
                last_update += 1
            time.sleep(1)

    return Response(event_stream(), mimetype="text/event-stream")

if __name__ == "__main__":
    app.run(debug=True, threaded=True)
