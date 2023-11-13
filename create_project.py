import requests
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()


api_key = os.getenv('LABELSTUDIO_API_KEY')
labelstudio_url = os.getenv('LABELSTUDIO_URL')
project_name = 'Test 2'
csv_file_path = 'sample_data.csv'

# Load the label configuration from an XML file
with open('label_config.xml', 'r') as file:
    label_config = file.read()

# Create a new project
project_response = requests.post(
    f'{labelstudio_url}/api/projects',
    headers={'Authorization': f'Token {api_key}'},
    json={'title': project_name, 'label_config': label_config}
)

print("Create project status:",project_response.status_code )
if project_response.status_code == 201:
    # Success - parse JSON
    project_id = project_response.json()['id']

    # Import data to the project
    with open(csv_file_path, 'rb') as f:
        import_response = requests.post(
            f'{labelstudio_url}/api/projects/{project_id}/import',
            headers={'Authorization': f'Token {api_key}'},
            files={'file': f}
        )

    print("Import data status:",import_response.status_code)
else:
    # Error - print response and exit or handle error
    print("Error:", project_response.text)
    exit()



