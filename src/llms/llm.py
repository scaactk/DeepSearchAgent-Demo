"""
支持OpenAI接口格式的通用LLM实现
"""

import os
from typing import Optional, Dict, Any
from openai import OpenAI
from .base import BaseLLM

class LLM(BaseLLM):
    """通用LLM实现类"""
    
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None, model_name: Optional[str] = None):
        """
        初始化LLM客户端
        
        Args:
            api_key: API密钥，如果不提供则从环境变量读取API_KEY
            base_url: API基础URL，默认使用DeepSeek的URL
            model_name: 模型名称，默认使用deepseek-chat
        """
        if api_key is None:
            raise ValueError("API Key未找到！请在config.py或.env文件中设置API_KEY。")
        
        if base_url is None:
            raise ValueError("Base URL未找到！请在config.py或.env文件中设置BASE_URL。")
            
        super().__init__(api_key, base_url, model_name)
        
        # 初始化OpenAI客户端，使用支持openai格式的endpoint url
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )
        if self.model_name:
            self.default_model = self.model_name
        else:
            raise ValueError("模型名称未找到！请在config.py或.env文件中设置MODEL_NAME。")
    
    
    def invoke(self, system_prompt: str, user_prompt: str, **kwargs) -> str:
        """
        调用LLM API生成回复
        
        Args:
            system_prompt: 系统提示词
            user_prompt: 用户输入
            **kwargs: 其他参数，如temperature、max_tokens等
            
        Returns:
            LLM 生成的回复文本
        """
        try:
            # 构建消息
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            # 设置默认参数
            params = {
                "model": self.default_model,
                "messages": messages,
                "temperature": kwargs.get("temperature", 0.7),
                "max_tokens": kwargs.get("max_tokens", 4000),
                "stream": False
            }
            
            # 调用API
            response = self.client.chat.completions.create(**params)
            
            # 提取回复内容
            if response.choices and response.choices[0].message:
                content = response.choices[0].message.content
                return self.validate_response(content)
            else:
                return ""
                
        except Exception as e:
            print(f"{self.base_url} API调用错误: {str(e)}")
            raise e
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        获取当前模型信息
        
        Returns:
            模型信息字典
        """
        return {
            "model": self.default_model,
            "base_url": self.base_url,
        }
