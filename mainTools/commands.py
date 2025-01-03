import os
import json
from datetime import datetime

class Command:
    description = "Base command class"
    example = "No example available"

    def execute(self):
        raise NotImplementedError("You should implement this method.")

class ReadPostsDirectoryCommand(Command):
    description = "Reads the posts directory and returns its structure."
    example = "ReadPostsDirectoryCommand"

    def __init__(self, posts_path):
        self.posts_path = posts_path

    def execute(self):
        if not os.path.exists(self.posts_path):
            raise FileNotFoundError(f"No such file or directory: '{self.posts_path}'")
        
        result = {}
        markdowns_path = os.path.join(self.posts_path, 'Markdowns')
        if os.path.exists(markdowns_path):
            result['Markdowns'] = self.read_markdowns(markdowns_path)

        directories = [
            file for file in os.listdir(self.posts_path)
            if os.path.isdir(os.path.join(self.posts_path, file))
        ]

        for dir_name in directories:
            dir_path = os.path.join(self.posts_path, dir_name)
            if dir_name not in ['Markdowns', 'Images']:
                sub_result = {}
                markdowns_sub_path = dir_path
                stats = os.stat(dir_path)
                sub_result['date'] = datetime.fromtimestamp(stats.st_ctime).strftime('%Y-%m-%d')
                if os.path.exists(markdowns_sub_path):
                    sub_result['Markdowns'] = self.read_markdowns(markdowns_sub_path)

                image = self.find_first_image(dir_path)
                if image:
                    sub_result['image'] = image

                result[dir_name] = sub_result

        return result

    def read_markdowns(self, dir_path):
        return [
            os.path.join(dir_path, file)
            for file in os.listdir(dir_path)
            if file.endswith('.md')
        ]

    def find_first_image(self, dir_path):
        image_extensions = ['.png', '.jpg', '.jpeg', '.gif']
        for file in os.listdir(dir_path):
            if any(file.endswith(ext) for ext in image_extensions):
                return os.path.join(dir_path, file)
        return None

class ListCollectionsCommand(Command):
    description = "Lists all collections in the posts directory."
    example = "ListCollectionsCommand"

    def __init__(self, posts_path):
        self.posts_path = posts_path

    def execute(self):
        if not os.path.exists(self.posts_path):
            raise FileNotFoundError(f"No such file or directory: '{self.posts_path}'")
        
        collections = []
        directories = [
            file for file in os.listdir(self.posts_path)
            if os.path.isdir(os.path.join(self.posts_path, file))
        ]

        for dir_name in directories:
            dir_path = os.path.join(self.posts_path, dir_name)
            if dir_name not in ['Markdowns', 'Images']:
                stats = os.stat(dir_path)
                creation_date = datetime.fromtimestamp(stats.st_ctime).strftime('%Y-%m-%d')
                article_count = len([file for file in os.listdir(dir_path) if file.endswith('.md')])
                collections.append({
                    'name': dir_name,
                    'creation_date': creation_date,
                    'article_count': article_count
                })

        # Format the output for human reading
        formatted_output = []
        for collection in collections:
            formatted_output.append(
                f"Collection: {collection['name']} | Articles: {collection['article_count']} | Created on: {collection['creation_date']}"
            )
        return "\n".join(formatted_output)

class OutputPostDirectoryCommand(Command):
    description = "Outputs the posts directory structure to a JSON file."
    example = "OutputPostDirectoryCommand"

    def __init__(self, posts_path, output_path):
        self.posts_path = posts_path
        self.output_path = output_path

    def execute(self):
        read_command = ReadPostsDirectoryCommand(self.posts_path)
        posts_directory = read_command.execute()

        # Ensure the output directory exists
        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)

        with open(self.output_path, 'w') as json_file:
            json.dump(posts_directory, json_file, indent=2)
        
        return f"Post directory output to {self.output_path}"

class AddPostCommand(Command):
    description = "Adds a new post with the given name and optional collection."
    example = "AddPostCommand NewPost MyCollection"

    def __init__(self, posts_path, output_path, name=None, collection=None):
        self.posts_path = posts_path
        self.output_path = output_path
        self.name = name
        self.collection = collection

    def execute(self):
        if not self.name:
            return f"Error: No post name provided.\nExample: {self.example}"

        # Determine the directory based on whether a collection is provided
        directory = os.path.join(self.posts_path, 'Markdowns') if not self.collection else os.path.join(self.posts_path, self.collection)
        os.makedirs(directory, exist_ok=True)

        # Generate the file path and metadata
        file_path = os.path.join(directory, f"{self.name}.md")
        date_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        metadata = f"""---
title: {self.name}
date: {date_str}
tags: 
categories: 
pre: 
img: 
---
"""

        # Check if the file already exists
        if os.path.exists(file_path):
            overwrite = input(f"File '{file_path}' already exists. Overwrite? (Y/N): ").strip().lower()
            if overwrite != 'y' and overwrite != 'yes' and overwrite != 'Y':
                return f"Post '{self.name}' creation aborted."

        # Write the metadata to the file
        with open(file_path, 'w') as file:
            file.write(metadata)
        
        # Output the posts directory structure to a JSON file
        output_command = OutputPostDirectoryCommand(self.posts_path, self.output_path)
        output_result = output_command.execute()
        
        return f"Post '{self.name}' created at {file_path}\n{output_result}"