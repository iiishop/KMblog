import os
import json
from datetime import datetime
from utility import parse_markdown_metadata, read_markdowns, find_first_image

class Command:
    description = "Base command class"

    def execute(self):
        raise NotImplementedError("You should implement this method.")

class ShowPostsJson(Command):
    description = "Shows the posts directory structure in JSON format."

    def execute(self):
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../'))
        posts_path = os.path.join(base_path, 'src/Posts')
        if not os.path.exists(posts_path):
            raise FileNotFoundError(f"No such file or directory: '{posts_path}'")
        
        result = {}
        markdowns_path = os.path.join(posts_path, 'Markdowns')
        if os.path.exists(markdowns_path):
            result['Markdowns'] = self._convert_to_relative_paths(read_markdowns(markdowns_path))

        directories = [
            file for file in os.listdir(posts_path)
            if os.path.isdir(os.path.join(posts_path, file))
        ]

        for dir_name in directories:
            dir_path = os.path.join(posts_path, dir_name)
            if dir_name not in ['Markdowns', 'Images']:
                sub_result = {}
                markdowns_sub_path = dir_path
                stats = os.stat(dir_path)
                sub_result['date'] = datetime.fromtimestamp(stats.st_ctime).strftime('%Y-%m-%d')
                if os.path.exists(markdowns_sub_path):
                    sub_result['Markdowns'] = self._convert_to_relative_paths(read_markdowns(markdowns_sub_path))

                image = find_first_image(dir_path)
                if image:
                    sub_result['image'] = self._convert_to_relative_path(image)

                result[dir_name] = sub_result

        return result

    def _convert_to_relative_paths(self, paths, base_path='/src'):
        return [self._convert_to_relative_path(path, base_path) for path in paths]

    def _convert_to_relative_path(self, path, base_path='/src'):
        return base_path + path.split(base_path, 1)[1]

class ListCollections(Command):
    description = "Lists all collections in the posts directory."

    def execute(self):
        posts_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../src/Posts'))
        if not os.path.exists(posts_path):
            raise FileNotFoundError(f"No such file or directory: '{posts_path}'")
        
        collections = []
        directories = [
            file for file in os.listdir(posts_path)
            if os.path.isdir(os.path.join(posts_path, file))
        ]

        for dir_name in directories:
            dir_path = os.path.join(posts_path, dir_name)
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

class OutputPostsJson(Command):
    description = "Outputs the posts directory structure to a JSON file."

    def execute(self):
        posts_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../src/Posts'))
        output_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../src/assets/PostDirectory.json'))
        
        show_command = ShowPostsJson()
        posts_directory = show_command.execute()

        # Ensure the output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        with open(output_path, 'w') as json_file:
            json.dump(posts_directory, json_file, indent=2)
        
        return f"Post directory output to {output_path}"

