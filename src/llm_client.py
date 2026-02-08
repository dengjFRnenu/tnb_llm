#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LLM 客户端封装
支持多种大模型 API：OpenAI、Claude、Qwen、DeepSeek、本地模型等
"""

import os
from typing import Optional, Callable
from pathlib import Path


class LLMClient:
    """
    统一的 LLM 客户端接口
    支持多种大模型 API
    """
    
    def __init__(
        self,
        provider: str = "openai",
        model: str = None,
        api_key: str = None,
        base_url: str = None,
        temperature: float = 0.7,
        max_tokens: int = 2000
    ):
        """
        初始化 LLM 客户端
        
        Args:
            provider: 提供商 ("openai", "qwen", "deepseek", "claude", "local")
            model: 模型名称
            api_key: API 密钥（优先从环境变量读取）
            base_url: API 基础 URL
            temperature: 温度参数
            max_tokens: 最大生成 token 数
        """
        self.provider = provider.lower()
        self.temperature = temperature
        self.max_tokens = max_tokens
        
        # 默认配置
        self.configs = {
            "openai": {
                "model": "gpt-4o-mini",
                "base_url": "https://api.openai.com/v1",
                "env_key": "OPENAI_API_KEY"
            },
            "qwen": {
                "model": "qwen-turbo",
                "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
                "env_key": "DASHSCOPE_API_KEY"
            },
            "deepseek": {
                "model": "deepseek-chat",
                "base_url": "https://api.deepseek.com/v1",
                "env_key": "DEEPSEEK_API_KEY"
            },
            "claude": {
                "model": "claude-3-haiku-20240307",
                "base_url": None,  # 使用官方 SDK
                "env_key": "ANTHROPIC_API_KEY"
            },
            # ========== 免费 API ==========
            # 硅基流动 - 注册送额度，支持多种开源模型
            # 申请: https://cloud.siliconflow.cn/
            "siliconflow": {
                "model": "Qwen/Qwen2.5-7B-Instruct",
                "base_url": "https://api.siliconflow.cn/v1",
                "env_key": "SILICONFLOW_API_KEY"
            },
            # Groq - 免费使用 Llama/Mixtral
            # 申请: https://console.groq.com/
            "groq": {
                "model": "llama-3.1-8b-instant",
                "base_url": "https://api.groq.com/openai/v1",
                "env_key": "GROQ_API_KEY"
            },
            # 智谱 GLM - 新用户有免费额度
            # 申请: https://open.bigmodel.cn/
            "zhipu": {
                "model": "glm-4-flash",
                "base_url": "https://open.bigmodel.cn/api/paas/v4",
                "env_key": "ZHIPU_API_KEY"
            },
            # Google Gemini - 免费额度充足
            # 申请: https://aistudio.google.com/apikey
            "gemini": {
                "model": "gemini-2.0-flash",
                "base_url": "https://generativelanguage.googleapis.com/v1beta/openai",
                "env_key": "GEMINI_API_KEY"
            },
            # ========== 本地模型 ==========
            "local": {
                "model": "default",
                "base_url": "http://localhost:8080/v1",
                "env_key": None
            },
            "ollama": {
                "model": "qwen2.5:7b",
                "base_url": "http://localhost:11434/v1",
                "env_key": None
            }
        }
        
        # 获取配置
        config = self.configs.get(self.provider, self.configs["openai"])
        
        self.model = model or config["model"]
        self.base_url = base_url or config["base_url"]
        self.api_key = api_key or os.getenv(config["env_key"] or "", "sk-placeholder")
        
        # 初始化客户端
        self.client = None
        self._init_client()
        
        print(f"✅ LLM 客户端初始化: {self.provider} / {self.model}")
    
    def _init_client(self):
        """初始化具体的客户端"""
        if self.provider == "claude":
            try:
                import anthropic
                self.client = anthropic.Anthropic(api_key=self.api_key)
            except ImportError:
                print("⚠️ 请安装 anthropic: pip install anthropic")
        else:
            # OpenAI 兼容接口
            try:
                import openai
                self.client = openai.OpenAI(
                    api_key=self.api_key,
                    base_url=self.base_url
                )
            except ImportError:
                print("⚠️ 请安装 openai: pip install openai")
    
    def chat(self, prompt: str, system: str = None) -> str:
        """
        发送对话请求
        
        Args:
            prompt: 用户提示
            system: 系统提示（可选）
        
        Returns:
            模型响应文本
        """
        if self.client is None:
            raise RuntimeError("LLM 客户端未初始化")
        
        try:
            if self.provider == "claude":
                # Claude API
                messages = [{"role": "user", "content": prompt}]
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=self.max_tokens,
                    system=system or "你是一个专业的医学助手。",
                    messages=messages
                )
                return response.content[0].text
            else:
                # OpenAI 兼容接口
                messages = []
                if system:
                    messages.append({"role": "system", "content": system})
                messages.append({"role": "user", "content": prompt})
                
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=self.temperature,
                    max_tokens=self.max_tokens
                )
                return response.choices[0].message.content
        
        except Exception as e:
            print(f"❌ LLM 调用失败: {e}")
            raise
    
    def __call__(self, prompt: str) -> str:
        """允许直接调用"""
        return self.chat(prompt)


# ============================================
# 便捷函数
# ============================================

def create_llm_api(
    provider: str = "qwen",
    model: str = None,
    api_key: str = None
) -> Callable[[str], str]:
    """
    创建 LLM API 函数，供 DiaAgent 使用
    
    Args:
        provider: 提供商名称
        model: 模型名称
        api_key: API 密钥
    
    Returns:
        可调用的 LLM 函数
    
    Usage:
        llm_api = create_llm_api("qwen")
        agent = DiaAgent(llm_api=llm_api)
    """
    client = LLMClient(provider=provider, model=model, api_key=api_key)
    return client


def create_qwen_api(api_key: str = None, model: str = "qwen-turbo") -> Callable[[str], str]:
    """创建通义千问 API"""
    return create_llm_api("qwen", model=model, api_key=api_key)


def create_deepseek_api(api_key: str = None, model: str = "deepseek-chat") -> Callable[[str], str]:
    """创建 DeepSeek API"""
    return create_llm_api("deepseek", model=model, api_key=api_key)


def create_openai_api(api_key: str = None, model: str = "gpt-4o-mini") -> Callable[[str], str]:
    """创建 OpenAI API"""
    return create_llm_api("openai", model=model, api_key=api_key)


def create_ollama_api(model: str = "qwen2.5:7b", base_url: str = None) -> Callable[[str], str]:
    """创建 Ollama 本地 API"""
    client = LLMClient(
        provider="ollama",
        model=model,
        base_url=base_url or "http://localhost:11434/v1",
        api_key="ollama"
    )
    return client


# ========== 免费 API 便捷函数 ==========

def create_siliconflow_api(api_key: str = None, model: str = "Qwen/Qwen2.5-7B-Instruct") -> Callable[[str], str]:
    """
    创建硅基流动 API (免费额度)
    申请地址: https://cloud.siliconflow.cn/
    """
    return create_llm_api("siliconflow", model=model, api_key=api_key)


def create_groq_api(api_key: str = None, model: str = "llama-3.1-8b-instant") -> Callable[[str], str]:
    """
    创建 Groq API (免费)
    申请地址: https://console.groq.com/
    """
    return create_llm_api("groq", model=model, api_key=api_key)


def create_zhipu_api(api_key: str = None, model: str = "glm-4-flash") -> Callable[[str], str]:
    """
    创建智谱 GLM API (新用户有免费额度)
    申请地址: https://open.bigmodel.cn/
    """
    return create_llm_api("zhipu", model=model, api_key=api_key)


def create_gemini_api(api_key: str = None, model: str = "gemini-2.0-flash") -> Callable[[str], str]:
    """
    创建 Google Gemini API (免费额度充足)
    申请地址: https://aistudio.google.com/apikey
    """
    return create_llm_api("gemini", model=model, api_key=api_key)


# ============================================
# 测试
# ============================================

if __name__ == "__main__":
    print("=" * 60)
    print("🧪 LLM 客户端测试")
    print("=" * 60)
    
    # 检查可用的 API 密钥 (优先检查免费 API)
    providers = [
        ("siliconflow", "SILICONFLOW_API_KEY", "硅基流动 (免费)"),
        ("groq", "GROQ_API_KEY", "Groq (免费)"),
        ("zhipu", "ZHIPU_API_KEY", "智谱 GLM"),
        ("qwen", "DASHSCOPE_API_KEY", "通义千问"),
        ("deepseek", "DEEPSEEK_API_KEY", "DeepSeek"),
        ("openai", "OPENAI_API_KEY", "OpenAI"),
    ]
    
    print("\n📋 API 配置状态:")
    available = None
    for provider, env_key, name in providers:
        if os.getenv(env_key):
            print(f"  ✅ {name}: 已配置")
            if available is None:
                available = provider
        else:
            print(f"  ❌ {name}: 未配置")
    
    if available:
        print(f"\n📝 测试 {available} API...")
        try:
            llm = create_llm_api(available)
            response = llm("请用一句话介绍糖尿病")
            print(f"响应: {response[:200]}...")
        except Exception as e:
            print(f"❌ 测试失败: {e}")
    else:
        print("\n" + "=" * 60)
        print("⚠️ 未检测到可用的 API 密钥")
        print("=" * 60)
        print("\n推荐免费 API (注册即用):")
        print("  1. 硅基流动: https://cloud.siliconflow.cn/")
        print("     export SILICONFLOW_API_KEY=your-key")
        print("  2. Groq: https://console.groq.com/")
        print("     export GROQ_API_KEY=your-key")
        print("  3. 智谱 GLM: https://open.bigmodel.cn/")
        print("     export ZHIPU_API_KEY=your-key")

