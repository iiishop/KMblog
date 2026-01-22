import os
import shutil
from path_utils import get_posts_path


class MovePost:
    """移动文章到不同合集的命令"""
    description = "Moves a post from one collection to another."

    def execute(self, post_name, source_collection, target_collection):
        """
        移动文章

        Args:
            post_name: 文章名称(不含.md后缀)
            source_collection: 源合集名称('Markdowns'表示无合集)
            target_collection: 目标合集名称('Markdowns'表示无合集)

        Returns:
            dict: {'success': bool, 'message': str}
        """
        posts_path = get_posts_path()

        # 确定源文件路径
        if source_collection == 'Markdowns' or not source_collection:
            source_dir = os.path.join(posts_path, 'Markdowns')
        else:
            source_dir = os.path.join(posts_path, source_collection)

        source_file = os.path.join(source_dir, f"{post_name}.md")

        # 检查源文件是否存在
        if not os.path.exists(source_file):
            return {
                'success': False,
                'message': f"源文件不存在: {source_file}"
            }

        # 如果源和目标相同,不做操作
        if source_collection == target_collection:
            return {
                'success': True,
                'message': "文章已在目标合集中"
            }

        # 确定目标文件路径
        if target_collection == 'Markdowns' or not target_collection:
            target_dir = os.path.join(posts_path, 'Markdowns')
        else:
            target_dir = os.path.join(posts_path, target_collection)

        # 确保目标目录存在
        os.makedirs(target_dir, exist_ok=True)

        target_file = os.path.join(target_dir, f"{post_name}.md")

        # 处理文件名冲突
        if os.path.exists(target_file):
            base_name = post_name
            counter = 1
            while os.path.exists(target_file):
                target_file = os.path.join(
                    target_dir, f"{base_name}_{counter}.md")
                counter += 1

        # 移动文件
        try:
            shutil.move(source_file, target_file)
            return {
                'success': True,
                'message': f"文章已移动: {os.path.basename(target_file)}"
            }
        except Exception as e:
            return {
                'success': False,
                'message': f"移动失败: {str(e)}"
            }
