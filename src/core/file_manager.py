"""
文件管理器 - 处理文件路径相关逻辑
"""
import os
from pathlib import Path
from typing import Optional, Tuple


class FileManager:
    """文件管理器"""
    
    @staticmethod
    def process_output_path(original_file_path: str, index: int, 
                           default_output_dir: str = "output_audio") -> str:
        """
        处理文件路径，将原始路径转换为输出路径
        保持原文件的扩展名格式（.m4a -> .m4a, .mp3 -> .mp3）
        
        Args:
            original_file_path: CSV中的原始文件路径
            index: 记录序号
            default_output_dir: 默认输出目录
            
        Returns:
            str: 处理后的输出路径
        """
        if not original_file_path:
            return os.path.join(default_output_dir, f"audio_{index:04d}.mp3")
        
        # 处理路径：去掉开头的/
        processed_path = original_file_path
        if processed_path.startswith('/'):
            processed_path = processed_path[1:]
        
        # 获取文件名（不含扩展名），保持原文件名不变（包括空格）
        base_name = Path(processed_path).stem
        
        # 获取原始扩展名（保持原格式）
        original_suffix = Path(processed_path).suffix
        if not original_suffix:
            original_suffix = '.mp3'
        
        # 获取目录部分
        dir_part = str(Path(processed_path).parent)
        
        # 构建新的文件名（保持原扩展名）
        output_filename = f"{base_name}{original_suffix}"
        
        # 完整输出路径
        return os.path.join('.', dir_part, output_filename)
    
    @staticmethod
    def ensure_dir(file_path: str) -> None:
        """
        确保文件所在目录存在
        
        Args:
            file_path: 文件路径
        """
        directory = os.path.dirname(file_path)
        if directory:
            os.makedirs(directory, exist_ok=True)
    
    @staticmethod
    def get_unique_filename(file_path: str) -> str:
        """
        获取唯一的文件名（如果文件已存在则添加序号）
        
        Args:
            file_path: 原始文件路径
            
        Returns:
            str: 唯一的文件路径
        """
        if not os.path.exists(file_path):
            return file_path
        
        path = Path(file_path)
        stem = path.stem
        suffix = path.suffix
        parent = path.parent
        
        counter = 1
        while True:
            new_name = f"{stem}_{counter:03d}{suffix}"
            new_path = parent / new_name
            if not new_path.exists():
                return str(new_path)
            counter += 1
    
    @staticmethod
    def validate_output_path(file_path: str) -> Tuple[bool, str]:
        """
        验证输出路径是否有效
        
        Args:
            file_path: 文件路径
            
        Returns:
            tuple[bool, str]: (是否有效, 错误信息)
        """
        try:
            path = Path(file_path)
            
            # 检查是否是绝对路径
            if path.is_absolute():
                # 检查父目录是否可写
                parent = path.parent
                if parent.exists() and not os.access(parent, os.W_OK):
                    return False, f"目录无写入权限: {parent}"
            
            # 检查文件名是否有效
            if not path.name or path.name in ['.', '..']:
                return False, "无效的文件名"
            
            # 检查扩展名
            valid_extensions = ['.mp3', '.m4a', '.wav', '.ogg', '.flac']
            if path.suffix.lower() not in valid_extensions:
                return False, f"不支持的音频格式，请使用: {', '.join(valid_extensions)}"
            
            return True, ""
            
        except Exception as e:
            return False, f"路径验证失败: {e}"
    
    @staticmethod
    def open_folder(file_path: str) -> bool:
        """
        打开文件所在文件夹
        
        Args:
            file_path: 文件路径
            
        Returns:
            bool: 是否成功打开
        """
        try:
            import subprocess
            import platform
            
            # 获取文件夹路径
            if os.path.isdir(file_path):
                folder_path = file_path
            else:
                folder_path = os.path.dirname(file_path)
            
            # 如果路径为空，使用当前目录
            if not folder_path:
                folder_path = os.getcwd()
            
            # 转换为绝对路径
            folder_path = os.path.abspath(folder_path)
            
            # 确保目录存在
            if not os.path.exists(folder_path):
                try:
                    os.makedirs(folder_path, exist_ok=True)
                except Exception:
                    return False
            
            # 使用explorer /select可以打开并选中文件，但这里只打开文件夹
            if platform.system() == 'Windows':
                # 使用start命令更可靠
                subprocess.Popen(f'explorer "{folder_path}"', shell=True)
            elif platform.system() == 'Darwin':  # macOS
                subprocess.Popen(['open', folder_path])
            else:  # Linux
                subprocess.Popen(['xdg-open', folder_path])
            
            return True
            
        except Exception as e:
            print(f"打开文件夹失败: {e}")
            return False
