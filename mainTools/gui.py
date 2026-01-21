import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import importlib
import inspect
from commands import Command


class BlogToolGUI:
    # 语言包
    LANGUAGES = {
        'zh': {
            'title': 'KMBlog 管理工具',
            'command_list': '命令列表',
            'output_result': '输出结果',
            'input_params': '输入参数',
            'post_name': '文章名称:',
            'collection_name': '合集名称:',
            'clear_output': '清空输出',
            'execute_command': '执行命令',
            'error': '错误',
            'result': '结果',
            'execute_error': '执行错误',
            'execute_error_msg': '执行 {} 时出错:\n{}',
            'input_error': '输入错误',
            'please_input_post': '请输入文章名称！',
            'please_input_collection': '请输入合集名称！',
            'confirm_delete': '确认删除',
            'confirm_delete_post': '确定要删除文章 \'{}\' 吗？',
            'confirm_delete_collection': '确定要删除合集 \'{}\' 及其所有文章吗？',
            'operation_cancelled': '操作已取消',
            'lang_switch': '切换语言',
            'build_project': '构建项目',
        },
        'en': {
            'title': 'KMBlog Management Tool',
            'command_list': 'Command List',
            'output_result': 'Output',
            'input_params': 'Parameters',
            'post_name': 'Post Name:',
            'collection_name': 'Collection:',
            'clear_output': 'Clear',
            'execute_command': 'Execute',
            'error': 'Error',
            'result': 'Result',
            'execute_error': 'Execution Error',
            'execute_error_msg': 'Error executing {}:\n{}',
            'input_error': 'Input Error',
            'please_input_post': 'Please enter post name!',
            'please_input_collection': 'Please enter collection name!',
            'confirm_delete': 'Confirm Delete',
            'confirm_delete_post': 'Are you sure to delete post \'{}\'?',
            'confirm_delete_collection': 'Are you sure to delete collection \'{}\' and all its posts?',
            'operation_cancelled': 'Operation cancelled',
            'lang_switch': 'Switch Language',
            'build_project': 'Build Project',
        }
    }

    # 命令描述的双语翻译
    COMMAND_DESCRIPTIONS = {
        'zh': {
            'InitBlog': '初始化博客结构，创建必要的目录和示例文章。',
            'ShowPostsJson': '以JSON格式显示文章目录结构。',
            'ShowTagsJson': '以JSON格式显示标签及其对应的markdown文件。',
            'ShowCategoriesJson': '以JSON格式显示分类及其对应的markdown文件。',
            'ListCollections': '列出文章目录中的所有合集。',
            'Generate': '将文章目录结构、标签和分类输出到JSON文件。',
            'AddPost': '添加一个新文章，可选择是否归入合集。',
            'DeletePost': '删除指定名称的文章（可选合集）。',
            'DeleteCollection': '删除一个合集及其所有文章。',
            'ListAllPosts': '列出文章目录中的所有文章和合集。',
            'Build': '使用 npm run build 构建博客项目。',
        },
        'en': {
            'InitBlog': 'Initializes the blog structure with necessary directories and a sample post.',
            'ShowPostsJson': 'Shows the posts directory structure in JSON format.',
            'ShowTagsJson': 'Shows the tags and their corresponding markdown files in JSON format.',
            'ShowCategoriesJson': 'Shows the categories and their corresponding markdown files in JSON format.',
            'ListCollections': 'Lists all collections in the posts directory.',
            'Generate': 'Outputs the posts directory structure, tags, and categories to JSON files.',
            'AddPost': 'Adds a new post with the given name and optional collection.',
            'DeletePost': 'Deletes a post with the given name from the optional collection.',
            'DeleteCollection': 'Deletes a collection and all its posts.',
            'ListAllPosts': 'Lists all posts and collections in the posts directory.',
            'Build': 'Builds the blog project using npm run build.',
            'ListAllPosts': 'Lists all posts and collections in the posts directory.',
        }
    }

    def __init__(self, root):
        self.root = root
        self.current_lang = 'zh'  # 默认中文
        self.root.title(self.t('title'))
        self.root.geometry("900x700")

        # 加载所有命令
        self.commands = self.get_commands()

        # 存储需要更新的组件引用
        self.widgets = {}
        # 存储命令描述标签引用
        self.cmd_desc_labels = {}

        # 创建主布局
        self.create_widgets()

    def t(self, key):
        """获取当前语言的文本"""
        return self.LANGUAGES[self.current_lang].get(key, key)

    def switch_language(self):
        """切换语言"""
        self.current_lang = 'en' if self.current_lang == 'zh' else 'zh'
        self.update_language()

    def update_language(self):
        """更新所有文本为当前语言"""
        self.root.title(self.t('title'))
        self.widgets['title_label'].config(text=self.t('title'))
        self.widgets['left_frame'].config(text=self.t('command_list'))
        self.widgets['right_frame'].config(text=self.t('output_result'))
        self.widgets['input_frame'].config(text=self.t('input_params'))
        self.widgets['post_label'].config(text=self.t('post_name'))
        self.widgets['collection_label'].config(text=self.t('collection_name'))
        self.widgets['clear_btn'].config(text=self.t('clear_output'))
        self.widgets['lang_btn'].config(text=self.t('lang_switch'))

        # 更新命令描述
        for cmd_name, desc_label in self.cmd_desc_labels.items():
            desc_text = self.COMMAND_DESCRIPTIONS[self.current_lang].get(
                cmd_name,
                self.commands[cmd_name].description
            )
            desc_label.config(text=desc_text)

        # 更新命令描述
        for cmd_name, desc_label in self.cmd_desc_labels.items():
            desc_text = self.COMMAND_DESCRIPTIONS[self.current_lang].get(
                cmd_name,
                self.commands[cmd_name].description
            )
            desc_label.config(text=desc_text)

    def get_commands(self):
        """动态获取所有命令类"""
        commands_module = importlib.import_module('commands')
        commands = {}
        for name, obj in inspect.getmembers(commands_module):
            if inspect.isclass(obj) and issubclass(obj, Command) and obj is not Command:
                commands[name] = obj
        return commands

    def create_widgets(self):
        """创建GUI组件"""
        # 顶部标题容器
        title_frame = tk.Frame(self.root, bg="#2C3E50")
        title_frame.pack(fill=tk.X)

        # 顶部标题
        title_label = tk.Label(
            title_frame,
            text=self.t('title'),
            font=("微软雅黑", 16, "bold"),
            bg="#2C3E50",
            fg="white",
            pady=10
        )
        title_label.pack(side=tk.LEFT, padx=20)
        self.widgets['title_label'] = title_label

        # 语言切换按钮
        lang_btn = tk.Button(
            title_frame,
            text=self.t('lang_switch'),
            command=self.switch_language,
            bg="#34495E",
            fg="white",
            font=("微软雅黑", 10),
            relief=tk.FLAT,
            padx=15,
            pady=5,
            cursor="hand2"
        )
        lang_btn.pack(side=tk.RIGHT, padx=20, pady=10)
        self.widgets['lang_btn'] = lang_btn

        # 主容器
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 左侧：命令按钮区域
        left_frame = ttk.LabelFrame(
            main_frame, text=self.t('command_list'), padding="10")
        left_frame.grid(row=0, column=0, sticky=(
            tk.W, tk.E, tk.N, tk.S), padx=(0, 5))
        self.widgets['left_frame'] = left_frame

        # 创建Canvas和滚动条用于命令按钮
        canvas = tk.Canvas(left_frame, width=350)
        scrollbar = ttk.Scrollbar(
            left_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # 添加命令按钮
        for i, (cmd_name, cmd_class) in enumerate(self.commands.items()):
            # 创建按钮框架
            btn_frame = ttk.Frame(scrollable_frame)
            btn_frame.pack(fill=tk.X, pady=5, padx=5)

            # 命令按钮
            btn = ttk.Button(
                btn_frame,
                text=cmd_name,
                command=lambda name=cmd_name: self.execute_command(name),
                width=20
            )
            btn.pack(side=tk.LEFT)

            # 命令描述（使用双语翻译）
            desc_text = self.COMMAND_DESCRIPTIONS[self.current_lang].get(
                cmd_name,
                cmd_class.description
            )
            desc = ttk.Label(
                btn_frame,
                text=desc_text,
                wraplength=200,
                font=("微软雅黑", 8)
            )
            desc.pack(side=tk.LEFT, padx=10)

            # 保存描述标签引用以便后续更新
            self.cmd_desc_labels[cmd_name] = desc

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 右侧：输出区域
        right_frame = ttk.LabelFrame(
            main_frame, text=self.t('output_result'), padding="10")
        right_frame.grid(row=0, column=1, sticky=(
            tk.W, tk.E, tk.N, tk.S), padx=(5, 0))
        self.widgets['right_frame'] = right_frame

        # 输出文本框
        self.output_text = scrolledtext.ScrolledText(
            right_frame,
            wrap=tk.WORD,
            width=50,
            height=30,
            font=("Consolas", 10)
        )
        self.output_text.pack(fill=tk.BOTH, expand=True)

        # 底部：输入区域（用于需要交互的命令）
        input_frame = ttk.LabelFrame(
            main_frame, text=self.t('input_params'), padding="10")
        input_frame.grid(row=1, column=0, columnspan=2,
                         sticky=(tk.W, tk.E), pady=(10, 0))
        self.widgets['input_frame'] = input_frame

        # 文章名称
        post_label = ttk.Label(input_frame, text=self.t('post_name'))
        post_label.grid(row=0, column=0, sticky=tk.W, pady=5)
        self.widgets['post_label'] = post_label
        self.post_name_entry = ttk.Entry(input_frame, width=30)
        self.post_name_entry.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)

        # 合集名称
        collection_label = ttk.Label(
            input_frame, text=self.t('collection_name'))
        collection_label.grid(row=0, column=2, sticky=tk.W, pady=5)
        self.widgets['collection_label'] = collection_label
        self.collection_entry = ttk.Entry(input_frame, width=30)
        self.collection_entry.grid(
            row=0, column=3, sticky=tk.W, padx=5, pady=5)

        # 清空按钮
        clear_btn = ttk.Button(
            input_frame,
            text=self.t('clear_output'),
            command=self.clear_output
        )
        clear_btn.grid(row=0, column=4, padx=5)
        self.widgets['clear_btn'] = clear_btn

        # 配置网格权重
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=2)
        main_frame.rowconfigure(0, weight=1)

    def execute_command(self, command_name):
        """执行指定的命令"""
        self.append_output(
            f"\n{'='*50}\n{self.t('execute_command')}: {command_name}\n{'='*50}\n")

        try:
            command_class = self.commands[command_name]

            # 特殊处理需要输入的命令
            if command_name in ['AddPost', 'DeletePost']:
                self.execute_post_command(command_class, command_name)
            elif command_name == 'DeleteCollection':
                self.execute_delete_collection_command(command_class)
            else:
                # 直接执行不需要输入的命令
                command_instance = command_class()
                result = command_instance.execute()
                self.display_result(result)

        except Exception as e:
            self.append_output(f"{self.t('error')}: {str(e)}\n", "error")
            messagebox.showerror(self.t('execute_error'), self.t(
                'execute_error_msg').format(command_name, str(e)))

    def execute_post_command(self, command_class, command_name):
        """执行文章相关命令（AddPost或DeletePost）"""
        post_name = self.post_name_entry.get().strip()
        collection = self.collection_entry.get().strip() or None

        if not post_name:
            messagebox.showwarning(self.t('input_error'),
                                   self.t('please_input_post'))
            return

        # 创建一个模拟的输入函数
        inputs = [post_name, collection or '']
        input_index = [0]

        def mock_input(prompt):
            if input_index[0] < len(inputs):
                value = inputs[input_index[0]]
                input_index[0] += 1
                self.append_output(f"{prompt}{value}\n")
                return value
            return ''

        # 如果是删除命令，需要确认
        if command_name == 'DeletePost':
            confirm = messagebox.askyesno(
                self.t('confirm_delete'),
                self.t('confirm_delete_post').format(post_name)
            )
            if not confirm:
                self.append_output(self.t('operation_cancelled') + "\n")
                return

            # 添加确认输入
            inputs.append('y')

        # 替换内置的input函数
        import builtins
        original_input = builtins.input
        builtins.input = mock_input

        try:
            command_instance = command_class()
            result = command_instance.execute()
            self.display_result(result)

            # 清空输入框
            self.post_name_entry.delete(0, tk.END)
            self.collection_entry.delete(0, tk.END)

        finally:
            # 恢复原始的input函数
            builtins.input = original_input

    def execute_delete_collection_command(self, command_class):
        """执行删除合集命令"""
        collection = self.collection_entry.get().strip()

        if not collection:
            messagebox.showwarning(self.t('input_error'),
                                   self.t('please_input_collection'))
            return

        confirm = messagebox.askyesno(
            self.t('confirm_delete'),
            self.t('confirm_delete_collection').format(collection)
        )
        if not confirm:
            self.append_output(self.t('operation_cancelled') + "\n")
            return

        # 创建模拟输入
        inputs = [collection, 'y']
        input_index = [0]

        def mock_input(prompt):
            if input_index[0] < len(inputs):
                value = inputs[input_index[0]]
                input_index[0] += 1
                self.append_output(f"{prompt}{value}\n")
                return value
            return ''

        import builtins
        original_input = builtins.input
        original_print = builtins.print

        # 也拦截print输出
        def mock_print(*args, **kwargs):
            output = ' '.join(str(arg) for arg in args)
            self.append_output(output + '\n')

        builtins.input = mock_input
        builtins.print = mock_print

        try:
            command_instance = command_class()
            result = command_instance.execute()
            self.display_result(result)

            # 清空输入框
            self.collection_entry.delete(0, tk.END)

        finally:
            builtins.input = original_input
            builtins.print = original_print

    def display_result(self, result):
        """显示命令执行结果"""
        if isinstance(result, dict):
            import json
            result_str = json.dumps(result, indent=2, ensure_ascii=False)
        else:
            result_str = str(result)

        self.append_output(f"\n{self.t('result')}:\n{result_str}\n")

    def append_output(self, text, tag=None):
        """添加文本到输出区域"""
        self.output_text.insert(tk.END, text)
        if tag == "error":
            # 可以添加颜色标记
            pass
        self.output_text.see(tk.END)
        self.root.update_idletasks()

    def clear_output(self):
        """清空输出区域"""
        self.output_text.delete(1.0, tk.END)


def main():
    root = tk.Tk()
    app = BlogToolGUI(root)
    root.mainloop()


if __name__ == '__main__':
    main()
