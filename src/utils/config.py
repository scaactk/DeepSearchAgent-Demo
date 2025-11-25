"""
配置管理模块
处理环境变量和配置参数
"""

import os
from dataclasses import dataclass
from typing import Optional

from openai import base_url


@dataclass
class Config:
    """配置类"""
    base_url: Optional[str] = None
    api_key: Optional[str] = None
    tavily_api_key: Optional[str] = None
    
    model: str = ""
    
    # 搜索配置
    max_search_results: int = 3
    search_timeout: int = 240
    max_content_length: int = 20000
    
    # Agent配置
    max_reflections: int = 2
    max_paragraphs: int = 5
    
    # 输出配置
    output_dir: str = "reports"
    save_intermediate_states: bool = True
    
    def validate(self) -> bool:
        """验证配置"""
        # 检查必需的API密钥
        if not self.api_key:
            print("错误: API Key未设置")
            return False
        
        if not self.tavily_api_key:
            print("错误: Tavily API Key未设置")
            return False
        
        return True
    
    @classmethod
    def from_file(cls, config_file: str, method="basic") -> "Config":
        """从配置文件创建配置"""
        if config_file.endswith('.py'):
            # Python配置文件
            import importlib.util
            
            # 动态导入配置文件
            spec = importlib.util.spec_from_file_location("config", config_file)
            config_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(config_module)
            
            if method == "basic":
                base_url = getattr(config_module, "DEEPSEEK_BASE_URL", None)
                api_key = getattr(config_module, "DEEPSEEK_API_KEY", None)
                model = getattr(config_module, "DEEPSEEK_MODEL", "deepseek-chat")
            if method == "advanced":
                base_url = getattr(config_module, "OPENAI_BASE_URL", None)
                api_key = getattr(config_module, "OPENAI_API_KEY", None)
                model = getattr(config_module, "OPENAI_MODEL", "gpt-4o-mini")

            return cls(
                base_url=base_url or None, # 短路赋值
                api_key=api_key,
                model=model,
                tavily_api_key = getattr(config_module, "TAVILY_API_KEY", None),
                max_search_results=getattr(config_module, "SEARCH_RESULTS_PER_QUERY", 3),
                search_timeout=getattr(config_module, "SEARCH_TIMEOUT", 240),
                max_content_length=getattr(config_module, "SEARCH_CONTENT_MAX_LENGTH", 20000),
                max_reflections=getattr(config_module, "MAX_REFLECTIONS", 2),
                max_paragraphs=getattr(config_module, "MAX_PARAGRAPHS", 5),
                output_dir=getattr(config_module, "OUTPUT_DIR", "reports"),
                save_intermediate_states=getattr(config_module, "SAVE_INTERMEDIATE_STATES", True)
            )
        else:
            # .env格式配置文件
            config_dict = {}
            
            if os.path.exists(config_file):
                with open(config_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            config_dict[key.strip()] = value.strip()
            
            return cls(
                base_url=config_dict.get("BASE_URL"),
                api_key=config_dict.get("API_KEY"),
                tavily_api_key=config_dict.get("TAVILY_API_KEY"),
                model=config_dict.get("MODEL_NAME", "deepseek-chat"),
                max_search_results=int(config_dict.get("SEARCH_RESULTS_PER_QUERY", "3")),
                search_timeout=int(config_dict.get("SEARCH_TIMEOUT", "240")),
                max_content_length=int(config_dict.get("SEARCH_CONTENT_MAX_LENGTH", "20000")),
                max_reflections=int(config_dict.get("MAX_REFLECTIONS", "2")),
                max_paragraphs=int(config_dict.get("MAX_PARAGRAPHS", "5")),
                output_dir=config_dict.get("OUTPUT_DIR", "reports"),
                save_intermediate_states=config_dict.get("SAVE_INTERMEDIATE_STATES", "true").lower() == "true"
            )


def load_config(config_file: Optional[str] = None, method="basic") -> Config:
    """
    加载配置
    
    Args:
        config_file: 配置文件路径，如果不指定则使用默认路径
        
    Returns:
        配置对象
    """
    # 确定配置文件路径
    if config_file:
        if not os.path.exists(config_file):
            raise FileNotFoundError(f"配置文件不存在: {config_file}")
        file_to_load = config_file
    else:
        # 尝试加载常见的配置文件
        for config_path in ["myconfig.py", "config.env", ".env"]:
            if os.path.exists(config_path):
                file_to_load = config_path
                print(f"已找到配置文件: {config_path}")
                break
        else:
            raise FileNotFoundError("未找到配置文件，请创建 config.py 文件")
    
    # 创建配置对象
    config = Config.from_file(file_to_load, method=method)
    
    # 验证配置
    if not config.validate():
        raise ValueError("配置验证失败，请检查配置文件中的API密钥")
    
    return config


def print_config(config: Config):
    """打印配置信息（隐藏敏感信息）"""
    print("\n=== 当前配置 ===")
    print(f"提供商: {config.base_url}")
    print(f"模型: {config.model}")
    print(f"最大搜索结果数: {config.max_search_results}")
    print(f"搜索超时: {config.search_timeout}秒")
    print(f"最大内容长度: {config.max_content_length}")
    print(f"最大反思次数: {config.max_reflections}")
    print(f"最大段落数: {config.max_paragraphs}")
    print(f"输出目录: {config.output_dir}")
    print(f"保存中间状态: {config.save_intermediate_states}")
    
    # 显示API密钥状态（不显示实际密钥）
    print(f"API Key: {'已设置' if config.api_key else '未设置'}")
    print(f"Tavily API Key: {'已设置' if config.tavily_api_key else '未设置'}")
    print("==================\n")
