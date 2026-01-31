"""
配置文件管理模块
支持从JSON文件加载和保存配置
"""
import json
import os
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import List, Tuple, Optional


@dataclass
class TTSConfig:
    """TTS配置类"""
    # 默认语音音色
    voice: str = 'zh-CN-XiaoxiaoNeural'
    # 默认语速调整（百分比）
    rate: str = '-22%'
    # 默认音量调整（百分比）
    volume: str = '+50%'
    # 默认音调调整
    pitch: str = 'default'
    # 默认并发数
    concurrent: int = 5


@dataclass
class AppConfig:
    """应用配置类"""
    # 默认最大转换记录数
    max_records: int = 500
    # CSV文件编码
    csv_encoding: str = 'utf-8'
    # 结果记录文件
    result_file: str = 'result.md'
    # CSV列名
    answer_text_column: str = 'answer_text'
    file_path_column: str = 'file_path'
    # 音频输出目录
    output_dir: str = 'output_audio'
    # TTS配置
    tts: TTSConfig = field(default_factory=TTSConfig)


class ConfigManager:
    """配置管理器"""
    
    # 可用音色列表（经过测试稳定的音色）
    AVAILABLE_VOICES: List[Tuple[str, str]] = [
        ('zh-CN-XiaoxiaoNeural', '晓晓 - 女声（年轻）'),
        ('zh-CN-YunxiNeural', '云希 - 男声（年轻）'),
        ('zh-CN-XiaoyiNeural', '晓伊 - 女声（儿童）'),
        ('zh-CN-YunjianNeural', '云健 - 男声（新闻）'),
    ]
    
    # 备用音色列表
    FALLBACK_VOICES: List[str] = [
        'zh-CN-XiaoxiaoNeural',
        'zh-CN-YunxiNeural',
        'zh-CN-XiaoyiNeural',
        'zh-CN-YunjianNeural',
    ]
    
    def __init__(self, config_path: str = 'config/settings.json'):
        """
        初始化配置管理器
        
        Args:
            config_path: 配置文件路径
        """
        self.config_path = Path(config_path)
        self._config = AppConfig()
        self._load_config()
    
    def _load_config(self) -> None:
        """从文件加载配置"""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # 加载TTS配置
                tts_data = data.get('tts', {})
                self._config.tts = TTSConfig(**tts_data)
                
                # 加载应用配置
                self._config.max_records = data.get('max_records', 500)
                self._config.csv_encoding = data.get('csv_encoding', 'utf-8')
                self._config.result_file = data.get('result_file', 'result.md')
                self._config.output_dir = data.get('output_dir', 'output_audio')
                
            except Exception as e:
                print(f"加载配置文件失败: {e}，使用默认配置")
    
    def save_config(self) -> None:
        """保存配置到文件"""
        try:
            # 确保目录存在
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            
            data = {
                'max_records': self._config.max_records,
                'csv_encoding': self._config.csv_encoding,
                'result_file': self._config.result_file,
                'output_dir': self._config.output_dir,
                'tts': asdict(self._config.tts)
            }
            
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            print(f"保存配置文件失败: {e}")
    
    @property
    def config(self) -> AppConfig:
        """获取配置对象"""
        return self._config
    
    @property
    def tts(self) -> TTSConfig:
        """获取TTS配置"""
        return self._config.tts
    
    def update_tts_config(self, **kwargs) -> None:
        """
        更新TTS配置
        
        Args:
            **kwargs: 要更新的配置项
        """
        for key, value in kwargs.items():
            if hasattr(self._config.tts, key):
                setattr(self._config.tts, key, value)
        self.save_config()
    
    def update_app_config(self, **kwargs) -> None:
        """
        更新应用配置
        
        Args:
            **kwargs: 要更新的配置项
        """
        for key, value in kwargs.items():
            if hasattr(self._config, key) and key != 'tts':
                setattr(self._config, key, value)
        self.save_config()
    
    def get_voice_display_name(self, voice_id: str) -> str:
        """
        获取音色的显示名称
        
        Args:
            voice_id: 音色ID
            
        Returns:
            str: 显示名称，找不到则返回ID
        """
        for vid, name in self.AVAILABLE_VOICES:
            if vid == voice_id:
                return name
        return voice_id
    
    def print_available_voices(self) -> None:
        """打印所有可用音色"""
        print("\n可用音色列表（中国大陆地区测试通过）：")
        print("-" * 60)
        print("  【推荐音色】")
        for voice_id, voice_name in self.AVAILABLE_VOICES:
            if '推荐' in voice_name:
                print(f"  {voice_id:<35} - {voice_name}")
        print("-" * 60)
        print("  【其他音色】")
        for voice_id, voice_name in self.AVAILABLE_VOICES:
            if '推荐' not in voice_name:
                print(f"  {voice_id:<35} - {voice_name}")
        print("-" * 60)
        print("\n提示：如果选择的音色不可用，程序会自动切换到备用音色")


# 全局配置管理器实例
_config_manager: Optional[ConfigManager] = None


def get_config_manager(config_path: str = 'config/settings.json') -> ConfigManager:
    """
    获取全局配置管理器实例（单例模式）
    
    Args:
        config_path: 配置文件路径
        
    Returns:
        ConfigManager: 配置管理器实例
    """
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager(config_path)
    return _config_manager
