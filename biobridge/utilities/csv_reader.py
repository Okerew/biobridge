import pandas as pd


class CSVReader:
    def __init__(self, file_path=None):
        self.file_path = file_path
        self.data = None
        if self.file_path:
            self.load_data()

    def load_data(self):
        """Loads data from the CSV file specified by self.file_path."""
        try:
            self.data = pd.read_csv(self.file_path)
        except FileNotFoundError:
            print(f"File {self.file_path} not found.")
            self.data = None
        except pd.errors.EmptyDataError:
            print(f"File {self.file_path} is empty.")
            self.data = None
        except pd.errors.ParserError:
            print(f"File {self.file_path} could not be parsed.")
            self.data = None
        except Exception as e:
            print(f"An error occurred: {e}")
            self.data = None

    def reload_data(self):
        """Reloads data from the CSV file if the path is already set."""
        if self.file_path:
            self.load_data()
        else:
            print("No file path specified to reload data.")

    def set_file_path(self, file_path):
        """Sets the file path and loads data."""
        self.file_path = file_path
        self.load_data()

    def get_data(self):
        """Returns the loaded data."""
        return self.data
