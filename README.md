# AGI学习项目 - 大模型应用开发实践

这是一个系统学习大模型应用开发的代码库，包含了从基础概念到实际项目的完整学习路径。

## 🎯 学习目标

通过这个项目，你将学习：
- 大模型的核心概念和基础技术
- 主流框架的使用方法
- AI代理的开发实践
- RAG应用的构建
- 模型微调和嵌入技术
- 应用监控和评估

## 📚 学习路径

### 1. 核心概念 (01-core-concepts/)
- **提示工程** - 学习如何编写有效的提示词
- **函数调用** - 掌握大模型的函数调用能力
- **自然语言生成** - 理解NLG的基本原理

### 2. 框架学习 (02-frameworks/)
- **LangChain** - 最流行的LLM应用开发框架
- **Semantic Kernel** - 微软的AI应用开发框架
- **Assistants API** - OpenAI的助手API使用
- **Qwen Agent** - 阿里一个Agent框架

### 3. AI代理开发 (03-ai-agent/)
- **AutoGPT** - 自主AI代理的实现
- **协作代理** - 多代理协作系统
- **路由代理** - 智能任务分发
- **简单代理** - 基础代理模式

### 4. RAG应用 (04-rag/)
- **向量搜索** - 基于向量的信息检索
- **文档问答** - 智能文档处理
- **图RAG** - 知识图谱增强检索

### 5. 模型技术 (05-model-techniques/)
- **嵌入模型** - 文本向量化技术
- **模型微调** - 定制化模型训练
- **PyTorch** - 深度学习框架实践

### 6. 监控与评估 (06-monitoring/)
- **Langfuse** - LLM应用监控平台

### 7. 工具与实用程序 (07-tools/)
- **Excel工具** - 数据处理工具
- **文件工具** - 文档处理工具
- **邮件工具** - 自动化邮件处理

## 🚀 快速开始

### 方式一：自动化安装（推荐）

运行安装脚本，自动完成环境配置：

```bash
bash setup.sh
```

脚本会帮你：
- 创建虚拟环境（venv 或 conda）
- 安装所有依赖
- 创建配置文件模板

### 方式二：手动安装

1. **克隆项目**
```bash
git clone <your-repo-url>
cd agi_study
```

2. **创建虚拟环境**

使用 venv:
```bash
python -m venv .venv
source .venv/bin/activate  # macOS/Linux
# 或 .venv\Scripts\activate  # Windows
```

使用 conda:
```bash
conda create -n agi_study python=3.11
conda activate agi_study
```

3. **安装依赖**
```bash
# 使用国内镜像加速
pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/

# 或使用官方源
pip install -r requirements.txt
```

4. **配置环境变量**
```bash
# 复制配置模板
cp .env.example .env

# 编辑 .env 文件，填入你的 API Key
vim .env  # 或使用其他编辑器
```

在 `.env` 中配置：
```bash
OPENAI_API_KEY=your-api-key-here
OPENAI_BASE_URL=https://api.openai.com/v1  # 可选
OPENAI_MODEL=gpt-3.5-turbo                  # 可选
```

5. **测试配置**
```bash
python config.py
```

6. **开始学习**

按顺序学习各个模块，每个代码文件都可以直接运行！

### 在代码中使用配置

所有示例代码都可以统一使用配置：

```python
from config import settings

# 使用 OpenAI
from openai import OpenAI
client = OpenAI(
    api_key=settings.OPENAI_API_KEY,
    base_url=settings.OPENAI_BASE_URL
)

# 使用 LangChain
from langchain_openai import ChatOpenAI
llm = ChatOpenAI(
    model=settings.OPENAI_MODEL,
    api_key=settings.OPENAI_API_KEY
)
```

详细配置说明请查看：[CONFIG_USAGE.md](./CONFIG_USAGE.md)

## 📖 学习建议

1. **循序渐进**：按照目录编号顺序学习
2. **动手实践**：每个示例都要亲自运行和修改
3. **项目驱动**：通过实际项目巩固所学知识
4. **持续更新**：关注大模型技术的最新发展

## 🤝 贡献

欢迎提交Issue和Pull Request来改进这个学习项目！

## 📄 许可证

MIT License
