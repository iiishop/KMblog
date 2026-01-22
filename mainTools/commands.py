import os
import json
import subprocess
import re
import base64
import shutil
from datetime import datetime
from urllib import request, error, parse as urlparse
from utility import parse_markdown_metadata, read_markdowns, find_first_image, read_file_safe
from path_utils import get_base_path, get_posts_path, get_assets_path
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class Command:
    description = "Base command class"

    def execute(self):
        raise NotImplementedError("You should implement this method.")


class CryptoEncryptor:
    """文章加密工具类 - 使用 AES-GCM 加密算法"""

    @staticmethod
    def derive_key(password: str, salt: bytes = None) -> tuple:
        """从密码派生加密密钥"""
        if salt is None:
            salt = os.urandom(16)

        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = kdf.derive(password.encode('utf-8'))
        return key, salt

    @staticmethod
    def encrypt_file(file_path: str, password: str, output_path: str) -> dict:
        """加密文件（只加密文章内容，保留 metadata 明文）

        Args:
            file_path: 源文件路径
            password: 加密密码
            output_path: 输出文件路径

        Returns:
            dict: {'success': bool, 'message': str, 'salt': str, 'nonce': str}
        """
        try:
            # 读取文件内容
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 分离 metadata 和 body
            metadata_regex = r'^---\n([\s\S]*?)\n---\n([\s\S]*)$'
            match = re.search(metadata_regex, content)

            if match:
                metadata_text = match.group(1)
                body_text = match.group(2)
            else:
                # 如果没有 metadata，整个内容作为 body
                metadata_text = ''
                body_text = content

            # 派生密钥
            key, salt = CryptoEncryptor.derive_key(password)

            # 创建 AES-GCM 加密器
            aesgcm = AESGCM(key)
            nonce = os.urandom(12)  # GCM 模式推荐 12 字节

            # 只加密 body 部分
            body_bytes = body_text.encode('utf-8')
            ciphertext = aesgcm.encrypt(nonce, body_bytes, None)

            # 确保输出目录存在
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            # 写入加密文件：metadata（明文）+ 分隔符 + salt + nonce + ciphertext
            with open(output_path, 'w', encoding='utf-8') as f:
                # 写入 metadata（如果存在）
                if metadata_text:
                    f.write('---\n')
                    f.write(metadata_text)
                    f.write('\n---\n')

                # 写入加密标记和加密数据（base64编码）
                f.write('<!-- ENCRYPTED CONTENT -->\n')
                encrypted_data = salt + nonce + ciphertext
                f.write(base64.b64encode(encrypted_data).decode('utf-8'))

            return {
                'success': True,
                'message': f'加密成功: {os.path.basename(file_path)}',
                'salt': base64.b64encode(salt).decode('utf-8'),
                'nonce': base64.b64encode(nonce).decode('utf-8')
            }

        except Exception as e:
            return {
                'success': False,
                'message': f'加密失败: {str(e)}'
            }

    @staticmethod
    def decrypt_file(file_path: str, password: str, output_path: str) -> dict:
        """解密文件（解密文章内容，保留 metadata）

        Args:
            file_path: 加密文件路径
            password: 解密密码
            output_path: 输出文件路径

        Returns:
            dict: {'success': bool, 'message': str}
        """
        try:
            # 读取加密文件
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 分离 metadata 和加密数据
            metadata_regex = r'^---\n([\s\S]*?)\n---\n'
            match = re.search(metadata_regex, content)

            if match:
                metadata_text = match.group(1)
                # 提取加密数据（去掉注释行）
                encrypted_part = content[match.end():]
                encrypted_part = encrypted_part.replace(
                    '<!-- ENCRYPTED CONTENT -->\n', '').strip()
            else:
                metadata_text = ''
                encrypted_part = content.replace(
                    '<!-- ENCRYPTED CONTENT -->\n', '').strip()

            # Base64 解码加密数据
            encrypted_data = base64.b64decode(encrypted_part)

            # 解析加密数据：salt + nonce + ciphertext
            if len(encrypted_data) < 28:
                raise Exception('加密数据格式错误')

            salt = encrypted_data[:16]
            nonce = encrypted_data[16:28]
            ciphertext = encrypted_data[28:]

            # 派生密钥
            key, _ = CryptoEncryptor.derive_key(password, salt)

            # 解密
            aesgcm = AESGCM(key)
            body_bytes = aesgcm.decrypt(nonce, ciphertext, None)
            body_text = body_bytes.decode('utf-8')

            # 确保输出目录存在
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            # 重新组合 metadata 和 body
            with open(output_path, 'w', encoding='utf-8') as f:
                if metadata_text:
                    f.write('---\n')
                    f.write(metadata_text)
                    f.write('\n---\n')
                f.write(body_text)

            return {
                'success': True,
                'message': f'解密成功: {os.path.basename(file_path)}'
            }

        except Exception as e:
            return {
                'success': False,
                'message': f'解密失败: {str(e)}'
            }


class InitBlog(Command):
    description = "Initializes the blog structure with necessary directories and a sample post."

    def execute(self):
        base_path = get_base_path()
        posts_path = get_posts_path()
        markdowns_path = os.path.join(posts_path, 'Markdowns')
        images_path = os.path.join(posts_path, 'Images')

        # Create directories if they don't exist
        os.makedirs(markdowns_path, exist_ok=True)
        os.makedirs(images_path, exist_ok=True)

        # Initialize a new post named 'Helloworld'
        name = "Helloworld"
        collection = None
        directory = markdowns_path
        file_path = os.path.join(directory, f"{name}.md")
        date_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        metadata = f"""---
title: {name}
date: {date_str}
tags: 
- hello world
categories: 
pre: This is a sample post to demonstrate the blog structure.
img: 
---

# Hello KMBlog
"""

        # Write the metadata and content to the file
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(metadata)

        output_command = Generate()
        output_result = output_command.execute()

        return f"Initialized blog structure at {posts_path}\nCreated sample post at {file_path}\n{output_result}"


