#!/bin/bash
# OpsPilot 启动脚本

echo "================================"
echo "  OpsPilot - 智能运维工具"
echo "================================"
echo ""

# 检查Python版本
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到python3，请先安装Python 3.8+"
    exit 1
fi

# 检查依赖
if [ ! -d "venv" ]; then
    echo "首次运行，正在创建虚拟环境..."
    python3 -m venv venv
    source venv/bin/activate
    echo "正在安装依赖..."
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

# 运行程序
echo "启动OpsPilot..."
echo ""
python3 main.py

deactivate
