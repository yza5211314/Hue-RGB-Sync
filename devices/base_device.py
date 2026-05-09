"""
RGB设备控制基类
所有设备控制器都应继承此类
"""

from abc import ABC, abstractmethod


class RGBDevice(ABC):
    """RGB设备抽象基类"""
    
    def __init__(self, name, vid, pid):
        self.name = name
        self.vid = vid
        self.pid = pid
        self.device = None
        self.connected = False
    
    @abstractmethod
    def connect(self):
        """连接设备"""
        pass
    
    @abstractmethod
    def disconnect(self):
        """断开连接"""
        pass
    
    @abstractmethod
    def set_color(self, r, g, b, **kwargs):
        """
        设置颜色
        
        Args:
            r: 红色值 (0-255)
            g: 绿色值 (0-255)
            b: 蓝色值 (0-255)
            **kwargs: 其他参数（亮度、模式等）
        
        Returns:
            bool: 是否成功
        """
        pass
    
    @abstractmethod
    def set_mode(self, mode, **kwargs):
        """
        设置灯效模式
        
        Args:
            mode: 模式名称或ID
            **kwargs: 模式参数
        
        Returns:
            bool: 是否成功
        """
        pass
    
    def is_connected(self):
        """检查是否已连接"""
        return self.connected
    
    def get_info(self):
        """获取设备信息"""
        return {
            'name': self.name,
            'vid': f"0x{self.vid:04X}",
            'pid': f"0x{self.pid:04X}",
            'connected': self.connected
        }
    
    def __enter__(self):
        """上下文管理器入口"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.disconnect()
        return False
