"""测试 DashScope Embedding"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from langchain_community.embeddings import DashScopeEmbeddings

api_key = os.getenv("DASHSCOPE_API_KEY")
print(f"API Key: {api_key[:10] if api_key else 'None'}...")

print("\n测试 DashScope Embedding...")
try:
    embeddings = DashScopeEmbeddings(
        model="text-embedding-v3",
        dashscope_api_key=api_key
    )
    vector = embeddings.embed_query("hello")
    print(f"✅ 成功! 向量维度: {len(vector)}")
except Exception as e:
    print(f"❌ 失败: {type(e).__name__}: {e}")
