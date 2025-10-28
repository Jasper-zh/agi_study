#!/bin/bash

# AGI Study 项目环境设置脚本
# 使用方法: bash setup.sh

set -e  # 遇到错误立即退出

echo "🚀 开始设置 AGI Study 项目环境..."
echo ""

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 检查 Python
echo "📌 检查 Python 环境..."
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ 未找到 Python3，请先安装 Python${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Python 版本: $(python3 --version)${NC}"
echo ""

# 询问使用哪种虚拟环境
echo "请选择虚拟环境类型："
echo "  1) venv (Python 自带)"
echo "  2) conda (Anaconda/Miniconda)"
read -p "请输入选项 [1 or 2]: " env_choice

if [ "$env_choice" = "1" ]; then
    # 使用 venv
    echo ""
    echo "📦 创建 venv 虚拟环境..."
    
    if [ -d ".venv" ]; then
        echo -e "${YELLOW}⚠️  .venv 已存在，跳过创建${NC}"
    else
        python3 -m venv .venv
        echo -e "${GREEN}✅ 虚拟环境创建完成${NC}"
    fi
    
    # 激活环境
    echo ""
    echo "🔄 激活虚拟环境..."
    source .venv/bin/activate
    echo -e "${GREEN}✅ 虚拟环境已激活${NC}"
    
elif [ "$env_choice" = "2" ]; then
    # 使用 conda
    echo ""
    echo "📦 创建 conda 虚拟环境..."
    
    if ! command -v conda &> /dev/null; then
        echo -e "${RED}❌ 未找到 conda，请先安装 Anaconda 或 Miniconda${NC}"
        exit 1
    fi
    
    read -p "请输入环境名称 [默认: agi_study]: " env_name
    env_name=${env_name:-agi_study}
    
    if conda env list | grep -q "^${env_name} "; then
        echo -e "${YELLOW}⚠️  环境 ${env_name} 已存在，跳过创建${NC}"
    else
        conda create -n ${env_name} python=3.11 -y
        echo -e "${GREEN}✅ Conda 环境创建完成${NC}"
    fi
    
    # 激活环境
    echo ""
    echo "🔄 激活 conda 环境..."
    eval "$(conda shell.bash hook)"
    conda activate ${env_name}
    echo -e "${GREEN}✅ Conda 环境已激活: ${env_name}${NC}"
    
else
    echo -e "${RED}❌ 无效的选项${NC}"
    exit 1
fi

# 升级 pip
echo ""
echo "⬆️  升级 pip..."
pip install --upgrade pip
echo -e "${GREEN}✅ pip 已升级${NC}"

# 安装依赖
echo ""
echo "📥 安装项目依赖..."
read -p "是否使用镜像源加速？[y/n, 默认: y]: " use_mirror
use_mirror=${use_mirror:-y}

if [ "$use_mirror" = "y" ] || [ "$use_mirror" = "Y" ]; then
    echo "使用阿里云镜像源..."
    pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/
else
    pip install -r requirements.txt
fi
echo -e "${GREEN}✅ 依赖安装完成${NC}"

# 配置 .env 文件
echo ""
echo "⚙️  配置环境变量..."
if [ -f ".env" ]; then
    echo -e "${YELLOW}⚠️  .env 文件已存在，跳过创建${NC}"
    echo -e "${YELLOW}   如需重新配置，请手动编辑 .env 文件${NC}"
else
    cp .env.example .env
    echo -e "${GREEN}✅ .env 文件已创建${NC}"
    echo -e "${YELLOW}⚠️  请编辑 .env 文件，填入你的 API Key:${NC}"
    echo ""
    echo "   vim .env   # 或使用其他编辑器"
    echo ""
fi

# 测试配置
echo ""
echo "🧪 测试配置..."
python config.py

# 完成
echo ""
echo -e "${GREEN}✨ 环境设置完成！${NC}"
echo ""
echo "下一步："
echo "  1. 编辑 .env 文件，填入你的 API Key"
echo "  2. 激活虚拟环境（如果还未激活）："
if [ "$env_choice" = "1" ]; then
    echo "     source .venv/bin/activate"
elif [ "$env_choice" = "2" ]; then
    echo "     conda activate ${env_name}"
fi
echo "  3. 开始学习和编码！"
echo ""
echo "📖 配置使用说明请查看: CONFIG_USAGE.md"
echo ""

