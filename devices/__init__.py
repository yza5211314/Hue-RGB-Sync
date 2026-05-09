"""
设备管理器
统一管理所有RGB设备
"""

import importlib
from .base_device import RGBDevice


class DeviceManager:
    """RGB设备管理器"""
    
    def __init__(self):
        self.devices = {}
        self.device_classes = {
            'tsg600': ('devices.tsg600_mouse', 'TSG600Mouse'),
            'mk850': ('devices.mk850_keyboard', 'MK850Keyboard'),
        }
    
    def register_device_class(self, device_id, module_path, class_name):
        """
        注册新的设备类
        
        Args:
            device_id: 设备标识符
            module_path: 模块路径
            class_name: 类名
        """
        self.device_classes[device_id] = (module_path, class_name)
    
    def create_device(self, device_id):
        """
        创建设备实例
        
        Args:
            device_id: 设备标识符
        
        Returns:
            RGBDevice: 设备实例，失败返回None
        """
        if device_id not in self.device_classes:
            print(f"❌ 未知设备: {device_id}")
            return None
        
        try:
            module_path, class_name = self.device_classes[device_id]
            module = importlib.import_module(module_path)
            device_class = getattr(module, class_name)
            
            device = device_class()
            self.devices[device_id] = device
            
            print(f"✅ 创建设备: {device_id}")
            return device
            
        except Exception as e:
            print(f"❌ 创建设备失败 {device_id}: {e}")
            return None
    
    def connect_all(self):
        """连接所有已创建的设备"""
        results = {}
        for device_id, device in self.devices.items():
            success = device.connect()
            results[device_id] = success
        
        return results
    
    def disconnect_all(self):
        """断开所有设备"""
        for device_id, device in self.devices.items():
            device.disconnect()
    
    def set_all_colors(self, r, g, b, **kwargs):
        """
        设置所有设备颜色
        
        Args:
            r, g, b: RGB颜色值
            **kwargs: 其他参数
        
        Returns:
            dict: 每个设备的设置结果
        """
        results = {}
        for device_id, device in self.devices.items():
            if device.is_connected():
                success = device.set_color(r, g, b, **kwargs)
                results[device_id] = success
        
        return results
    
    def get_device(self, device_id):
        """获取指定设备"""
        return self.devices.get(device_id)
    
    def get_all_devices(self):
        """获取所有设备"""
        return self.devices
    
    def get_device_info(self):
        """获取所有设备信息"""
        info = {}
        for device_id, device in self.devices.items():
            info[device_id] = device.get_info()
        
        return info
    
    def list_available_devices(self):
        """列出所有可用的设备类型"""
        return list(self.device_classes.keys())
    
    def scan_and_auto_connect(self):
        """
        扫描并自动连接已知设备
        
        Returns:
            dict: 连接结果
        """
        print("🔍 扫描设备...")
        
        # 创建所有已知设备
        for device_id in self.device_classes.keys():
            if device_id not in self.devices:
                self.create_device(device_id)
        
        # 尝试连接所有设备
        results = self.connect_all()
        
        # 显示结果
        print("\n设备连接状态:")
        for device_id, success in results.items():
            status = "✅ 已连接" if success else "❌ 未连接"
            print(f"  {device_id}: {status}")
        
        return results
