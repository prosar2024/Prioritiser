from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import openai, json, re, os

app = Flask(__name__)
CORS(app)
os.getenv("OPENAI_API_KEY")


def prioritize_tasks(job_description, tasks):
    prompt = f"""
    You are an AI assistant that prioritizes tasks based on job role expectations.
    
    Job Description:
    {job_description}
    
    Tasks to be prioritized:
    {tasks}
    
    Categorize each task into one of the following categories:
    - High Priority: Critical for the job role, must be completed first.
    - Medium Priority: Important but not urgent.
    - Low Priority: Related to the job but not crucial.
    - Unwanted Items: Not relevant to the job role.
    
    Provide a structured JSON response with the following format:
    {{
        "items": [
            {{
                "item": "Task Name",
                "description": "Reason why it is prioritized in this level",
                "priority": "high, medium, low, or unwanted"
            }}
        ]
    }}
    """
    
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a task prioritization assistant."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.5
    )
    
    return response["choices"][0]["message"]["content"]

@app.route('/')
def index():
    return render_template('ui.html')

@app.route('/prioritize', methods=['POST'])
def prioritize():
    try:
        data = request.json
        job_description = data.get("job_description", "")
        tasks = data.get("items", [])
        
        if not job_description or not tasks:
            return jsonify({"error": "Job description and tasks are required."}), 400

        prioritized_result = prioritize_tasks(job_description, tasks)
        response_content = re.sub(r'```json\n?|```', '', prioritized_result).strip()
        return json.loads(response_content)
    
    except Exception as e:
        raise e
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
