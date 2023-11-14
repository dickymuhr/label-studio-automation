import requests
from dotenv import load_dotenv
import os

class LabelStudio:
    def __init__(self):
        # Load environment variables
        load_dotenv()
        self.api_key = os.getenv('LABELSTUDIO_API_KEY')
        self.labelstudio_url = os.getenv('LABELSTUDIO_URL')

    def create_project(self, project_name, label_config_path, csv_file_path=None):
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
            project_id = response.json()['id']
            # Import data if csv_file_path is provided
            if csv_file_path:
                self.import_data(project_id, csv_file_path)
            return project_id
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

    def list_projects(self):
        projects = []
        next_page_url = f'{self.labelstudio_url}/api/projects'

        while next_page_url:
            response = requests.get(
                next_page_url,
                headers={'Authorization': f'Token {self.api_key}'},
            )

            if response.status_code == 200:
                data = response.json()
                projects.extend(data['results'])
                next_page_url = data.get('next')  # URL for the next page
            else:
                print(f"Error {response.status_code}: {response.text}")
                return None

        return [{'id': project['id'], 'name': project['title']} for project in projects]


    def delete_all_projects(self):
        projects = self.list_projects()
        if projects is None:
            print("Failed to retrieve projects or no projects to delete.")
            return

        for project in projects:
            project_id = project['id']
            response = requests.delete(
                f'{self.labelstudio_url}/api/projects/{project_id}',
                headers={'Authorization': f'Token {self.api_key}'},
            )

            if response.status_code == 204:
                print(f"Deleted project {project['name']} (ID: {project_id})")
            else:
                print(f"Failed to delete project {project['name']} (ID: {project_id}): {response.text}")

    def create_project_bulk(self, folder, label_config_path):
        dir_path = folder
        dir_list = sorted(os.listdir(dir_path), reverse=True)
        for file in dir_list:
            project_name = file.replace('annotator_', 'Annotation ').replace('.csv', '')
            print(f'Creating {project_name} project and importing data...')
            csv_file_path = os.path.join(dir_path, file)
            self.create_project(project_name, label_config_path, csv_file_path=csv_file_path)

    def export_annotations(self, project_id, export_path, project_name):
        # Export annotations for a specific project
        response = requests.get(
            f'{self.labelstudio_url}/api/projects/{project_id}/export?exportType=CSV',
            headers={'Authorization': f'Token {self.api_key}'}
        )

        if response.status_code == 200:
            filename = f'annotation_{project_name.replace("Annotation ", "").lower()}.csv'
            file_path = os.path.join(export_path, filename)
            with open(file_path, 'wb') as f:
                f.write(response.content)
            print(f"Exported annotations to {file_path}")
        else:
            print(f"Failed to export annotations for project {project_name}: {response.text}")

    def export_all_annotations(self, export_path):
        projects = self.list_projects()
        if not projects:
            print("No projects to export.")
            return

        if not os.path.exists(export_path):
            os.makedirs(export_path)

        for project in projects:
            self.export_annotations(project['id'], export_path, project['name'])



# Example usage
if __name__ == "__main__":
    ls = LabelStudio()
    ### Create Project
    # data_dir = 'dataset'
    # ls.create_project_bulk(data_dir, 'label_config.xml')

    ### Export Annotation
    export_directory = 'annotation'  # Replace with your desired path
    ls.export_all_annotations(export_directory)

    ### Delete Project
    # ls.delete_all_projects()
    # print(f'Any project left: {len(ls.list_projects())}')