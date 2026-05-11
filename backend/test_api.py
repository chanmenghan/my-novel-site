"""一键测试脚本 - 验证系统是否正常工作"""
import requests
import json

BASE_URL = "http://localhost:5000"

def test_health():
    """测试服务器是否正常运行"""
    print("=" * 50)
    print("测试1: 检查服务器状态")
    print("=" * 50)

    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")
        print("✅ 服务器运行正常！\n")
        return True
    except Exception as e:
        print(f"❌ 服务器连接失败: {e}")
        print("\n请确保服务器正在运行：uv run python run.py")
        return False


def test_screenplay():
    """测试剧本生成功能"""
    print("=" * 50)
    print("测试2: 生成剧本测试")
    print("=" * 50)

    request_data = {
        "creative_brief": {
            "title": "重生之都市医圣",
            "genre": "都市重生",
            "description": "天才医生被陷害致死，重生回大学时代，凭借前世记忆和医术，一步步复仇崛起"
        }
    }

    print(f"请求数据: {json.dumps(request_data, ensure_ascii=False, indent=2)}")
    print("\n正在调用AI生成剧本，请稍候...\n")

    try:
        response = requests.post(
            f"{BASE_URL}/api/screenplay/generate",
            json=request_data
        )

        print(f"状态码: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print("\n" + "=" * 50)
            print("生成结果:")
            print("=" * 50)
            print(f"标题: {result.get('title', 'N/A')}")
            print(f"类型: {result.get('genre', 'N/A')}")
            print(f"人物数量: {len(result.get('characters', []))}")
            print(f"质量评分: {result.get('quality_score', 0)}")

            if result.get('characters'):
                print("\n人物设定:")
                for i, char in enumerate(result['characters'], 1):
                    print(f"  {i}. {char.get('name', 'N/A')} - {char.get('personality', 'N/A')[:50]}...")

            if result.get('plot_outline'):
                print(f"\n主线剧情: {result['plot_outline'].get('main_arc', 'N/A')[:100]}...")

            if result.get('screenplay_draft'):
                draft = result['screenplay_draft']
                print(f"\n剧本正文 (前500字):\n{draft[:500]}...")

            print("\n✅ 剧本生成成功！")
            return True
        else:
            print(f"❌ 生成失败: {response.text}")
            return False

    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return False


def main():
    print("\n" + "=" * 50)
    print("🎬 企业级剧本创作系统 - 一键测试")
    print("=" * 50 + "\n")

    if not test_health():
        return

    if not test_screenplay():
        return

    print("\n" + "=" * 50)
    print("🎉 所有测试通过！系统运行正常！")
    print("=" * 50)
    print("\n你现在可以：")
    print("1. 打开 http://localhost:5000/docs 查看完整的API文档")
    print("2. 在浏览器中尝试不同的创意来生成剧本")


if __name__ == "__main__":
    main()
