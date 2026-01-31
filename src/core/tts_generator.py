"""
TTS音频生成器 - 使用edge-tts实现快速批量转换
"""
import os
import asyncio
import edge_tts
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Callable
from dataclasses import dataclass


@dataclass
class TTSTask:
    """TTS任务数据类"""
    text: str
    output_path: str
    index: int = 0


@dataclass
class TTSResult:
    """TTS结果数据类"""
    index: int
    output_path: str
    success: bool
    text_preview: str
    error: str = ""


class TTSGenerator:
    """文本转语音生成器 - 基于edge-tts"""
    
    # 备用音色列表（当主音色失败时使用）
    FALLBACK_VOICES = [
        'zh-CN-XiaoxiaoNeural',
        'zh-CN-YunxiNeural',
        'zh-CN-XiaoyiNeural',
        'zh-CN-YunjianNeural',
    ]
    
    def __init__(self, voice: str = "zh-CN-XiaoxiaoNeural", 
                 rate: str = "+0%", 
                 volume: str = "+0%",
                 pitch: str = "default"):
        """
        初始化TTS生成器
        
        Args:
            voice: 语音类型，默认使用中文晓晓语音
            rate: 语速调整，例如 "-20%" 表示慢20%，"+20%" 表示快20%
            volume: 音量调整，例如 "+50%" 表示增加50%音量
            pitch: 音调调整，可选值：x-low, low, medium, high, x-high, default
        """
        self.voice = voice
        self.rate = rate
        self.volume = volume
        self.pitch = pitch
        self._cancelled = False
    
    def _get_text_preview(self, text: str, max_length: int = 50) -> str:
        """获取文本预览"""
        if len(text) <= max_length:
            return text
        return text[:max_length] + "..."
    
    async def generate_audio_async(self, text: str, output_path: str, 
                                   max_retries: int = 3) -> Tuple[bool, str]:
        """
        异步将文本转换为音频文件
        
        Args:
            text: 要转换的文本
            output_path: 输出文件路径
            max_retries: 最大重试次数
            
        Returns:
            tuple[bool, str]: (是否成功, 错误信息)
        """
        if self._cancelled:
            return False, "任务已取消"
        
        # 确保输出目录存在
        output_dir = os.path.dirname(output_path)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        
        last_error = ""
        voices_tried = []
        
        for attempt in range(max_retries):
            if self._cancelled:
                return False, "任务已取消"
            
            # 获取要尝试的音色
            if attempt == 0:
                current_voice = self.voice
            else:
                # 尝试备用音色
                fallback_idx = (attempt - 1) % len(self.FALLBACK_VOICES)
                current_voice = self.FALLBACK_VOICES[fallback_idx]
                if current_voice == self.voice:
                    continue
            
            if current_voice in voices_tried:
                continue
            voices_tried.append(current_voice)
            
            try:
                # 构建参数
                kwargs = {
                    'text': text,
                    'voice': current_voice,
                    'rate': self.rate,
                    'volume': self.volume,
                }
                
                # 只有pitch不是default时才添加
                if self.pitch and self.pitch != 'default':
                    kwargs['pitch'] = self.pitch
                
                # 使用edge-tts生成音频
                communicate = edge_tts.Communicate(**kwargs)
                await communicate.save(output_path)
                
                return True, ""
                
            except Exception as e:
                error_msg = str(e)
                last_error = error_msg
                await asyncio.sleep(0.5)
        
        return False, f"所有音色都失败，最后错误: {last_error}"
    
    def generate_audio(self, text: str, output_path: str) -> TTSResult:
        """
        同步方式将文本转换为音频文件
        
        Args:
            text: 要转换的文本
            output_path: 输出文件路径
            
        Returns:
            TTSResult: 转换结果
        """
        success, error = asyncio.run(self.generate_audio_async(text, output_path))
        return TTSResult(
            index=0,
            output_path=output_path,
            success=success,
            text_preview=self._get_text_preview(text),
            error=error
        )
    
    async def batch_generate(self, tasks: List[TTSTask], 
                            max_concurrent: int = 5,
                            progress_callback: Optional[Callable[[int, int, TTSResult], None]] = None) -> List[TTSResult]:
        """
        批量异步生成音频
        
        Args:
            tasks: 任务列表
            max_concurrent: 最大并发数
            progress_callback: 进度回调函数(当前进度, 总数, 结果)
            
        Returns:
            List[TTSResult]: 每个任务的结果
        """
        semaphore = asyncio.Semaphore(max_concurrent)
        total = len(tasks)
        completed = 0
        
        async def process_task(task: TTSTask) -> TTSResult:
            nonlocal completed
            async with semaphore:
                if self._cancelled:
                    result = TTSResult(
                        index=task.index,
                        output_path=task.output_path,
                        success=False,
                        text_preview=self._get_text_preview(task.text),
                        error="任务已取消"
                    )
                else:
                    success, error = await self.generate_audio_async(task.text, task.output_path)
                    result = TTSResult(
                        index=task.index,
                        output_path=task.output_path,
                        success=success,
                        text_preview=self._get_text_preview(task.text),
                        error=error
                    )
                
                completed += 1
                if progress_callback:
                    progress_callback(completed, total, result)
                
                return result
        
        # 创建所有任务
        coroutines = [process_task(task) for task in tasks]
        
        # 并发执行所有任务
        results = await asyncio.gather(*coroutines, return_exceptions=True)
        
        # 处理异常结果
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append(TTSResult(
                    index=tasks[i].index if i < len(tasks) else i,
                    output_path=tasks[i].output_path if i < len(tasks) else "",
                    success=False,
                    text_preview=self._get_text_preview(tasks[i].text) if i < len(tasks) else "",
                    error=str(result)
                ))
            else:
                processed_results.append(result)
        
        return processed_results
    
    def batch_generate_sync(self, tasks: List[TTSTask], 
                           max_concurrent: int = 5,
                           progress_callback: Optional[Callable[[int, int, TTSResult], None]] = None) -> List[TTSResult]:
        """
        同步方式批量生成音频
        
        Args:
            tasks: 任务列表
            max_concurrent: 最大并发数
            progress_callback: 进度回调函数
            
        Returns:
            List[TTSResult]: 每个任务的结果
        """
        # 在 Windows 上需要设置事件循环策略以避免警告
        if os.name == 'nt':
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        
        return asyncio.run(self.batch_generate(tasks, max_concurrent, progress_callback))
    
    def cancel(self) -> None:
        """取消当前操作"""
        self._cancelled = True
    
    def reset(self) -> None:
        """重置取消状态"""
        self._cancelled = False
    
    def cleanup(self) -> None:
        """清理资源"""
        pass
