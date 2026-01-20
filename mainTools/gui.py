import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import importlib
import inspect
from commands import Command


class BlogToolGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("KMBlog 管理工具")
        self.root.geometry("900x700")

        # 加载所有命令
        self.commands = self.get_commands()

        # 创建主布局
        self.create_widgets()

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
        # 顶部标题
        title_label = tk.Label(
            self.root,
            text="KMBlog 管理工具",
            font=("微软雅黑", 16, "bold"),
            bg="#2C3E50",
            fg="white",
            pady=10
        )
        title_label.pack(fill=tk.X)

        # 主容器
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 左侧：命令按钮区域
        left_frame = ttk.LabelFrame(main_frame, text="命令列表", padding="10")
        left_frame.grid(row=0, column=0, sticky=(
            tk.W, tk.E, tk.N, tk.S), padx=(0, 5))

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

            # 命令描述
            desc = ttk.Label(
                btn_frame,
                text=cmd_class.description,
                wraplength=200,
                font=("微软雅黑", 8)
            )
            desc.pack(side=tk.LEFT, padx=10)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 右侧：输出区域
        right_frame = ttk.LabelFrame(main_frame, text="输出结果", padding="10")
        right_frame.grid(row=0, column=1, sticky=(
            tk.W, tk.E, tk.N, tk.S), padx=(5, 0))

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
        input_frame = ttk.LabelFrame(main_frame, text="输入参数", padding="10")
        input_frame.grid(row=1, column=0, columnspan=2,
                         sticky=(tk.W, tk.E), pady=(10, 0))

        # 文章名称
        ttk.Label(input_frame, text="文章名称:").grid(
            row=0, column=0, sticky=tk.W, pady=5)
        self.post_name_entry = ttk.Entry(input_frame, width=30)
        self.post_name_entry.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)

        # 合集名称
        ttk.Label(input_frame, text="合集名称:").grid(
            row=0, column=2, sticky=tk.W, pady=5)
        self.collection_entry = ttk.Entry(input_frame, width=30)
        self.collection_entry.grid(
            row=0, column=3, sticky=tk.W, padx=5, pady=5)

        # 清空按钮
        clear_btn = ttk.Button(
            input_frame,
            text="清空输出",
            command=self.clear_output
        )
        clear_btn.grid(row=0, column=4, padx=5)

        # 配置网格权重
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=2)
        main_frame.rowconfigure(0, weight=1)

    def execute_command(self, command_name):
        """执行指定的命令"""
        self.append_output(f"\n{'='*50}\n执行命令: {command_name}\n{'='*50}\n")

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
            self.append_output(f"错误: {str(e)}\n", "error")
            messagebox.showerror("执行错误", f"执行 {command_name} 时出错:\n{str(e)}")

    def execute_post_command(self, command_class, command_name):
        """执行文章相关命令（AddPost或DeletePost）"""
        post_name = self.post_name_entry.get().strip()
        collection = self.collection_entry.get().strip() or None

        if not post_name:
            messagebox.showwarning("输入错误", "请输入文章名称！")
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
                "确认删除",
                f"确定要删除文章 '{post_name}' 吗？"
            )
            if not confirm:
                self.append_output("操作已取消\n")
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
            messagebox.showwarning("输入错误", "请输入合集名称！")
            return

        confirm = messagebox.askyesno(
            "确认删除",
            f"确定要删除合集 '{collection}' 及其所有文章吗？"
        )
        if not confirm:
            self.append_output("操作已取消\n")
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

        self.append_output(f"\n结果:\n{result_str}\n")

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
