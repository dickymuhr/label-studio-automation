import requests
from dotenv import load_dotenv
import os

class LabelStudio:
    def __init__(self):
        # Load environment variables
        load_dotenv()
        self.api_key = os.getenv('LABELSTUDIO_API_KEY')
        self.labelstudio_url = os.getenv('LABELSTUDIO_URL')

    def create_project(self, project_name, label_config_path):
        # Load the label configuration from an XML file
        with open(label_config_path, 'r') as file:
            label_config = file.read()

        # Create a new project
        response = requests.post(
            f'{self.labelstudio_url}/api/projects',
            headers={'Authorization': f'Token {self.api_key}'},
            json={'title': project_name, 'label_config': label_config}
        )

        print("Create project status:", response.status_code)
        if response.status_code == 201:
            return response.json()['id']  # Return project ID
        else:
            print("Error:", response.text)
            return None

    def import_data(self, project_id, csv_file_path):
        # Import data to the project
        with open(csv_file_path, 'rb') as f:
            response = requests.post(
                f'{self.labelstudio_url}/api/projects/{project_id}/import',
                headers={'Authorization': f'Token {self.api_key}'},
                files={'file': f}
            )

        print("Import data status:", response.status_code)

# Example usage
if __name__ == "__main__":
    ls = LabelStudio()
    project_id = ls.create_project('Test 3', 'label_config.xml')
    if project_id:
        ls.import_data(project_id, 'sample_data.csv')
