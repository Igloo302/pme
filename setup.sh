#!/bin/bash
# ==============================================================================
# PME Behavior Monitor & Memory Engine Setup Script
# ==============================================================================

set -e

# Output styling
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0;0m' # No Color

echo -e "${BLUE}======================================================================${NC}"
echo -e "${BLUE}     PME Behavior Monitor & Memory Engine - 一键部署环境安装脚本        ${NC}"
echo -e "${BLUE}======================================================================${NC}"

# 1. Check Python installation
echo -e "\n${BLUE}[1/4] 正在检查本地 Python 3 环境...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}错误: 未在系统中检测到 python3，请先安装 Python 3.8 以上版本。${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
echo -e "${GREEN}✓ 检测到 Python 版本: ${PYTHON_VERSION}${NC}"

# 2. Create Virtual Environment
echo -e "\n${BLUE}[2/4] 正在本地创建 Python 虚拟环境 (.venv)...${NC}"
if [ -d ".venv" ]; then
    echo -e "${BLUE}提示: 虚拟环境 .venv 已存在，将跳过创建直接使用。${NC}"
else
    python3 -m venv .venv
    echo -e "${GREEN}✓ 虚拟环境 .venv 创建成功。${NC}"
fi

# 3. Install Dependencies
echo -e "\n${BLUE}[3/4] 正在激活虚拟环境并安装 Python 依赖项...${NC}"
source .venv/bin/activate

echo -e "正在更新 pip 与 setuptools..."
pip install --upgrade pip setuptools &> /dev/null

echo -e "正在从 requirements.txt 安装项目依赖..."
pip install -r requirements.txt

echo -e "${GREEN}✓ 依赖项安装完成。${NC}"

# 4. Final instructions
echo -e "\n${BLUE}[4/4] 环境安装与配置校验完成！${NC}"
echo -e "${BLUE}======================================================================${NC}"
echo -e "${GREEN}安装部署成功！请遵循以下说明使用本系统：${NC}"
echo -e ""
echo -e "1. 激活虚拟环境 (在终端运行):"
echo -e "   ${BLUE}source .venv/bin/activate${NC}"
echo -e ""
echo -e "2. 运行多源数据清洗 (生成 pme_cleaned_memories.db):"
echo -e "   ${BLUE}python pme_cli.py clean --days 3${NC}"
echo -e ""
echo -e "3. 启动控制台 Web UI 管理面板 (可在网页端控制录制与检索):"
echo -e "   ${BLUE}python pme_cli.py gui${NC}"
echo -e ""
echo -e "4. 基于清洗后的数据进行智能 RAG 记忆问答:"
echo -e "   ${BLUE}python pme_cli.py ask \"今天下午做了什么关于 Aura 项目的工作？\"${NC}"
echo -e ""
echo -e "5. 所有的路径和多频 OCR 时间参数均可在 ${BLUE}config.yaml${NC} 中自定义修改。"
echo -e "${BLUE}======================================================================${NC}"
