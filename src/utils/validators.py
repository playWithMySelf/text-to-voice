"""
验证工具模块
"""
import os
from pathlib import Path
from typing import Tuple


def validate_text(text: str, max_length: int = 5000) -> Tuple[bool, str]:
    """
    验证文本内容
    
    Args:
        text: 要验证的文本
        max_length: 最大长度限制
        
    Returns:
        Tuple[bool, str]: (是否有效, 错误信息)
    """
    if not text:
        return False, "文本内容不能为空"
    
    if not text.strip():
        return False, "文本内容不能全为空格"
    
    if len(text) > max_length:
        return False, f"文本内容过长，最大支持{max_length}个字符"
    
    return True, ""


def validate_csv_file(file_path: str) -> Tuple[bool, str]:
    """
    验证CSV文件
    
    Args:
        file_path: CSV文件路径
        
    Returns:
        Tuple[bool, str]: (是否有效, 错误信息)
    """
    if not file_path:
        return False, "请选择CSV文件"
    
    path = Path(file_path)
    
    if not path.exists():
        return False, f"文件不存在: {file_path}"
    
    if not path.is_file():
        return False, f"路径不是文件: {file_path}"
    
    if path.suffix.lower() != '.csv':
        return False, f"文件格式错误，请选择CSV文件"
    
    if path.stat().st_size == 0:
        return False, "CSV文件为空"
    
    return True, ""


def validate_output_directory(dir_path: str) -> Tuple[bool, str]:
    """
    验证输出目录
    
    Args:
        dir_path: 目录路径
        
    Returns:
        Tuple[bool, str]: (是否有效, 错误信息)
    """
    if not dir_path:
        return False, "输出目录不能为空"
    
    path = Path(dir_path)
    
    # 如果目录已存在，检查是否可写
    if path.exists():
        if not path.is_dir():
            return False, f"路径不是目录: {dir_path}"
        
        if not os.access(path, os.W_OK):
            return False, f"目录无写入权限: {dir_path}"
    
    return True, ""


def validate_rate(rate: str) -> Tuple[bool, str]:
    """
    验证语速参数
    
    Args:
        rate: 语速字符串，如 "-20%", "+30%"
        
    Returns:
        Tuple[bool, str]: (是否有效, 错误信息)
    """
    if not rate:
        return True, ""  # 允许空值，使用默认值
    
    rate = rate.strip()
    
    # 检查格式
    if not rate.endswith('%'):
        return False, "语速格式错误，应以%结尾，如 -20% 或 +30%"
    
    # 提取数字部分
    try:
        value = int(rate[:-1])
        if value < -100 or value > 100:
            return False, "语速值应在 -100% 到 +100% 之间"
    except ValueError:
        return False, "语速值应为数字，如 -20% 或 +30%"
    
    return True, ""


def validate_volume(volume: str) -> Tuple[bool, str]:
    """
    验证音量参数
    
    Args:
        volume: 音量字符串，如 "+50%", "+100%"
        
    Returns:
        Tuple[bool, str]: (是否有效, 错误信息)
    """
    if not volume:
        return True, ""  # 允许空值，使用默认值
    
    volume = volume.strip()
    
    # 检查格式
    if not volume.endswith('%'):
        return False, "音量格式错误，应以%结尾，如 +50%"
    
    # 提取数字部分
    try:
        value = int(volume[:-1])
        if value < 0 or value > 100:
            return False, "音量值应在 0% 到 +100% 之间"
    except ValueError:
        return False, "音量值应为数字，如 +50%"
    
    return True, ""