class ShowPostsJson(Command):
    description = "Shows the posts directory structure in JSON format."

    def execute(self):
        base_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), '../'))
        posts_path = os.path.join(base_path, 'public/Posts')
        if not os.path.exists(posts_path):
            raise FileNotFoundError(
                f"No such file or directory: '{posts_path}'")

        result = {}
        current_id = 1  # 初始化 ID 计数器

        markdowns_path = os.path.join(posts_path, 'Markdowns')
        if (os.path.exists(markdowns_path)):
            result['Markdowns'] = self._convert_to_relative_paths(
                read_markdowns(markdowns_path), current_id)
            current_id += len(result['Markdowns'])

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
                sub_result['date'] = datetime.fromtimestamp(
                    stats.st_ctime).strftime('%Y-%m-%d')
                if os.path.exists(markdowns_sub_path):
                    sub_result['Markdowns'] = self._convert_to_relative_paths(
                        read_markdowns(markdowns_sub_path), current_id)
                    current_id += len(sub_result['Markdowns'])

                image = find_first_image(dir_path)
                if image:
                    sub_result['image'] = self._convert_to_relative_path(image)

                result[dir_name] = sub_result

        return result

    def _convert_to_relative_paths(self, paths, start_id, base_path='/public'):
        return [{'id': start_id + i, 'path': self._convert_to_relative_path(path, base_path)} for i, path in enumerate(paths)]

    def _convert_to_relative_path(self, path, base_path='/public'):
        base_path = get_base_path()
        if path.startswith(base_path):
            relative_path = path[len(base_path):].replace('\\', '/')
            # 移除开头的 /public 前缀（因为 Vite 会自动将 public 文件夹映射到根路径）
            if relative_path.startswith('/public/'):
                relative_path = relative_path[7:]  # 移除 '/public'
            return relative_path
        else:
            return path.replace('\\', '/')


class ShowTagsJson(Command):
    description = "Shows the tags and their corresponding markdown files in JSON format."

    def execute(self):
        base_path = get_base_path()
        posts_path = get_posts_path()
        if not os.path.exists(posts_path):
            raise FileNotFoundError(
                f"No such file or directory: '{posts_path}'")

        tags_dict = {}

        # List Markdown files in the root directory
        markdowns_path = os.path.join(posts_path, 'Markdowns')
        if os.path.exists(markdowns_path):
            root_files = [file for file in os.listdir(
                markdowns_path) if file.endswith('.md')]
            for file in root_files:
                file_path = os.path.join(markdowns_path, file)
                metadata = parse_markdown_metadata(file_path)

                # Update tags_dict with tags from metadata
                if 'tags' in metadata and metadata['tags']:
                    tags = metadata['tags']
                    if tags is None:
                        continue
                    if isinstance(tags, str):
                        tags = [tags]
                    for tag in tags:
                        if tag not in tags_dict:
                            tags_dict[tag] = []
                        tags_dict[tag].append(
                            self._convert_to_relative_path(file_path, base_path))

        # List collections and their posts
        directories = [
            file for file in os.listdir(posts_path)
            if os.path.isdir(os.path.join(posts_path, file)) and file not in ['Markdowns', 'Images']
        ]

        for dir_name in directories:
            dir_path = os.path.join(posts_path, dir_name)
            md_files = [file for file in os.listdir(
                dir_path) if file.endswith('.md')]
            for md_file in md_files:
                md_file_path = os.path.join(dir_path, md_file)
                metadata = parse_markdown_metadata(md_file_path)

                # Update tags_dict with tags from metadata
                if 'tags' in metadata and metadata['tags']:
                    tags = metadata['tags']
                    if tags is None:
                        continue
                    if isinstance(tags, str):
                        tags = [tags]
                    for tag in tags:
                        if tag not in tags_dict:
                            tags_dict[tag] = []
                        tags_dict[tag].append(
                            self._convert_to_relative_path(md_file_path, base_path))

        return tags_dict

    def _convert_to_relative_path(self, path, base_path='/public'):
        base_path = get_base_path()
        if path.startswith(base_path):
            relative_path = path[len(base_path):].replace('\\', '/')
            # 移除开头的 /public 前缀（因为 Vite 会自动将 public 文件夹映射到根路径）
            if relative_path.startswith('/public/'):
                relative_path = relative_path[7:]  # 移除 '/public'
            return relative_path
        else:
            return path.replace('\\', '/')


class ShowCategoriesJson(Command):
    description = "Shows the categories and their corresponding markdown files in JSON format."

    def execute(self):
        base_path = get_base_path()
        posts_path = get_posts_path()
        if not os.path.exists(posts_path):
            raise FileNotFoundError(
                f"No such file or directory: '{posts_path}'")

        categories_dict = {}

        # List Markdown files in the root directory
        markdowns_path = os.path.join(posts_path, 'Markdowns')
        if os.path.exists(markdowns_path):
            root_files = [os.path.join(markdowns_path, file) for file in os.listdir(
                markdowns_path) if file.endswith('.md')]
            for file_path in root_files:
                self._process_markdown_file(file_path, categories_dict)

        # List collections and their posts
        directories = [
            file for file in os.listdir(posts_path)
            if os.path.isdir(os.path.join(posts_path, file)) and file not in ['Markdowns', 'Images']
        ]

        for dir_name in directories:
            dir_path = os.path.join(posts_path, dir_name)
            md_files = [os.path.join(dir_path, file) for file in os.listdir(
                dir_path) if file.endswith('.md')]
            for md_file_path in md_files:
                self._process_markdown_file(md_file_path, categories_dict)

        return categories_dict

    def _process_markdown_file(self, file_path, categories_dict):
        metadata = parse_markdown_metadata(file_path)
        categories = metadata.get('categories', [])

        if not categories:
            return

        parent_category = categories_dict
        before_category = None
        for category in categories:
            if category not in parent_category:
                parent_category[category] = {
                    'files': [],
                    'childCategories': {}
                }
            before_category = parent_category[category]
            parent_category = parent_category[category]['childCategories']

        # Add the file to the last category in the list
        relative_path = self._convert_to_relative_path(file_path)
        if 'files' not in before_category:
            before_category['files'] = []
        before_category['files'].append(relative_path)

    def _convert_to_relative_path(self, path, base_path='/public'):
        base_path = get_base_path()
        if path.startswith(base_path):
            relative_path = path[len(base_path):].replace('\\', '/')
            # 移除开头的 /public 前缀（因为 Vite 会自动将 public 文件夹映射到根路径）
            if relative_path.startswith('/public/'):
                relative_path = relative_path[7:]  # 移除 '/public'
            return relative_path
        else:
            return path.replace('\\', '/')


class ListCollections(Command):
    description = "Lists all collections in the posts directory."

    def execute(self):
        posts_path = get_posts_path()
        if not os.path.exists(posts_path):
            raise FileNotFoundError(
                f"No such file or directory: '{posts_path}'")

        collections = []
        directories = [
            file for file in os.listdir(posts_path)
            if os.path.isdir(os.path.join(posts_path, file))
        ]

        for dir_name in directories:
            dir_path = os.path.join(posts_path, dir_name)
            if dir_name not in ['Markdowns', 'Images']:
                stats = os.stat(dir_path)
                creation_date = datetime.fromtimestamp(
                    stats.st_ctime).strftime('%Y-%m-%d')
                article_count = len(
                    [file for file in os.listdir(dir_path) if file.endswith('.md')])
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


