from typing import Dict, Any, Callable, List
import threading
import time


class Event:
    """事件类"""

    def __init__(self, event_type: str, data: Dict[str, Any] = None):
        """初始化事件"""
        self.event_type = event_type
        self.data = data or {}
        self.timestamp = time.time()


class EventListener:
    """事件监听器类"""

    def __init__(self, callback: Callable[[Event], None], event_type: str = None):
        """初始化事件监听器"""
        self.callback = callback
        self.event_type = event_type


class EventSystem:
    """事件系统类"""

    def __init__(self):
        """初始化事件系统"""
        self.listeners: List[EventListener] = []
        self.event_queue: List[Event] = []
        self.running = False
        self.thread = None
        self.lock = threading.Lock()

    def start(self):
        """启动事件系统"""
        self.running = True
        self.thread = threading.Thread(target=self._process_events, daemon=True)
        self.thread.start()

    def stop(self):
        """停止事件系统"""
        self.running = False
        if self.thread:
            self.thread.join()

    def register_listener(self, callback: Callable[[Event], None], event_type: str = None):
        """注册事件监听器"""
        listener = EventListener(callback, event_type)
        with self.lock:
            self.listeners.append(listener)
        return listener

    def unregister_listener(self, listener: EventListener):
        """注销事件监听器"""
        with self.lock:
            if listener in self.listeners:
                self.listeners.remove(listener)

    def emit(self, event_type: str, data: Dict[str, Any] = None):
        """发送事件"""
        event = Event(event_type, data)
        with self.lock:
            self.event_queue.append(event)

    def _process_events(self):
        """处理事件队列"""
        while self.running:
            # 处理所有事件
            with self.lock:
                events = self.event_queue.copy()
                self.event_queue.clear()

            for event in events:
                self._dispatch_event(event)

            # 短暂休眠，避免CPU占用过高
            time.sleep(0.01)

    def _dispatch_event(self, event: Event):
        """分发事件到监听器"""
        with self.lock:
            # 复制监听器列表，避免在遍历过程中修改
            listeners = self.listeners.copy()

        for listener in listeners:
            # 如果监听器指定了事件类型，则只处理该类型的事件
            if listener.event_type is None or listener.event_type == event.event_type:
                try:
                    listener.callback(event)
                except Exception as e:
                    print(f"Error in event listener: {e}")


# 事件类型常量
class EventType:
    """事件类型常量"""
    # 音频相关事件
    AUDIO_LOADED = "audio_loaded"
    AUDIO_PLAYING = "audio_playing"
    AUDIO_PAUSED = "audio_paused"
    AUDIO_STOPPED = "audio_stopped"
    AUDIO_FEATURES_UPDATED = "audio_features_updated"
    BEAT_DETECTED = "beat_detected"
    
    # 视觉相关事件
    VISUAL_TYPE_CHANGED = "visual_type_changed"
    VISUAL_CONFIG_UPDATED = "visual_config_updated"
    PATTERN_CHANGED = "pattern_changed"
    
    # 系统相关事件
    CONFIG_UPDATED = "config_updated"
    ERROR_OCCURRED = "error_occurred"
    INFO_MESSAGE = "info_message"


# 全局事件系统实例
global_event_system = EventSystem()


def get_event_system() -> EventSystem:
    """获取全局事件系统实例"""
    return global_event_system


def emit_event(event_type: str, data: Dict[str, Any] = None):
    """发送事件的便捷函数"""
    global_event_system.emit(event_type, data)


def register_event_listener(callback: Callable[[Event], None], event_type: str = None) -> EventListener:
    """注册事件监听器的便捷函数"""
    return global_event_system.register_listener(callback, event_type)


def unregister_event_listener(listener: EventListener):
    """注销事件监听器的便捷函数"""
    global_event_system.unregister_listener(listener)
