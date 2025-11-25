import json
import os
from datetime import datetime
from typing import Any


class DB:
    def __init__(self, name, verbose=True, indent=False):
        """
        Initialize a new instance of the DB class.

        This constructor sets up the database file, and creates it if it does not exist.

        Args:
            name (str): The base name of the database file (without extension).
            verbose (bool, optional): If True, prints messages about database operations. Defaults to True.
            indent (bool, optional): If True, the JSON data will be pretty-printed with indents. Defaults to False.
        """

        self.name = name + ".db.json"
        self.verbose = verbose
        self.indent = indent
        if not os.path.isfile(os.path.join(os.path.dirname(__file__), "..", "json", self.name)):
            with open(os.path.join(os.path.dirname(__file__), "..", "json", self.name), "w", encoding="utf-8") as file:
                json.dump({}, file)
        print(f"[{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}] DB created at " + self.name)

    def get(self, name) -> Any:
        """
        Retrieves a value from the database.

        Args:
            name (str): The name of the key to retrieve.

        Returns:
            Any: The value associated with the given key, or None if the key does not exist.
        """
        with open(os.path.join(os.path.dirname(__file__), "..", "json", self.name), "r", encoding="utf-8") as file:
            data = json.loads(file.read())
        try:
            result = data[name]
            return result
        except Exception:
            print(f"[{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}] ERROR : No [{name}] in the database")
            return None

    def print(self):
        """
        Prints all the data stored in the database.

        This function reads the database file and prints out all the key-value pairs in the format "key -> value".
        """
        with open(os.path.join(os.path.dirname(__file__), "..", "json", self.name), "r", encoding="utf-8") as file:
            data = json.loads(file.read())
        for key in data:
            print(f"{key} -> {data[key]}")

    def modify(self, name, value):
        """
        Modifies a value in the database.

        If the key exists, the associated value is updated with the given value.
        If the key does not exist, the key-value pair is added to the database.

        Args:
            name (str): The name of the key to modify.
            value (Any): The new value to associate with the given key.
        """
        with open(os.path.join(os.path.dirname(__file__), "..", "json", self.name), "r", encoding="utf-8") as file:
            data = json.loads(file.read())
        if self.match(name):
            data[name] = value
            with open(os.path.join(os.path.dirname(__file__), "..", "json", self.name), "w", encoding="utf-8") as file:
                json.dump(data, file, indent=4 if self.indent else None)
            if self.verbose:
                print(
                    f"[{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}] [{self.name}] The data {name} has been modified successfully"
                )
        else:
            self.add(name, value)
            if self.verbose:
                print(
                    f"[{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}] [{self.name}] The data {name} has been added successfully"
                )

    def remove(self, name):
        """
        Removes a key-value pair from the database.

        If the key exists, it is removed from the database and the associated value is lost.
        If the key does not exist, an error message is printed and nothing is done.

        Args:
            name (str): The name of the key to remove.
        """
        with open(os.path.join(os.path.dirname(__file__), "..", "json", self.name), "r", encoding="utf-8") as file:
            data = json.loads(file.read())
        if self.match(name):
            del data[name]
            with open(os.path.join(os.path.dirname(__file__), "..", "json", self.name), "w", encoding="utf-8") as file:
                json.dump(data, file, indent=4 if self.indent else None)
            if self.verbose:
                print(
                    f"[{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}] [{self.name}] The data {name} has been removed successfully"
                )
        else:
            print(
                f"[{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}] [{self.name}] ERROR : No ["
                + name
                + "] in the database"
            )

    def add(self, name, value):
        """
        Adds a key-value pair to the database.

        If the key already exists, an error message is printed and nothing is done.
        If the key does not exist, the key-value pair is added to the database.

        Args:
            name (str): The name of the key to add.
            value (any): The value to associate with the key.
        """
        with open(os.path.join(os.path.dirname(__file__), "..", "json", self.name), "r", encoding="utf-8") as file:
            data = json.loads(file.read())
        if self.match(name):
            print(
                f"[{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}] [{self.name}] ERROR : [{name}] already exist in the database"
            )
        else:
            data.update({name: value})
            with open(os.path.join(os.path.dirname(__file__), "..", "json", self.name), "w", encoding="utf-8") as file:
                json.dump(data, file, indent=4 if self.indent else None)
            if self.verbose:
                print(
                    f"[{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}] [{self.name}] The data ({name} -> {value}) has been added successfully"
                )

    def match(self, name):
        """
        Checks if a key exists in the database.

        Args:
            name (str): The name of the key to check.

        Returns:
            bool: True if the key exists, False otherwise.
        """
        with open(os.path.join(os.path.dirname(__file__), "..", "json", self.name), "r", encoding="utf-8") as file:
            data = json.loads(file.read())
        return name in data
