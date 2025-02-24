import requests
import json

def callAgentAPI(agent_url, agent_data):
    print("Calling agent: ", agent_url)

    KEY = "enter-your-key-here"
    
    url = "https://api-lr.agent.ai/v1/action/invoke_agent"
    headers = {
        "Authorization": f"Bearer {KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "id": agent_url,
        "user_input": agent_data
    }

    response = requests.post(url, headers=headers, json=data)
    return response.json()


if __name__ == "__main__":
    agent1 = "orchestrate-tech"
    prompt = "build a simple portfolio website"

    agent1_op = callAgentAPI(agent1, prompt)

    json.dump(agent1_op, open('agent_op/agent_output.json', 'w'))