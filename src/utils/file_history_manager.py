import json
import os
from typing import List, Optional
from pathlib import Path


class FileHistoryManager:
    """文件历史记录管理器"""

    def __init__(self, history_file: str = "file_history.json", max_history: int = 20):
        """
        初始化文件历史记录管理器
        
        Args:
            history_file: 历史记录文件路径
            max_history: 最大历史记录数量
        """
        self.history_file = history_file
        self.max_history = max_history
        self.history: List[str] = []
        self._load_history()

    def _load_history(self) -> None:
        """加载历史记录"""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    self.history = json.load(f)
            except Exception as e:
                print(f"加载历史记录失败: {e}")
                self.history = []
        else:
            self.history = []

    def _save_history(self) -> None:
        """保存历史记录"""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存历史记录失败: {e}")

    def add_file(self, file_path: str) -> None:
        """
        添加文件到历史记录
        
        Args:
            file_path: 文件路径
        """
        if not file_path or not os.path.exists(file_path):
            return

        file_path = os.path.abspath(file_path)

        if file_path in self.history:
            self.history.remove(file_path)

        self.history.insert(0, file_path)

        if len(self.history) > self.max_history:
            self.history = self.history[:self.max_history]

        self._save_history()

    def get_history(self) -> List[str]:
        """
        获取历史记录列表
        
        Returns:
            历史记录文件路径列表
        """
        valid_history = []
        for file_path in self.history:
            if os.path.exists(file_path):
                valid_history.append(file_path)
        
        self.history = valid_history
        self._save_history()
        
        return self.history

    def get_display_names(self) -> List[str]:
        """
        获取历史记录的显示名称列表
        
        Returns:
            显示名称列表（文件名）
        """
        display_names = []
        for file_path in self.get_history():
            file_name = os.path.basename(file_path)
            display_names.append(file_name)
        
        return display_names

    def clear_history(self) -> None:
        """清空历史记录"""
        self.history = []
        self._save_history()

    def remove_file(self, file_path: str) -> None:
        """
        从历史记录中移除文件
        
        Args:
            file_path: 文件路径
        """
        if file_path in self.history:
            self.history.remove(file_path)
            self._save_history()

    def get_file_by_display_name(self, display_name: str) -> Optional[str]:
        """
        根据显示名称获取完整文件路径
        
        Args:
            display_name: 显示名称（文件名）
        
        Returns:
            完整文件路径，如果找不到则返回None
        """
        for file_path in self.history:
            if os.path.basename(file_path) == display_name:
                return file_path
        return None