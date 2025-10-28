# 🚀 快速参考卡片

## 📁 项目文件说明

| 文件 | 说明 |
|------|------|
| `config.py` | **统一配置管理**，所有代码都从这里导入配置 |
| `.env` | **你的私有配置**（不提交到 Git），存放 API Key |
| `.env.example` | **配置模板**，可以分享给他人 |
| `requirements.txt` | **项目依赖列表** |
| `setup.sh` | **自动化安装脚本** |
| `CONFIG_USAGE.md` | **详细的配置使用文档** |
| `README.md` | **项目说明和快速开始** |

## ⚡ 常用命令

### 环境管理

```bash
# 激活 venv 环境
source .venv/bin/activate

# 激活 conda 环境
conda activate agi_study

# 退出虚拟环境
deactivate  # venv
conda deactivate  # conda
```

### 依赖管理

```bash
# 安装依赖（使用镜像）
pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/

# 安装单个包
pip install package-name

# 查看已安装的包
pip list

# 导出当前环境的依赖
pip freeze > requirements.txt
```

### 配置管理

```bash
# 创建配置文件
cp .env.example .env

# 测试配置
python config.py

# 查看当前配置（在 Python 中）
from config import settings
settings.print_config()
```

## 💡 代码模板

### 1. OpenAI 基础使用

```python
from config import settings
from openai import OpenAI

client = OpenAI(
    api_key=settings.OPENAI_API_KEY,
    base_url=settings.OPENAI_BASE_URL
)

response = client.chat.completions.create(
    model=settings.OPENAI_MODEL,
    messages=[
        {"role": "user", "content": "Hello!"}
    ]
)
print(response.choices[0].message.content)
```

### 2. LangChain 使用

```python
from config import settings
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    model=settings.OPENAI_MODEL,
    api_key=settings.OPENAI_API_KEY,
    base_url=settings.OPENAI_BASE_URL,
    temperature=settings.OPENAI_TEMPERATURE
)

response = llm.invoke("Hello!")
print(response.content)
```

### 3. LangGraph Agent

```python
from config import settings
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langchain_core.tools import tool

@tool
def my_tool(query: str) -> str:
    """工具描述"""
    return "结果"

llm = ChatOpenAI(
    model=settings.OPENAI_MODEL,
    api_key=settings.OPENAI_API_KEY
)

agent = create_react_agent(llm, [my_tool])
result = agent.invoke({"messages": [("user", "你好")]})
```

### 4. RAG 应用

```python
from config import settings
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA

# Embedding
embeddings = OpenAIEmbeddings(
    api_key=settings.OPENAI_API_KEY,
    base_url=settings.OPENAI_BASE_URL
)

# 向量存储
vectorstore = FAISS.from_texts(
    texts=["文本1", "文本2"],
    embedding=embeddings
)

# QA 链
llm = ChatOpenAI(
    api_key=settings.OPENAI_API_KEY,
    model=settings.OPENAI_MODEL
)

qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=vectorstore.as_retriever()
)

answer = qa_chain.run("问题")
```

## 🔧 常见问题

### Q1: 导入 settings 报错？
```python
# 确保从项目根目录导入
from config import settings

# 如果还是报错，检查 PYTHONPATH
import sys
sys.path.append('/path/to/agi_study')
```

### Q2: API Key 不生效？
```bash
# 1. 确认 .env 文件在项目根目录
ls -la .env

# 2. 确认格式正确（等号前后无空格）
OPENAI_API_KEY=sk-xxx

# 3. 重启 Python 解释器或 PyCharm
```

### Q3: PyCharm 终端不激活虚拟环境？
1. `Settings` → `Tools` → `Terminal`
2. 勾选 `Activate virtualenv` 或 `Activate conda environment`
3. 重启终端

### Q4: 包安装失败？
```bash
# 使用国内镜像
pip install package-name -i https://mirrors.aliyun.com/pypi/simple/

# 或临时信任
pip install package-name --trusted-host pypi.tuna.tsinghua.edu.cn
```

## 📚 学习路径

```
01-core-concepts/      ← 从这里开始
├── prompt_engineering/
├── function_calling/
└── nlg/

02-frameworks/         ← 然后学框架
├── langchain/
├── semantic_kernel/
└── assistants_api/

03-ai-agent/          ← 再学 Agent
├── simple_agent/
├── route_agent/
└── cooperation_agent/

04-rag/               ← RAG 应用
├── base/
├── chatpdf/
└── graph_rag/

05-model-techniques/  ← 高级技术
├── embedding/
└── fine-tuning/

06-monitoring/        ← 监控评估
└── langfuse/
```

## 🎯 最佳实践

### ✅ 推荐做法

```python
# ✅ 使用统一配置
from config import settings
client = OpenAI(api_key=settings.OPENAI_API_KEY)

# ✅ 使用类型提示
def process(text: str) -> str:
    return text.upper()

# ✅ 使用上下文管理器
with open('file.txt', 'r') as f:
    content = f.read()

# ✅ 异常处理
try:
    result = risky_operation()
except Exception as e:
    print(f"错误: {e}")
```

### ❌ 避免的做法

```python
# ❌ 硬编码密钥
api_key = "sk-xxx"

# ❌ 分散配置
OPENAI_KEY = "xxx"  # 在多个文件中重复

# ❌ 忽略异常
try:
    operation()
except:
    pass  # 不处理也不记录

# ❌ 全局导入
from module import *  # 不清楚导入了什么
```

## 🛠️ 调试技巧

```python
# 1. 打印配置
from config import settings
settings.print_config()

# 2. 启用 LangChain 调试
import langchain
langchain.debug = True

# 3. 查看模型输出
response = llm.invoke("test")
print(response)  # 查看完整响应对象

# 4. 使用 pdb 调试
import pdb; pdb.set_trace()
```

## 📞 获取帮助

1. **查看文档**：`CONFIG_USAGE.md`
2. **运行测试**：`python config.py`
3. **查看示例**：各目录下的代码文件
4. **提交 Issue**：如果遇到问题

---

**记住**：所有配置都统一在 `config.py`，所有密钥都放在 `.env` 文件中！

