import requests
import json
import re  # Import regex for extracting JSON

def query_model(prompt, data):
    if prompt == "ad_gen":
        prompt_text = f'''
            Generate 3 ad concepts based on the following criteria:

            Product/Service Overview: {data['Product/Service Overview']}
            Target Audience: {data['Target Audience']}
            Campaign Goal: {data['Campaign Goal']}

            Return the response in the following JSON format:

            {{
                "ads": [
                    {{
                        "title": "Ad Concept 1 Title",
                        "description": "Brief description of Ad Concept 1",
                        "key_message": "Main takeaway of Ad Concept 1"
                    }},
                    {{
                        "title": "Ad Concept 2 Title",
                        "description": "Brief description of Ad Concept 2",
                        "key_message": "Main takeaway of Ad Concept 2"
                    }},
                    {{
                        "title": "Ad Concept 3 Title",
                        "description": "Brief description of Ad Concept 3",
                        "key_message": "Main takeaway of Ad Concept 3"
                    }}
                ]
            }}
        '''

    payload = {
        "model": "llama3.2:latest",
        "prompt": prompt_text,
        "stream": False,
        "system": ""
    }

    response = requests.post("http://localhost:11434/api/generate", json=payload)

    if response.status_code == 200:
        try:
            result = response.json()
            
            # Extract the 'response' field (which contains JSON inside a string)
            response_text = result.get("response", "")

            # Use regex to extract the JSON block inside triple backticks (```)
            json_match = re.search(r"```(.*?)```", response_text, re.DOTALL)

            if json_match:
                json_str = json_match.group(1).strip()  # Extract JSON content
                parsed_json = json.loads(json_str)  # Convert to Python dictionary
                
                print(parsed_json.get("ads", []))
                
                return parsed_json.get("ads", [])  # Return just the ads array

            else:
                print("No JSON block found in API response.")
                return {"error": "No valid JSON found in API response"}

        except json.JSONDecodeError as e:
            print("JSONDecodeError:", e)
            return {"error": "Invalid JSON response from API"}
    else:
        return {"error": f"API Error {response.status_code}: {response.text}"}