class AddPost(Command):
    description = "Adds a new post with the given name and optional collection."

    def execute(self):
        posts_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../src/Posts'))
        output_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../src/assets/PostDirectory.json'))
        name = input("Enter the name of the new post: ").strip()
        collection = input("Enter the collection name (optional): ").strip() or None

        if not name:
            return "Error: No post name provided."

        # Determine the directory based on whether a collection is provided
        directory = os.path.join(posts_path, 'Markdowns') if not collection else os.path.join(posts_path, collection)
        os.makedirs(directory, exist_ok=True)

        # Generate the file path and metadata
        file_path = os.path.join(directory, f"{name}.md")
        date_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        metadata = f"""---
title: {name}
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
            if overwrite not in ['y', 'yes']:
                return f"Post '{name}' creation aborted."

        # Write the metadata to the file
        with open(file_path, 'w') as file:
            file.write(metadata)
        
        # Output the posts directory structure to a JSON file
        output_command = OutputPostsJson()
        output_result = output_command.execute()
        
        return f"Post '{name}' created at {file_path}\n{output_result}"

class DeletePost(Command):
    description = "Deletes a post with the given name from the optional collection."

    def execute(self):
        posts_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../src/Posts'))
        output_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../src/assets/PostDirectory.json'))
        name = input("Enter the name of the post to delete: ").strip()
        collection = input("Enter the collection name (optional): ").strip() or None

        if not name:
            return "Error: No post name provided."

        # Determine the directory based on whether a collection is provided
        directory = os.path.join(posts_path, 'Markdowns') if not collection else os.path.join(posts_path, collection)
        file_path = os.path.join(directory, f"{name}.md")

        # Check if the file exists
        if not os.path.exists(file_path):
            return f"Error: Post '{name}' does not exist."

        # Get file metadata
        stats = os.stat(file_path)
        creation_date = datetime.fromtimestamp(stats.st_ctime).strftime('%Y-%m-%d %H:%M:%S')
        with open(file_path, 'r') as file:
            content = file.read()
            content_length = len(content)

        # Ask for confirmation
        print(f"Post '{name}' was created on {creation_date} and has {content_length} characters.")
        confirm = input(f"Are you sure you want to delete this post? (Y/N): ").strip().lower()
        if confirm not in ['y', 'yes']:
            return f"Deletion of post '{name}' aborted."

        # Delete the file
        os.remove(file_path)

        # Output the posts directory structure to a JSON file
        output_command = OutputPostsJson()
        output_result = output_command.execute()

        return f"Post '{name}' deleted.\n{output_result}"

class DeleteCollection(Command):
    description = "Deletes a collection and all its posts."

    def execute(self):
        posts_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../src/Posts'))
        output_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../src/assets/PostDirectory.json'))
        collection = input("Enter the name of the collection to delete: ").strip()

        if not collection:
            return "Error: No collection name provided."

        directory = os.path.join(posts_path, collection)

        # Check if the directory exists
        if not os.path.exists(directory) or not os.path.isdir(directory):
            return f"Error: Collection '{collection}' does not exist."

        # List the posts in the collection
        posts = [file for file in os.listdir(directory) if file.endswith('.md')]
        if not posts:
            return f"Error: Collection '{collection}' is empty or contains no posts."

        print(f"Collection '{collection}' contains the following posts:")
        for post in posts:
            print(f" - {post}")

        # Ask for confirmation
        confirm = input(f"Are you sure you want to delete this collection and all its posts? (Y/N): ").strip().lower()
        if confirm not in ['y', 'yes']:
            return f"Deletion of collection '{collection}' aborted."

        # Delete all posts and the directory
        for post in posts:
            os.remove(os.path.join(directory, post))
        os.rmdir(directory)

        # Output the posts directory structure to a JSON file
        output_command = OutputPostsJson()
        output_result = output_command.execute()

        return f"Collection '{collection}' and all its posts have been deleted.\n{output_result}"

class ListAllPosts(Command):
    description = "Lists all posts and collections in the posts directory."

    def execute(self):
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../'))
        posts_path = os.path.join(base_path, 'src/Posts')
        if not os.path.exists(posts_path):
            raise FileNotFoundError(f"No such file or directory: '{posts_path}'")

        formatted_output = []

        # List Markdown files in the root directory
        markdowns_path = os.path.join(posts_path, 'Markdowns')
        if os.path.exists(markdowns_path):
            root_files = [file for file in os.listdir(markdowns_path) if file.endswith('.md')]
            for file in root_files:
                file_path = os.path.join(markdowns_path, file)
                stats = os.stat(file_path)
                creation_date = datetime.fromtimestamp(stats.st_ctime).strftime('%Y-%m-%d')
                metadata = parse_markdown_metadata(file_path)
                title = metadata.get('title', 'Untitled')
                with open(file_path, 'r') as f:
                    content_length = len(f.read())
                formatted_output.append(f"Post: {file} | Title: {title} | Created on: {creation_date} | Characters: {content_length}")

        # List collections and their posts
        directories = [
            file for file in os.listdir(posts_path)
            if os.path.isdir(os.path.join(posts_path, file)) and file not in ['Markdowns', 'Images']
        ]

        for dir_name in directories:
            dir_path = os.path.join(posts_path, dir_name)
            stats = os.stat(dir_path)
            creation_date = datetime.fromtimestamp(stats.st_ctime).strftime('%Y-%m-%d')
            md_files = [file for file in os.listdir(dir_path) if file.endswith('.md')]
            formatted_output.append(f"Collection: {dir_name} | Created on: {creation_date} | Posts: {len(md_files)}")
            for md_file in md_files:
                md_file_path = os.path.join(dir_path, md_file)
                md_stats = os.stat(md_file_path)
                md_creation_date = datetime.fromtimestamp(md_stats.st_ctime).strftime('%Y-%m-%d')
                metadata = parse_markdown_metadata(md_file_path)
                title = metadata.get('title', 'Untitled')
                with open(md_file_path, 'r') as f:
                    content_length = len(f.read())
                formatted_output.append(f"    Post: {md_file} | Title: {title} | Created on: {md_creation_date} | Characters: {content_length}")

        return "\n".join(formatted_output)