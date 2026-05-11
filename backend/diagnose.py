"""环境诊断脚本 - 检查依赖和导入"""
import sys
import traceback

def check_import(module_path, imports):
    """检查模块导入"""
    result = {"module": module_path, "imports": {}, "success": True, "error": None}
    try:
        module = __import__(module_path, fromlist=imports)
        for imp in imports:
            try:
                obj = getattr(module, imp)
                result["imports"][imp] = "OK"
            except AttributeError:
                result["imports"][imp] = "NOT FOUND"
                result["success"] = False
    except Exception as e:
        result["success"] = False
        result["error"] = str(e)
    return result

def main():
    print("=" * 60)
    print("Python 环境诊断")
    print("=" * 60)
    print(f"Python 版本: {sys.version}")
    print(f"Python 路径: {sys.executable}")
    print()

    checks = [
        ("langchain", ["__version__"]),
        ("langchain.agents", ["AgentExecutor", "create_tool_calling_agent"]),
        ("langchain_core", ["__version__"]),
        ("langchain_core.agents", ["AgentExecutor"]),
        ("langgraph", ["__version__"]),
        ("langgraph.graph", ["StateGraph"]),
    ]

    for module_path, imports in checks:
        print(f"检查 {module_path}...")
        result = check_import(module_path, imports)
        if result["success"]:
            for imp, status in result["imports"].items():
                print(f"  - {imp}: {status}")
        else:
            print(f"  导入失败: {result['error']}")
        print()

    print("=" * 60)
    print("诊断完成")
    print("=" * 60)

if __name__ == "__main__":
    main()