class Generate(Command):
    description = "Outputs the posts directory structure, tags, and categories to JSON files."

    def _get_crypto_tag(self):
        """从 config.js 中读取 CryptoTag 配置"""
        try:
            base_path = get_base_path()
            config_path = os.path.join(base_path, 'src', 'config.js')
            if not os.path.exists(config_path):
                return None

            with open(config_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 匹配 CryptoTag 配置
            pattern = r"CryptoTag:\s*['\"]([^'\"]*)['\"]"
            match = re.search(pattern, content)
            if match:
                return match.group(1)
            return None
        except:
            return None

    def _collect_crypto_posts(self, crypto_tag):
        """收集包含加密标签的文章"""
        if not crypto_tag:
            return []

        posts_path = get_posts_path()
        crypto_posts = []

        # 检查 Markdowns 目录
        markdowns_path = os.path.join(posts_path, 'Markdowns')
        if os.path.exists(markdowns_path):
            for file in os.listdir(markdowns_path):
                if file.endswith('.md'):
                    file_path = os.path.join(markdowns_path, file)
                    metadata = parse_markdown_metadata(file_path)
                    tags = metadata.get('tags', [])
                    # 确保 tags 是列表且不为 None
                    if tags is None:
                        tags = []
                    elif isinstance(tags, str):
                        tags = [tags]

                    if crypto_tag in tags:
                        relative_path = self._convert_to_relative_path(
                            file_path)
                        crypto_posts.append(relative_path)

        # 检查各个合集目录
        directories = [
            file for file in os.listdir(posts_path)
            if os.path.isdir(os.path.join(posts_path, file)) and file not in ['Markdowns', 'Images']
        ]

        for dir_name in directories:
            dir_path = os.path.join(posts_path, dir_name)
            for file in os.listdir(dir_path):
                if file.endswith('.md'):
                    file_path = os.path.join(dir_path, file)
                    metadata = parse_markdown_metadata(file_path)
                    tags = metadata.get('tags', [])
                    # 确保 tags 是列表且不为 None
                    if tags is None:
                        tags = []
                    elif isinstance(tags, str):
                        tags = [tags]

                    if crypto_tag in tags:
                        relative_path = self._convert_to_relative_path(
                            file_path)
                        crypto_posts.append(relative_path)

        return crypto_posts

    def _convert_to_relative_path(self, path):
        """转换为相对路径"""
        base_path = get_base_path()
        if path.startswith(base_path):
            relative_path = path[len(base_path):].replace('\\', '/')
            # 移除开头的 /public 前缀
            if relative_path.startswith('/public/'):
                relative_path = relative_path[7:]
            return relative_path
        else:
            return path.replace('\\', '/')

    def execute(self):
        posts_path = get_posts_path()
        assets_path = get_assets_path()
        posts_output_path = os.path.join(assets_path, 'PostDirectory.json')
        tags_output_path = os.path.join(assets_path, 'Tags.json')
        categories_output_path = os.path.join(assets_path, 'Categories.json')
        crypto_output_path = os.path.join(assets_path, 'Crypto.json')

        show_posts_command = ShowPostsJson()
        posts_directory = show_posts_command.execute()

        show_tags_command = ShowTagsJson()
        tags_dictionary = show_tags_command.execute()

        show_categories_command = ShowCategoriesJson()
        categories_dictionary = show_categories_command.execute()

        # 收集加密文章
        crypto_tag = self._get_crypto_tag()
        crypto_posts = self._collect_crypto_posts(crypto_tag)

        # Ensure the output directory exists
        os.makedirs(os.path.dirname(posts_output_path), exist_ok=True)
        os.makedirs(os.path.dirname(tags_output_path), exist_ok=True)
        os.makedirs(os.path.dirname(categories_output_path), exist_ok=True)
        os.makedirs(os.path.dirname(crypto_output_path), exist_ok=True)

        # Output posts directory to JSON file
        with open(posts_output_path, 'w', encoding='utf-8') as json_file:
            json.dump(posts_directory, json_file, indent=2, ensure_ascii=False)

        # Output tags dictionary to JSON file
        with open(tags_output_path, 'w', encoding='utf-8') as json_file:
            json.dump(tags_dictionary, json_file, indent=2, ensure_ascii=False)

        # Output categories dictionary to JSON file
        with open(categories_output_path, 'w', encoding='utf-8') as json_file:
            json.dump(categories_dictionary, json_file,
                      indent=2, ensure_ascii=False)

        # Output crypto posts to JSON file with password preservation
        existing_password = ""
        if os.path.exists(crypto_output_path):
            try:
                with open(crypto_output_path, 'r', encoding='utf-8') as json_file:
                    existing_data = json.load(json_file)
                    # 如果现有文件包含 password 字段，保留它
                    if isinstance(existing_data, dict) and 'password' in existing_data:
                        existing_password = existing_data.get('password', '')
            except:
                pass

        # 构建新的 crypto 数据结构
        crypto_data = {
            'password': existing_password,
            'posts': crypto_posts
        }

        with open(crypto_output_path, 'w', encoding='utf-8') as json_file:
            json.dump(crypto_data, json_file, indent=2, ensure_ascii=False)

        # 加密文章
        encrypted_count = 0
        if crypto_posts and existing_password:
            print(f"[Crypto] 开始加密 {len(crypto_posts)} 篇文章...")

            # 创建 cryptoPosts 目录（在项目根目录）
            base_path = get_base_path()
            crypto_posts_dir = os.path.join(base_path, 'cryptoPosts')
            os.makedirs(crypto_posts_dir, exist_ok=True)

            for post_path in crypto_posts:
                # 转换为完整路径
                full_path = os.path.join(
                    base_path, 'public', post_path.lstrip('/'))

                if os.path.exists(full_path):
                    # 生成加密后的文件路径（保持相同的目录结构）
                    relative_path = os.path.relpath(
                        full_path, os.path.join(base_path, 'public', 'Posts'))
                    encrypted_path = os.path.join(
                        crypto_posts_dir, relative_path)

                    # 加密文件
                    result = CryptoEncryptor.encrypt_file(
                        full_path, existing_password, encrypted_path)
                    if result['success']:
                        encrypted_count += 1
                        print(f"[Crypto] ✓ {os.path.basename(full_path)}")
                    else:
                        print(f"[Crypto] ✗ {result['message']}")
                else:
                    print(f"[Crypto] 警告: 文件不存在 {full_path}")

            print(f"[Crypto] 加密完成: {encrypted_count}/{len(crypto_posts)} 篇文章")

        return f"Post directory output to {posts_output_path}\nTags output to {tags_output_path}\nCategories output to {categories_output_path}\nCrypto posts output to {crypto_output_path} ({len(crypto_posts)} posts)\nEncrypted: {encrypted_count} files"


class AddPost(Command):
    description = "Adds a new post with the given name and optional collection."

    def execute(self):
        posts_path = get_posts_path()
        output_path = os.path.join(get_assets_path(), 'PostDirectory.json')
        name = input("Enter the name of the new post: ").strip()
        collection = input(
            "Enter the collection name (optional): ").strip() or None

        if not name:
            return "Error: No post name provided."

        # Determine the directory based on whether a collection is provided
        directory = os.path.join(
            posts_path, 'Markdowns') if not collection else os.path.join(posts_path, collection)
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
            overwrite = input(
                f"File '{file_path}' already exists. Overwrite? (Y/N): ").strip().lower()
            if overwrite not in ['y', 'yes']:
                return f"Post '{name}' creation aborted."

        # Write the metadata to the file
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(metadata)

        # Output the posts directory structure to a JSON file
        output_command = Generate()
        output_result = output_command.execute()

        return f"Post '{name}' created at {file_path}\n{output_result}"


class DeletePost(Command):
    description = "Deletes a post with the given name from the optional collection."

    def execute(self):
        posts_path = get_posts_path()
        output_path = os.path.join(get_assets_path(), 'PostDirectory.json')
        name = input("Enter the name of the post to delete: ").strip()
        collection = input(
            "Enter the collection name (optional): ").strip() or None

        if not name:
            return "Error: No post name provided."

        # Determine the directory based on whether a collection is provided
        directory = os.path.join(
            posts_path, 'Markdowns') if not collection else os.path.join(posts_path, collection)
        file_path = os.path.join(directory, f"{name}.md")

        # Check if the file exists
        if not os.path.exists(file_path):
            return f"Error: Post '{name}' does not exist."

        # Get file metadata
        stats = os.stat(file_path)
        creation_date = datetime.fromtimestamp(
            stats.st_ctime).strftime('%Y-%m-%d %H:%M:%S')
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            content_length = len(content)

        # Ask for confirmation
        print(
            f"Post '{name}' was created on {creation_date} and has {content_length} characters.")
        confirm = input(
            f"Are you sure you want to delete this post? (Y/N): ").strip().lower()
        if confirm not in ['y', 'yes']:
            return f"Deletion of post '{name}' aborted."

        # Delete the file
        os.remove(file_path)

        # Output the posts directory structure to a JSON file
        output_command = Generate()
        output_result = output_command.execute()

        return f"Post '{name}' deleted.\n{output_result}"


class DeleteCollection(Command):
    description = "Deletes a collection and all its posts."

    def execute(self):
        posts_path = get_posts_path()
        output_path = os.path.join(get_assets_path(), 'PostDirectory.json')
        collection = input(
            "Enter the name of the collection to delete: ").strip()

        if not collection:
            return "Error: No collection name provided."

        directory = os.path.join(posts_path, collection)

        # Check if the directory exists
        if not os.path.exists(directory) or not os.path.isdir(directory):
            return f"Error: Collection '{collection}' does not exist."

        # List the posts in the collection
        posts = [file for file in os.listdir(
            directory) if file.endswith('.md')]
        if not posts:
            return f"Error: Collection '{collection}' is empty or contains no posts."

        print(f"Collection '{collection}' contains the following posts:")
        for post in posts:
            print(f" - {post}")

        # Ask for confirmation
        confirm = input(
            f"Are you sure you want to delete this collection and all its posts? (Y/N): ").strip().lower()
        if confirm not in ['y', 'yes']:
            return f"Deletion of collection '{collection}' aborted."

        # Delete all posts and the directory
        for post in posts:
            os.remove(os.path.join(directory, post))
        os.rmdir(directory)

        # Output the posts directory structure to a JSON file
        output_command = Generate()
        output_result = output_command.execute()

        return f"Collection '{collection}' and all its posts have been deleted.\n{output_result}"


class ListAllPosts(Command):
    description = "Lists all posts and collections in the posts directory."

    def execute(self):
        base_path = get_base_path()
        posts_path = get_posts_path()
        if not os.path.exists(posts_path):
            raise FileNotFoundError(
                f"No such file or directory: '{posts_path}'")

        formatted_output = []

        # List Markdown files in the root directory
        markdowns_path = os.path.join(posts_path, 'Markdowns')
        if os.path.exists(markdowns_path):
            root_files = [file for file in os.listdir(
                markdowns_path) if file.endswith('.md')]
            for file in root_files:
                file_path = os.path.join(markdowns_path, file)
                stats = os.stat(file_path)
                creation_date = datetime.fromtimestamp(
                    stats.st_ctime).strftime('%Y-%m-%d')
                metadata = parse_markdown_metadata(file_path)
                title = metadata.get('title', 'Untitled')
                content = read_file_safe(file_path)
                content_length = len(content)
                formatted_output.append(
                    f"Post: {file} | Title: {title} | Created on: {creation_date} | Characters: {content_length}")

        # List collections and their posts
        directories = [
            file for file in os.listdir(posts_path)
            if os.path.isdir(os.path.join(posts_path, file)) and file not in ['Markdowns', 'Images']
        ]

        for dir_name in directories:
            dir_path = os.path.join(posts_path, dir_name)
            stats = os.stat(dir_path)
            creation_date = datetime.fromtimestamp(
                stats.st_ctime).strftime('%Y-%m-%d')
            md_files = [file for file in os.listdir(
                dir_path) if file.endswith('.md')]
            formatted_output.append(
                f"Collection: {dir_name} | Created on: {creation_date} | Posts: {len(md_files)}")
            for md_file in md_files:
                md_file_path = os.path.join(dir_path, md_file)
                md_stats = os.stat(md_file_path)
                md_creation_date = datetime.fromtimestamp(
                    md_stats.st_ctime).strftime('%Y-%m-%d')
                metadata = parse_markdown_metadata(md_file_path)
                title = metadata.get('title', 'Untitled')
                content = read_file_safe(md_file_path)
                content_length = len(content)
                formatted_output.append(
                    f"    Post: {md_file} | Title: {title} | Created on: {md_creation_date} | Characters: {content_length}")

        return "\n".join(formatted_output)


class Build(Command):
    description = "Builds the blog project using npm run build."

    def execute(self):
        base_path = get_base_path()
        crypto_json_path = os.path.join(
            base_path, 'public', 'assets', 'Crypto.json')
        temp_crypto_json_path = os.path.join(base_path, 'Crypto.json')
        crypto_posts_dir = os.path.join(base_path, 'cryptoPosts')
        posts_dir = os.path.join(base_path, 'public', 'Posts')
        backup_dir = os.path.join(base_path, 'Posts_backup_temp')

        crypto_moved = False
        swapped_files = []  # 记录交换的文件信息

        try:
            # Build 前：将 Crypto.json 暂时移出 public 目录，避免密码明文被 push
            if os.path.exists(crypto_json_path):
                shutil.move(crypto_json_path, temp_crypto_json_path)
                crypto_moved = True
                print("[Security] Crypto.json 已暂时移出 public 目录")

            # Build 前：只交换需要加密的文件
            if os.path.exists(crypto_posts_dir):
                print("[Crypto] 开始交换加密文件...")
                os.makedirs(backup_dir, exist_ok=True)

                # 遍历 cryptoPosts 中的所有加密文件
                for root, dirs, files in os.walk(crypto_posts_dir):
                    for file in files:
                        if file.endswith('.md'):
                            # 加密文件路径
                            encrypted_file = os.path.join(root, file)
                            # 相对路径
                            rel_path = os.path.relpath(
                                encrypted_file, crypto_posts_dir)
                            # public/Posts 中对应的明文文件
                            original_file = os.path.join(posts_dir, rel_path)
                            # 备份位置
                            backup_file = os.path.join(backup_dir, rel_path)

                            if os.path.exists(original_file):
                                # 确保备份目录存在
                                os.makedirs(os.path.dirname(
                                    backup_file), exist_ok=True)

                                # 步骤1：将明文文件移动到备份位置
                                shutil.move(original_file, backup_file)

                                # 步骤2：将密文文件复制到 public/Posts
                                shutil.copy2(encrypted_file, original_file)

                                # 记录交换信息
                                swapped_files.append({
                                    'original_file': original_file,
                                    'backup_file': backup_file,
                                    'encrypted_file': encrypted_file
                                })
                                print(f"[Crypto] 交换: {rel_path}")

                print(f"[Crypto] 已交换 {len(swapped_files)} 个加密文件")

            # 在项目根目录执行 npm run build
            # Windows 需要 shell=True 或使用 npm.cmd
            result = subprocess.run(
                'npm run build',
                cwd=base_path,
                capture_output=True,
                text=True,
                shell=True,  # 在 Windows 上需要 shell=True
                encoding='utf-8',  # 指定 UTF-8 编码避免 GBK 解码错误
                errors='replace',  # 遇到无法解码的字符时替换而不是报错
                check=True
            )

            # Build 完成后：将加密文件复制到 dist/Posts
            # 这是必需的，因为 vite 在 build 时可能已经缓存了 public 目录
            if swapped_files:
                print("[Crypto] 将加密文件复制到 dist 目录...")
                dist_posts_dir = os.path.join(base_path, 'dist', 'Posts')

                for swap_info in swapped_files:
                    try:
                        # 计算相对路径
                        rel_path = os.path.relpath(
                            swap_info['encrypted_file'], crypto_posts_dir)
                        # dist 中的目标文件
                        dist_file = os.path.join(dist_posts_dir, rel_path)

                        # 确保目录存在
                        os.makedirs(os.path.dirname(dist_file), exist_ok=True)

                        # 复制加密文件到 dist
                        shutil.copy2(swap_info['encrypted_file'], dist_file)
                        print(f"[Crypto] 复制到 dist: {rel_path}")
                    except Exception as e:
                        print(f"[Crypto] 复制失败 {rel_path}: {e}")

                print(f"[Crypto] 已将 {len(swapped_files)} 个加密文件复制到 dist")

            return f"Build successful!\n{result.stdout}"

        except subprocess.CalledProcessError as e:
            raise Exception(f"Build failed:\n{e.stderr}")
        except FileNotFoundError:
            raise Exception(
                "npm not found. Please ensure Node.js is installed and added to PATH.")
        finally:
            # Build 后：恢复 Crypto.json 到原位置
            if crypto_moved and os.path.exists(temp_crypto_json_path):
                shutil.move(temp_crypto_json_path, crypto_json_path)
                print("[Security] Crypto.json 已恢复到 public/assets 目录")

            # Build 后：恢复被交换的文件
            if swapped_files:
                print("[Crypto] 开始恢复原始文件...")
                for swap_info in swapped_files:
                    try:
                        # 删除 public/Posts 中的密文
                        if os.path.exists(swap_info['original_file']):
                            os.remove(swap_info['original_file'])

                        # 将明文从备份位置移回
                        if os.path.exists(swap_info['backup_file']):
                            shutil.move(
                                swap_info['backup_file'], swap_info['original_file'])
                            print(
                                f"[Crypto] 恢复: {os.path.basename(swap_info['original_file'])}")
                    except Exception as e:
                        print(
                            f"[Crypto] 恢复失败 {os.path.basename(swap_info['original_file'])}: {e}")

                print(f"[Crypto] 已恢复 {len(swapped_files)} 个文件")

                # 清理备份目录
                if os.path.exists(backup_dir):
                    try:
                        shutil.rmtree(backup_dir)
                        print("[Crypto] 已清理临时备份目录")
                    except:
                        pass


class GetConfig(Command):
    description = "Gets the current blog configuration from config.js."

    def execute(self):
        base_path = get_base_path()
        config_path = os.path.join(base_path, 'src', 'config.js')

        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Config file not found: {config_path}")

        with open(config_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 解析配置文件
        config = {}

        # 匹配字符串值（单引号或双引号）- 注意 CryptoTag 也会被这里匹配
        string_pattern = r"(\w+):\s*['\"]([^'\"]*)['\"]"
        for match in re.finditer(string_pattern, content):
            key = match.group(1)
            value = match.group(2)
            config[key] = value

        # 匹配数字值（包括小数）
        number_pattern = r"(\w+):\s*(\d+\.?\d*)\s*[,\/]"
        for match in re.finditer(number_pattern, content):
            key = match.group(1)
            value = match.group(2)
            if key not in config:  # 避免覆盖已匹配的字符串
                config[key] = float(value) if '.' in value else int(value)

        # 匹配布尔值
        bool_pattern = r"(\w+):\s*(true|false)\s*[,\/]"
        for match in re.finditer(bool_pattern, content):
            key = match.group(1)
            config[key] = match.group(2) == 'true'

        # 匹配简单字符串数组（如 InfoListUp）
        list_pattern = r"(\w+List(?:Up|Down|Float)?):\s*\[([^\]]+)\]"
        for match in re.finditer(list_pattern, content):
            key = match.group(1)
            array_content = match.group(2)
            # 提取数组中的字符串
            items = re.findall(r"['\"]([^'\"]+)['\"]", array_content)
            config[key] = items

        # 匹配 Links 数组（对象数组）
        links_pattern = r"Links:\s*\[(.*?)\]"
        links_match = re.search(links_pattern, content, re.DOTALL)
        if links_match:
            links_content = links_match.group(1)
            links = []
            # 匹配每个链接对象（支持尾随逗号）
            link_objects = re.finditer(
                r"\{\s*name:\s*['\"]([^'\"]+)['\"]\s*,\s*url:\s*['\"]([^'\"]+)['\"]\s*,?\s*\}", links_content, re.DOTALL)
            for link_obj in link_objects:
                links.append({
                    'name': link_obj.group(1),
                    'url': link_obj.group(2)
                })
            config['Links'] = links

        return json.dumps(config, indent=2, ensure_ascii=False)


class UpdateConfig(Command):
    description = "Updates the blog configuration in config.js."

    def execute(self, **kwargs):
        base_path = get_base_path()
        config_path = os.path.join(base_path, 'src', 'config.js')

        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Config file not found: {config_path}")

        with open(config_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 更新配置项
        for key, value in kwargs.items():
            # 根据值类型决定如何格式化
            if isinstance(value, list):
                # 处理数组类型
                if key == 'Links':
                    # Links 是对象数组
                    links_str = '[\n'
                    for link in value:
                        links_str += f"        {{\n            name: '{link['name']}',\n            url: '{link['url']}',\n        }},\n"
                    links_str += '    ]'
                    pattern = rf"{key}:\s*\[[^\]]*\]"
                    content = re.sub(
                        pattern, f"{key}: {links_str}", content, flags=re.DOTALL)
                else:
                    # 其他 List 是字符串数组
                    if value:
                        items_str = ',\n        '.join(
                            [f"'{item}'" for item in value])
                        formatted_value = f"[\n        {items_str},\n    ]"
                    else:
                        formatted_value = "[\n    ]"
                    pattern = rf"{key}:\s*\[[^\]]*\]"
                    content = re.sub(
                        pattern, f"{key}: {formatted_value}", content, flags=re.DOTALL)
            elif isinstance(value, str):
                formatted_value = f"'{value}'"
                pattern = rf"\b{key}\s*:\s*[^,\n]+([,\/])"
                replacement = f"{key}: {formatted_value}\\1"
                content = re.sub(pattern, replacement, content)
            elif isinstance(value, bool):
                formatted_value = 'true' if value else 'false'
                pattern = rf"\b{key}\s*:\s*[^,\n]+([,\/])"
                replacement = f"{key}: {formatted_value}\\1"
                content = re.sub(pattern, replacement, content)
            else:
                formatted_value = str(value)
                pattern = rf"\b{key}\s*:\s*[^,\n]+([,\/])"
                replacement = f"{key}: {formatted_value}\\1"
                content = re.sub(pattern, replacement, content)

        # 写回文件
        with open(config_path, 'w', encoding='utf-8') as f:
            f.write(content)

        return f"Configuration updated successfully!"


class UpdateCryptoPassword(Command):
    description = "Updates the password in Crypto.json file."

    def execute(self, password):
        base_path = get_base_path()
        assets_path = get_assets_path()
        crypto_output_path = os.path.join(assets_path, 'Crypto.json')

        # 读取现有的 Crypto.json
        existing_posts = []
        if os.path.exists(crypto_output_path):
            try:
                with open(crypto_output_path, 'r', encoding='utf-8') as json_file:
                    existing_data = json.load(json_file)
                    # 如果现有文件包含 posts 字段，保留它
                    if isinstance(existing_data, dict) and 'posts' in existing_data:
                        existing_posts = existing_data.get('posts', [])
            except:
                pass

        # 构建新的 crypto 数据结构
        crypto_data = {
            'password': password,
            'posts': existing_posts
        }

        # 确保目录存在
        os.makedirs(os.path.dirname(crypto_output_path), exist_ok=True)

        # 写入文件
        with open(crypto_output_path, 'w', encoding='utf-8') as json_file:
            json.dump(crypto_data, json_file, indent=2, ensure_ascii=False)

        return f"Crypto password updated successfully!"


class GetCryptoPassword(Command):
    description = "Gets the password from Crypto.json file."

    def execute(self):
        base_path = get_base_path()
        assets_path = get_assets_path()
        crypto_output_path = os.path.join(assets_path, 'Crypto.json')

        if os.path.exists(crypto_output_path):
            try:
                with open(crypto_output_path, 'r', encoding='utf-8') as json_file:
                    data = json.load(json_file)
                    if isinstance(data, dict):
                        return data.get('password', '')
            except:
                pass
        return ''


class MigrateFromHexo(Command):
    description = "Migrates blog posts from Hexo format to KMBlog format."

    def execute(self):
        """迁移所有 Hexo 格式的文章到 KMBlog 格式"""
        posts_path = get_posts_path()

        if not os.path.exists(posts_path):
            raise FileNotFoundError(f"Posts directory not found: {posts_path}")

        migrated_count = 0
        skipped_count = 0
        error_count = 0

        # 第一步：迁移图片
        print("[迁移] 开始迁移图片...")
        image_migration_result = self._migrate_images(posts_path)
        print(image_migration_result)

        # 第二步：移动 md 文件到第一层（Collection 目录根）
        print("[迁移] 开始整理 markdown 文件...")
        md_migration_result = self._reorganize_markdown_files(posts_path)
        print(md_migration_result)

        # 第三步：递归扫描所有 .md 文件并更新格式
        print("[迁移] 开始迁移 markdown 格式...")
        for root, dirs, files in os.walk(posts_path):
            for file in files:
                if file.endswith('.md'):
                    file_path = os.path.join(root, file)
                    try:
                        if self._migrate_file(file_path):
                            migrated_count += 1
                        else:
                            skipped_count += 1
                    except Exception as e:
                        print(f"[迁移错误] {file}: {e}")
                        error_count += 1

        # 第四步：删除空的第二层文件夹
        print("[迁移] 开始删除原 Hexo 文件夹...")
        cleanup_result = self._cleanup_empty_directories(posts_path)
        print(cleanup_result)

        return f"迁移完成！\n{image_migration_result}\n{md_migration_result}\nMarkdown 格式迁移: {migrated_count} 篇, 跳过: {skipped_count} 篇, 错误: {error_count} 篇\n{cleanup_result}"

    def _migrate_images(self, posts_path: str) -> str:
        """迁移所有图片到 Images 目录，处理名称冲突"""
        images_dir = os.path.join(posts_path, 'Images')
        os.makedirs(images_dir, exist_ok=True)

        image_extensions = {'.jpg', '.jpeg',
                            '.png', '.gif', '.webp', '.svg', '.ico'}
        migrated_count = 0
        image_map = {}  # 记录原始路径和新文件名的映射

        # 遍历所有子目录寻找图片
        for root, dirs, files in os.walk(posts_path):
            # 跳过 Images 目录本身
            if root == images_dir:
                continue

            for file in files:
                if os.path.splitext(file)[1].lower() in image_extensions:
                    # 跳过 /public/Posts 直接子目录下的 image.png 文件
                    if file == 'image.png':
                        rel_path = os.path.relpath(root, posts_path)
                        # 计算深度：只有一级路径分隔符表示直接在 posts_path 下
                        if os.sep not in rel_path:  # 直接在某个子目录下，没有进一步的嵌套
                            print(f"[图片跳过] {file} (集合封面，不迁移)")
                            continue

                    old_path = os.path.join(root, file)

                    # 计算新文件名（处理冲突）
                    new_filename = self._get_unique_filename(
                        images_dir, file, old_path, posts_path)
                    new_path = os.path.join(images_dir, new_filename)

                    try:
                        # 移动文件
                        shutil.move(old_path, new_path)

                        # 记录映射关系（用于更新 md 文件中的图片链接）
                        relative_old_path = os.path.relpath(
                            old_path, posts_path)
                        image_map[file] = new_filename  # 原始文件名 -> 新文件名

                        print(f"[图片迁移] {file} -> {new_filename}")
                        migrated_count += 1
                    except Exception as e:
                        print(f"[图片错误] {file}: {e}")

        # 第二步：更新 md 文件中的图片链接
        self._update_image_links_in_md(posts_path, image_map)

        return f"已迁移 {migrated_count} 张图片到 Images 目录"

    def _reorganize_markdown_files(self, posts_path: str) -> str:
        """将第二层的 md 文件移到第一层（Collection 目录）"""
        reorganized_count = 0

        # 遍历第一层目录（Collection）
        for collection in os.listdir(posts_path):
            collection_path = os.path.join(posts_path, collection)

            # 跳过特殊目录和文件
            if not os.path.isdir(collection_path) or collection in ['Images', 'Markdowns']:
                continue

            # 遍历第二层目录
            for second_level in os.listdir(collection_path):
                second_level_path = os.path.join(collection_path, second_level)

                if not os.path.isdir(second_level_path):
                    continue

                # 查找该目录中的 .md 文件
                for file in os.listdir(second_level_path):
                    if file.endswith('.md'):
                        old_path = os.path.join(second_level_path, file)
                        new_path = os.path.join(collection_path, file)

                        try:
                            # 处理名称冲突
                            if os.path.exists(new_path):
                                # 生成唯一文件名
                                name, ext = os.path.splitext(file)
                                counter = 1
                                while os.path.exists(new_path):
                                    new_path = os.path.join(
                                        collection_path, f"{name}-{counter}{ext}")
                                    counter += 1

                            # 移动文件
                            shutil.move(old_path, new_path)
                            print(f"[文件整理] {file} 已移动到 {collection}/")
                            reorganized_count += 1
                        except Exception as e:
                            print(f"[文件整理错误] {file}: {e}")

        return f"已整理 {reorganized_count} 个 markdown 文件"

    def _cleanup_empty_directories(self, posts_path: str) -> str:
        """删除所有空的第二层文件夹"""
        deleted_count = 0

        # 遍历第一层目录（Collection）
        for collection in os.listdir(posts_path):
            collection_path = os.path.join(posts_path, collection)

            # 跳过特殊目录和文件
            if not os.path.isdir(collection_path) or collection in ['Images', 'Markdowns']:
                continue

            # 遍历第二层目录
            second_level_dirs = []
            for second_level in os.listdir(collection_path):
                second_level_path = os.path.join(collection_path, second_level)

                if os.path.isdir(second_level_path):
                    second_level_dirs.append((second_level, second_level_path))

            # 删除这些第二层目录（无论是否为空）
            for dirname, dirpath in second_level_dirs:
                try:
                    # 递归删除整个目录
                    shutil.rmtree(dirpath)
                    print(f"[删除文件夹] {collection}/{dirname} 已删除")
                    deleted_count += 1
                except Exception as e:
                    print(f"[删除错误] {collection}/{dirname}: {e}")

        return f"已删除 {deleted_count} 个第二层文件夹"

    def _get_unique_filename(self, images_dir: str, filename: str, old_path: str, posts_path: str) -> str:
        """生成唯一的文件名，处理冲突"""
        target_path = os.path.join(images_dir, filename)

        # 如果没有冲突，直接使用原文件名
        if not os.path.exists(target_path):
            return filename

        # 有冲突，生成新名称：在扩展名前添加前缀
        # 前缀格式：Collection-ArticleFolder-
        # 例如：Code-MyArticle-image.png

        try:
            # 获取文章所在的目录信息
            rel_path = os.path.relpath(old_path, posts_path)
            path_parts = rel_path.split(os.sep)

            # path_parts 结构：
            # ['Collection', 'ArticleFolder', 'image.png'] 或
            # ['Markdowns', 'image.png']

            if len(path_parts) >= 3:
                # 有 Collection 和 ArticleFolder
                collection = path_parts[0]
                article_folder = path_parts[1]
                prefix = f"{collection}-{article_folder}-"
            elif len(path_parts) == 2 and path_parts[0] != 'Markdowns':
                # 直接在 Posts 下的某个文件夹中
                prefix = f"{path_parts[0]}-"
            else:
                # Markdowns 目录中的文件，使用较短的前缀
                prefix = "markdown-"

            # 分离文件名和扩展名
            name, ext = os.path.splitext(filename)
            new_filename = prefix + filename

            # 继续检查新名称是否存在冲突
            counter = 1
            while os.path.exists(os.path.join(images_dir, new_filename)):
                new_filename = f"{prefix}{name}-{counter}{ext}"
                counter += 1

            return new_filename
        except Exception as e:
            # 如果处理失败，使用时间戳
            import time
            timestamp = int(time.time())
            name, ext = os.path.splitext(filename)
            return f"{name}-{timestamp}{ext}"

    def _update_image_links_in_md(self, posts_path: str, image_map: dict) -> None:
        """更新 md 文件中的图片链接"""
        if not image_map:
            return

        print("[图片链接] 开始更新 md 文件中的图片链接...")

        updated_count = 0

        # 遍历所有 md 文件
        for root, dirs, files in os.walk(posts_path):
            for file in files:
                if file.endswith('.md'):
                    md_path = os.path.join(root, file)

                    try:
                        with open(md_path, 'r', encoding='utf-8') as f:
                            content = f.read()

                        original_content = content

                        # 更新所有图片链接
                        for old_name, new_name in image_map.items():
                            # 匹配多种图片链接格式
                            # ![alt](./image.png) 或 ![alt](image.png) 或 ![alt](../folder/image.png) 等

                            # 构建正则表达式来匹配包含原文件名的链接
                            patterns = [
                                # 形式 1: ![...](./filename)
                                rf"(\!\[.*?\]\(\.\/[^)]*){re.escape(old_name)}",
                                # 形式 2: ![...](...filename) - 任何包含路径的
                                rf"(\!\[.*?\]\([^)]*\/{re.escape(old_name)})",
                                # 形式 3: ![...](filename) - 直接文件名
                                rf"(\!\[.*?\]\(){re.escape(old_name)}(\))",
                                # 形式 4: 其他可能的引用格式
                                rf"(\[.*?\]\([^)]*\/{re.escape(old_name)})",
                            ]

                            for pattern in patterns:
                                # 匹配并替换
                                matches = list(re.finditer(pattern, content))
                                for match in matches:
                                    if old_name in match.group(0):
                                        # 替换为新的文件名（保持原有的格式）
                                        new_link = match.group(
                                            0).replace(old_name, new_name)
                                        content = content.replace(
                                            match.group(0), new_link, 1)

                        # 如果内容有变化，写回文件
                        if content != original_content:
                            with open(md_path, 'w', encoding='utf-8') as f:
                                f.write(content)
                            print(f"[图片链接] 已更新: {file}")
                            updated_count += 1

                    except Exception as e:
                        print(f"[图片链接错误] {file}: {e}")

        print(f"[图片链接] 已更新 {updated_count} 个 md 文件中的图片链接")

    def _migrate_file(self, file_path: str) -> bool:
        """迁移单个文件，返回是否迁移过"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 提取 metadata 部分
        metadata_match = re.match(r'^---\n([\s\S]*?)\n---\n', content)
        if not metadata_match:
            return False  # 格式不正确

        metadata_text = metadata_match.group(1)
        body = content[metadata_match.end():]

        # 解析 metadata（支持 YAML 格式）
        metadata = self._parse_yaml_metadata(metadata_text)

        # 检查是否已经是 KMBlog 格式（有 pre 或 img 字段）
        if 'pre' in metadata or 'img' in metadata or isinstance(metadata.get('tags'), list) and len(metadata.get('tags', [])) > 0 and isinstance(metadata['tags'][0], dict):
            return False  # 已经是新格式

        # 转换格式
        new_metadata = self._convert_metadata(metadata)

        # 构建新的文件内容
        new_content = self._build_new_content(new_metadata, body)

        # 写回文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)

        return True

    def _parse_yaml_metadata(self, metadata_text: str) -> dict:
        """解析 YAML 格式的 metadata"""
        metadata = {}
        lines = metadata_text.split('\n')
        current_key = None
        current_list = []

        for line in lines:
            line = line.rstrip()

            # 检查是否是键值对
            if ': ' in line and not line.startswith(' '):
                # 保存前一个列表
                if current_key and current_list:
                    metadata[current_key] = current_list
                    current_list = []

                key, value = line.split(': ', 1)
                key = key.strip()
                value = value.strip()

                # 处理数组格式 [a, b, c]
                if value.startswith('[') and value.endswith(']'):
                    array_str = value[1:-1]
                    metadata[key] = [item.strip().strip('\'"')
                                     for item in array_str.split(',')]
                else:
                    metadata[key] = value
                current_key = None

            # 检查是否是列表项 - key:
            elif ': ' in line and not line.startswith(' '):
                # 保存前一个列表
                if current_key and current_list:
                    metadata[current_key] = current_list
                    current_list = []

                key, value = line.split(': ', 1)
                metadata[key.strip()] = value.strip()
                current_key = None

            # 检查是否是 YAML 列表开始
            elif line.endswith(':') and not line.startswith(' '):
                key = line[:-1].strip()
                if current_key and current_list:
                    metadata[current_key] = current_list
                current_key = key
                current_list = []

            # 检查是否是列表项 - 空格开头
            elif line.startswith('- ') and current_key:
                item = line[2:].strip().strip('\'"')
                current_list.append(item)

        # 保存最后一个列表
        if current_key and current_list:
            metadata[current_key] = current_list

        return metadata

    def _convert_metadata(self, metadata: dict) -> dict:
        """转换 metadata 格式"""
        new_metadata = {}

        # 保留基本字段
        for key in ['title', 'date']:
            if key in metadata:
                new_metadata[key] = metadata[key]

        # 转换 tags - 确保是列表格式
        if 'tags' in metadata:
            tags = metadata['tags']
            if isinstance(tags, str):
                # 如果是字符串，尝试解析
                if tags.startswith('[') and tags.endswith(']'):
                    tags = [t.strip().strip('\'"')
                            for t in tags[1:-1].split(',')]
                else:
                    tags = [tags]
            elif not isinstance(tags, list):
                tags = [str(tags)]
            new_metadata['tags'] = tags
        else:
            new_metadata['tags'] = []

        # 转换 categories
        if 'categories' in metadata:
            categories = metadata['categories']
            if isinstance(categories, str):
                if categories.startswith('[') and categories.endswith(']'):
                    categories = [c.strip().strip('\'"')
                                  for c in categories[1:-1].split(',')]
                else:
                    categories = [categories]
            elif not isinstance(categories, list):
                categories = [str(categories)]
            new_metadata['categories'] = categories
        else:
            new_metadata['categories'] = []

        # 添加新字段（如果不存在）
        if 'pre' not in new_metadata:
            new_metadata['pre'] = ''
        if 'img' not in new_metadata:
            new_metadata['img'] = ''

        return new_metadata

    def _build_new_content(self, metadata: dict, body: str) -> str:
        """构建新格式的文件内容"""
        lines = ['---']

        # 写入各字段
        for key in ['title', 'date']:
            if key in metadata:
                lines.append(f"{key}: {metadata[key]}")

        # 写入 tags（列表格式）
        if 'tags' in metadata and metadata['tags']:
            lines.append('tags:')
            for tag in metadata['tags']:
                lines.append(f'- {tag}')
        else:
            lines.append('tags:')

        # 写入 categories（列表格式）
        if 'categories' in metadata and metadata['categories']:
            lines.append('categories:')
            for cat in metadata['categories']:
                lines.append(f'- {cat}')
        else:
            lines.append('categories:')

        # 写入 pre 和 img
        lines.append(f"pre: {metadata.get('pre', '')}")
        lines.append(f"img: {metadata.get('img', '')}")

        lines.append('---')
        lines.append(body)

        return '\n'.join(lines)


# 导入 GitHub 相关命令
