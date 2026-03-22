#!/usr/bin/env python3
"""
超市采购管理系统启动脚本
双击此文件即可启动系统
"""
import sys
import os

# 确保当前目录在Python路径中
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# 导入并运行主程序
from main import main

if __name__ == "__main__":
    main()
