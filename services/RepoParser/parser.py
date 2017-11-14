import config
import io
import json
import repo
import requests
import zipfile


def load(repo_path):
    """
    Public method to obtain lines of code per language in a GitHub repo.
    """
    parser = Parser()
    return parser.get_counts(repo_path)


# Separating the load function from the Parser class makes the API clean
# while making it easy to maintain state.
class Parser:
    def __init__(self):
        self.file_types = self.load_file_types()
        self.repo_data = None
        self.counts = {}
        self.username = config.github['username']
        self.password = config.github['password']

    def load_file_types(self):
        """
        Returns file types while properly opening/closing source file.
        """
        with open('services/RepoParser/file_types.json') as f:
            file_types = json.load(f)
        return file_types

    def get_counts(self, relative_path):
        """
        Launch the process of downloading zip file and parsing files for
        to count lines of code.
        """
        clean_rel_path = repo.validate(relative_path)
        if not clean_rel_path:
            return False
        path = "https://api.github.com/repos/" + clean_rel_path
        self.repo_data = self.get_repo_data(path)
        if 'clone_url' not in self.repo_data:
            return False

        self.count()

        return self.counts


    def get_repo_data(self, url):
        """
        Get repo metadata from GitHub.
        """
        contents = requests.get(url, auth=(self.username, self.password))

        return contents.json()

    def get_zip_file(self, repo_data):
        """
        Download zipfile from GitHub using clone_url in repo_data.
        """
        zip_url = self.repo_data['clone_url'][:-4] + '/archive/master.zip'
        return requests.get(zip_url, auth=(self.username, self.password))

    def count(self):
        """
        Parse through zip files to count lines of code.
        """
        zip_response = self.get_zip_file()
        if not zip_response.ok:
            return False

        with zipfile.ZipFile(io.BytesIO(zip_response.content)) as zip_file:
            for info in zip_file.filelist:
                if info.filename[-1] == '/':
                    continue
                with zip_file.open(info) as byte_file:
                    line_count = sum(1 for _ in byte_file)
                    self.track_line_count(info.filename, line_count)

    def track_line_count(self, file_name, line_count):
        """
        Add line_count for specified file to running tally of line counts.
        """
        file_type = self.get_file_type(file_name)
        if not file_type:
            self.counts['unknown'] = line_count
        elif file_type not in self.counts:
            self.counts[file_type] = line_count
        else:
            self.counts[file_type] += line_count

    def get_file_type(self, file_name):
        """
        Get the file type based on the file type suffix.
        """
        parts = [part.lower() for part in file_name.split('.')]
        if parts[-1] in self.file_types:
            return parts[-1]
        elif len(parts) >= 2 and parts[-2] + '.' + parts[-1] in self.file_types:
            return parts[-2] + '.' + parts[-1]
        else:
            return None
