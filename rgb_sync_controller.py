"""
RGB灯光同步主控制器
整合设备管理、颜色提取和同步逻辑
"""

import time
from devices import DeviceManager
from color_extractor import ColorExtractor


class RGBSyncController:
    """RGB灯光同步控制器"""
    
    def __init__(self, update_interval=0.3, color_threshold=20, 
                 color_method="dominant"):
        """
        初始化控制器
        
        Args:
            update_interval: 更新间隔（秒）
            color_threshold: 颜色变化阈值
            color_method: 颜色提取方法 ("dominant" 或 "vibrant")
        """
        self.update_interval = update_interval
        self.color_threshold = color_threshold
        self.color_method = color_method
        
        # 初始化组件
        self.device_manager = DeviceManager()
        self.color_extractor = ColorExtractor()
        
        # 状态
        self.running = False
        self.last_color = (0, 0, 0)
        
        print("=" * 60)
        print("🎨 RGB灯光同步系统 - 模块化版本")
        print("=" * 60)
    
    def add_device(self, device_id):
        """
        添加设备
        
        Args:
            device_id: 设备标识符
        
        Returns:
            bool: 是否成功
        """
        device = self.device_manager.create_device(device_id)
        if device:
            return device.connect()
        return False
    
    def auto_scan_devices(self):
        """自动扫描并连接设备"""
        return self.device_manager.scan_and_auto_connect()
    
    def get_screen_color(self):
        """获取屏幕颜色"""
        return self.color_extractor.get_screen_color(self.color_method)
    
    def should_update_color(self, new_color):
        """判断是否应该更新颜色"""
        distance = self.color_extractor.color_distance(self.last_color, new_color)
        
        # 从黑色切换到其他颜色，立即更新
        if self.last_color == (0, 0, 0) and new_color != (0, 0, 0):
            return True
        
        # 颜色差异超过阈值
        if distance > self.color_threshold:
            return True
        
        return False
    
    def sync_color(self, r, g, b):
        """
        同步颜色到所有设备
        
        Args:
            r, g, b: RGB颜色值
        
        Returns:
            dict: 每个设备的同步结果
        """
        results = self.device_manager.set_all_colors(r, g, b)
        
        # 打印结果
        status_parts = []
        for device_id, success in results.items():
            status = "✅" if success else "❌"
            status_parts.append(f"{device_id}: {status}")
        
        print(f"🎯 RGB({r:3d}, {g:3d}, {b:3d}) | {', '.join(status_parts)}")
        
        return results
    
    def run(self):
        """运行主循环"""
        print("\n开始屏幕取色同步... (Ctrl+C 退出)")
        print("-" * 60)
        
        self.running = True
        
        try:
            while self.running:
                # 获取屏幕颜色
                current_color = self.get_screen_color()
                
                # 判断是否需要更新
                if self.should_update_color(current_color):
                    r, g, b = current_color
                    self.sync_color(r, g, b)
                    self.last_color = current_color
                
                time.sleep(self.update_interval)
        
        except KeyboardInterrupt:
            print("\n\n⏹️  程序已停止")
        finally:
            self.stop()
    
    def stop(self):
        """停止同步并断开所有设备"""
        self.running = False
        self.device_manager.disconnect_all()
        print("🔌 所有设备已断开")
    
    def get_status(self):
        """获取系统状态"""
        return {
            'running': self.running,
            'last_color': self.last_color,
            'devices': self.device_manager.get_device_info(),
            'update_interval': self.update_interval,
            'color_method': self.color_method
        }
