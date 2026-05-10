# 🚀 快速开始指南

## 📦 项目简介

RGB灯光同步控制系统，支持：
- ✅ 屏幕取色同步到RGB设备
- ✅ MK850键盘独立控制（105键）
- ✅ TSG600鼠标控制
- ✅ 虚拟键盘可视化操作
- ✅ 紧凑型控制中心布局

---

## ⚡ 快速启动

### 方法1: 使用启动脚本（推荐）

```bash
# 右键 → 以管理员身份运行
启动控制面板.bat
```

### 方法2: 命令行启动

```bash
# 以管理员权限打开PowerShell或CMD
python gui_control.py
```

---

## 🎮 主要功能

### 1. 屏幕取色同步
- 点击"开始同步"按钮
- 鼠标移动时实时提取颜色
- 自动同步到连接的RGB设备

### 2. 虚拟键盘控制
- 点击任意虚拟按键
- 选择颜色后应用到实体键盘
- 支持单键、多键、全键盘设置

### 3. 手动颜色设置
- 使用颜色选择器选取颜色
- 调节 R/G/B 滑块
- 应用到指定设备或按键

---

## 📁 核心文件说明

| 文件 | 用途 |
|------|------|
| `gui_control.py` | GUI主程序 |
| `key_mapping.py` | 按键映射配置 |
| `rgb_sync_controller.py` | RGB同步控制器 |
| `color_extractor.py` | 屏幕取色模块 |
| `devices/mk850_keyboard.py` | MK850键盘驱动 |
| `devices/tsg600_mouse.py` | TSG600鼠标驱动 |

---

## 🔧 常用操作

### 查看按键映射配置
1. 编辑 `key_mapping.py` 查看逻辑映射
2. 修改 `mk850_key_mapping.ini` 自定义布局
3. 运行 `python key_mapping.py` 可预览当前所有按键的映射表

---

## ❓ 常见问题

### Q: 为什么需要管理员权限？
A: HID设备控制需要访问底层硬件接口，Windows要求管理员权限。

### Q: 键盘只有98个按键？
A: 经过驱动优化，目前已支持 105 个按键的独立控制。

### Q: 如何修改按键映射？
A: 编辑 `mk850_key_mapping.ini` 文件即可。

### Q: Grid布局和Pack布局有什么区别？
A: Grid布局更精确、更美观、性能更好，详见 `CLEANUP_AND_OPTIMIZATION.md`。

---

## 📚 详细文档

- [README.md](README.md) - 项目总览
- [USER_GUIDE.md](USER_GUIDE.md) - 完整使用指南
- [MK850_KEYBOARD_INFO.md](MK850_KEYBOARD_INFO.md) - 键盘技术说明
- [KEY_MAPPING_README.md](KEY_MAPPING_README.md) - 按键映射使用说明
- [CLEANUP_AND_OPTIMIZATION.md](CLEANUP_AND_OPTIMIZATION.md) - 优化报告
- [FINAL_SUMMARY.md](FINAL_SUMMARY.md) - 最终总结

---

## 🎯 下一步

1. **启动GUI**: 运行 `启动控制面板.bat`
2. **连接设备**: 确保MK850键盘已连接
3. **测试功能**: 点击虚拟键盘测试按键控制
4. **享受RGB**: 体验屏幕取色同步效果

---

**版本**: v2.1.0  
**更新日期**: 2026-05-10
**状态**: ✅ 生产就绪
