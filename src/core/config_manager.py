import yaml
from typing import Dict, Any, Optional
from .interfaces import ConfigManagerInterface


class ConfigManager(ConfigManagerInterface):
    """配置管理器类"""

    def __init__(self, config_path: str = "config.yaml"):
        """初始化配置管理器"""
        self.config_path = config_path
        self.config = self.load_config(config_path)

    def load_config(self, file_path: str) -> Dict[str, Any]:
        """加载配置文件"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)
            return config or {}
        except Exception as e:
            print(f"Error loading config: {e}")
            return {}

    def save_config(self, config: Dict[str, Any], file_path: str) -> None:
        """保存配置文件"""
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
        except Exception as e:
            print(f"Error saving config: {e}")

    def get_config(self, section: Optional[str] = None) -> Dict[str, Any]:
        """获取配置"""
        if section is None:
            return self.config
        return self.config.get(section, {})

    def set_config(self, section: str, key: str, value: Any) -> None:
        """设置配置"""
        if section not in self.config:
            self.config[section] = {}
        self.config[section][key] = value
        # 保存到文件
        self.save_config(self.config, self.config_path)

    def update_config(self, config: Dict[str, Any]) -> None:
        """更新配置"""
        self.config.update(config)
        # 保存到文件
        self.save_config(self.config, self.config_path)

    def get(self, path: str, default: Any = None) -> Any:
        """获取配置值（支持点号路径）"""
        keys = path.split(".")
        value = self.config
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        return value

    def set(self, path: str, value: Any) -> None:
        """设置配置值（支持点号路径）"""
        keys = path.split(".")
        config = self.config
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]
        config[keys[-1]] = value
        # 保存到文件
        self.save_config(self.config, self.config_path)


# 全局配置管理器实例
global_config_manager = ConfigManager()


def get_config_manager() -> ConfigManager:
    """获取全局配置管理器实例"""
    return global_config_manager
