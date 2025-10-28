"""
统一配置管理
所有项目中的配置都从这里导入使用
使用方法：
    from config import settings
    
    client = OpenAI(
        api_key=settings.OPENAI_API_KEY,
        base_url=settings.OPENAI_BASE_URL
    )
"""
import os
from pathlib import Path
from dotenv import load_dotenv, find_dotenv

# 加载 .env 文件（从项目根目录）
_env_file = find_dotenv()
if _env_file:
    load_dotenv(_env_file)
else:
    # 如果找不到 .env，尝试从当前目录加载
    _project_root = Path(__file__).parent
    _env_path = _project_root / ".env"
    if _env_path.exists():
        load_dotenv(_env_path)


class Settings:
    """配置类 - 集中管理所有配置项"""
    
    # ==================== OpenAI 配置 ====================
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_BASE_URL: str = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
    OPENAI_TEMPERATURE: float = float(os.getenv("OPENAI_TEMPERATURE", "0.7"))
    
    # ==================== 其他大模型配置 ====================
    # 如果使用其他模型，可以在这里添加
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    QWEN_API_KEY: str = os.getenv("QWEN_API_KEY", "")
    QWEN_BASE_URL: str = os.getenv("QWEN_BASE_URL", "")
    
    # ==================== LangChain 配置 ====================
    LANGCHAIN_API_KEY: str = os.getenv("LANGCHAIN_API_KEY", "")
    LANGCHAIN_TRACING_V2: str = os.getenv("LANGCHAIN_TRACING_V2", "false")
    LANGCHAIN_PROJECT: str = os.getenv("LANGCHAIN_PROJECT", "agi_study")
    
    # ==================== Langfuse 监控配置 ====================
    LANGFUSE_PUBLIC_KEY: str = os.getenv("LANGFUSE_PUBLIC_KEY", "")
    LANGFUSE_SECRET_KEY: str = os.getenv("LANGFUSE_SECRET_KEY", "")
    LANGFUSE_HOST: str = os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")
    
    # ==================== 向量数据库配置 ====================
    ELASTICSEARCH_URL: str = os.getenv("ELASTICSEARCH_URL", "http://localhost:9200")
    PINECONE_API_KEY: str = os.getenv("PINECONE_API_KEY", "")
    
    # ==================== 项目路径配置 ====================
    PROJECT_ROOT: Path = Path(__file__).parent
    DATA_DIR: Path = PROJECT_ROOT / "data"
    MODELS_DIR: Path = PROJECT_ROOT / "models"
    
    # ==================== Embedding 模型配置 ====================
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "BAAI/bge-m3")
    EMBEDDING_DIMENSION: int = int(os.getenv("EMBEDDING_DIMENSION", "1024"))
    
    # ==================== 其他配置 ====================
    AMAP_API_KEY: str = os.getenv("AMAP_API_KEY", "")
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    @classmethod
    def validate(cls):
        """验证必要的配置是否存在"""
        if not cls.OPENAI_API_KEY:
            print("⚠️  警告: OPENAI_API_KEY 未设置，请在 .env 文件中配置")
        return cls
    
    @classmethod
    def print_config(cls, show_secrets: bool = False):
        """打印当前配置（用于调试）"""
        print("=" * 50)
        print("当前配置:")
        print("=" * 50)
        for key, value in cls.__dict__.items():
            if not key.startswith("_") and key.isupper():
                if "KEY" in key or "SECRET" in key:
                    if show_secrets:
                        print(f"{key}: {value}")
                    else:
                        masked = value[:8] + "..." if value else "(未设置)"
                        print(f"{key}: {masked}")
                else:
                    print(f"{key}: {value}")
        print("=" * 50)


# 创建全局配置实例
settings = Settings.validate()


# ==================== 兼容性支持 ====================
# 为了向后兼容，提供一些常用的变量名
openai_api_key = settings.OPENAI_API_KEY
openai_base_url = settings.OPENAI_BASE_URL
openai_model = settings.OPENAI_MODEL


if __name__ == "__main__":
    # 测试配置
    settings.print_config(show_secrets=False)

