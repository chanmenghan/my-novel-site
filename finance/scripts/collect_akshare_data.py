"""AKShare 金融数据采集脚本 - 将数据整理到知识库"""
import os
import json
from datetime import datetime
from pathlib import Path

import akshare as ak


BASE_DIR = Path(__file__).resolve().parent.parent
KNOWLEDGE_BASE_DIR = BASE_DIR / "knowledge_base"
RESEARCH_REPORTS_DIR = KNOWLEDGE_BASE_DIR / "research_reports"
FINANCIAL_THEORY_DIR = KNOWLEDGE_BASE_DIR / "financial_theory"
MARKET_DATA_DIR = KNOWLEDGE_BASE_DIR / "market_data"

for dir_path in [KNOWLEDGE_BASE_DIR, RESEARCH_REPORTS_DIR, FINANCIAL_THEORY_DIR, MARKET_DATA_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)


def fetch_stock_spot_data():
    """获取 A 股实时行情数据"""
    print("[1/6] 获取 A 股实时行情数据...")
    try:
        df = ak.stock_zh_a_spot_em()
        top_stocks = []

        for _, row in df.head(50).iterrows():
            top_stocks.append({
                "股票代码": row.get('代码', ''),
                "股票名称": row.get('名称', ''),
                "最新价": row.get('最新价', ''),
                "涨跌幅": row.get('涨跌幅', ''),
                "成交量": row.get('成交量', ''),
                "成交额": row.get('成交额', ''),
                "市盈率": row.get('市盈率-动态', ''),
                "市净率": row.get('市净率', ''),
            })

        content = "# A 股实时行情数据\n\n"
        content += f"数据更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        content += "## 热门股票行情\n\n"

        for stock in top_stocks:
            content += f"### {stock['股票名称']} ({stock['股票代码']})\n"
            content += f"- 最新价: {stock['最新价']}\n"
            content += f"- 涨跌幅: {stock['涨跌幅']}%\n"
            content += f"- 成交量: {stock['成交量']}\n"
            content += f"- 成交额: {stock['成交额']}\n"
            content += f"- 市盈率(PE): {stock['市盈率']}\n"
            content += f"- 市净率(PB): {stock['市净率']}\n\n"

        file_path = MARKET_DATA_DIR / "a_stock_spot.txt"
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"  ✓ 已保存到 {file_path}")
        return True
    except Exception as e:
        print(f"  ✗ 获取失败: {e}")
        return False


def fetch_index_data():
    """获取主要指数数据"""
    print("[2/6] 获取主要指数数据...")
    try:
        df = ak.stock_zh_index_spot_em()
        major_indices = df[df['代码'].isin(['000001', '399001', '399006', '000300', '000016'])]

        content = "# A 股主要指数\n\n"
        content += f"数据更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

        for _, row in major_indices.iterrows():
            content += f"## {row.get('名称', '')} ({row.get('代码', '')})\n"
            content += f"- 最新价: {row.get('最新价', '')}\n"
            content += f"- 涨跌幅: {row.get('涨跌幅', '')}%\n"
            content += f"- 涨跌额: {row.get('涨跌额', '')}\n"
            content += f"- 成交量: {row.get('成交量', '')}\n"
            content += f"- 成交额: {row.get('成交额', '')}\n\n"

        file_path = MARKET_DATA_DIR / "major_indices.txt"
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"  ✓ 已保存到 {file_path}")
        return True
    except Exception as e:
        print(f"  ✗ 获取失败: {e}")
        return False


def fetch_stock_history_sample():
    """获取样本股票历史数据"""
    print("[3/6] 获取样本股票历史数据...")
    try:
        sample_stocks = [
            ("600000", "浦发银行"),
            ("600519", "贵州茅台"),
            ("000001", "平安银行"),
            ("000858", "五粮液"),
        ]

        content = "# 样本股票历史 K 线数据\n\n"
        content += f"数据更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

        for symbol, name in sample_stocks:
            try:
                df = ak.stock_zh_a_hist(symbol=symbol, period="daily",
                                       start_date="20240101", end_date="20240630",
                                       adjust="qfq")
                recent = df.tail(30)

                content += f"## {name} ({symbol})\n\n"
                content += "| 日期 | 开盘 | 收盘 | 最高 | 最低 | 成交量 | 涨跌幅 |\n"
                content += "|------|------|------|------|------|--------|--------|\n"

                for _, row in recent.iterrows():
                    content += f"| {row.get('日期', '')} | {row.get('开盘', '')} | "
                    content += f"{row.get('收盘', '')} | {row.get('最高', '')} | "
                    content += f"{row.get('最低', '')} | {row.get('成交量', '')} | "
                    content += f"{row.get('涨跌幅', '')}% |\n"

                content += "\n"
            except Exception as e:
                print(f"  ! {name} 数据获取失败: {e}")

        file_path = MARKET_DATA_DIR / "stock_history.txt"
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"  ✓ 已保存到 {file_path}")
        return True
    except Exception as e:
        print(f"  ✗ 获取失败: {e}")
        return False


def fetch_macro_data():
    """获取宏观数据"""
    print("[4/6] 获取宏观数据...")
    try:
        content = "# 宏观经济数据\n\n"
        content += f"数据更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

        try:
            cpi_df = ak.macro_china_cpi()
            content += "## 居民消费价格指数 (CPI)\n\n"
            if not cpi_df.empty:
                latest = cpi_df.tail(12)
                for _, row in latest.iterrows():
                    content += f"- {row.get('月份', '')}: {row.get('全国', '')}%\n"
            content += "\n"
        except Exception as e:
            print(f"  ! CPI 数据获取失败: {e}")

        try:
            m2_df = ak.macro_china_m2()
            content += "## 货币供应量 (M2)\n\n"
            if not m2_df.empty:
                latest = m2_df.tail(6)
                for _, row in latest.iterrows():
                    content += f"- {row.get('月份', '')}: {row.get('M2', '')} 万亿元\n"
            content += "\n"
        except Exception as e:
            print(f"  ! M2 数据获取失败: {e}")

        file_path = MARKET_DATA_DIR / "macro_data.txt"
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"  ✓ 已保存到 {file_path}")
        return True
    except Exception as e:
        print(f"  ✗ 获取失败: {e}")
        return False


def fetch_financial_theory():
    """生成金融投资理论文档"""
    print("[5/6] 生成金融投资理论基础文档...")

    theories = {
        "价值投资": """# 价值投资理论

## 核心理念
价值投资由本杰明·格雷厄姆创立，后由沃伦·巴菲特发扬光大。核心思想是：
- 投资于内在价值高于市场价格的股票
- 关注股票的长期价值，而非短期波动
- 安全边际：只在价格低于内在价值时买入

## 关键指标
- 市盈率 (PE): 越低越好，通常 < 20 为佳
- 市净率 (PB): 越低越好，通常 < 1.5 为佳
- 股息率: 越高越好，通常 > 3% 为佳
- 自由现金流: 越高越好

## 经典策略
1. 护城河分析：评估企业的竞争优势
2. 管理层评估：诚信有能力的管理层
3. 长期持有：忽略短期波动，等待价值回归
""",

        "技术分析": """# 技术分析理论

## 核心理念
技术分析认为市场价格反映了所有已知信息，因此通过分析价格走势和交易量可以预测未来走势。

## 主要理论
1. 道氏理论：趋势分析的基础
2. 艾略特波浪理论：价格走势呈5浪上升3浪下跌
3. 江恩理论：时间与价格的关系

## 常用指标
- 移动平均线 (MA): 5日、10日、20日、60日、120日、250日
- 相对强弱指数 (RSI): 超买 > 70，超卖 < 30
- MACD: 指数平滑异同移动平均线
- 布林带: 价格波动的上下轨

## 注意事项
- 技术分析适合短期交易
- 应结合基本面分析使用
- 注意量价配合
""",

        "趋势投资": """# 趋势投资理论

## 核心理念
趋势投资认为应该"顺势而为"，在上升趋势中买入，在下降趋势中卖出。

## 趋势判断
1. 上升趋势：高点不断抬高，低点也不断抬高
2. 下降趋势：高点不断降低，低点也不断降低
3. 横盘整理：高低点基本水平

## 策略要点
- 趋势线画法：连接两个以上的低点或高点
- 突破确认：收盘价突破趋势线视为信号
- 止损设置：在趋势线下方设止损

## 风险控制
- 永远不要逆势操作
- 及时止损，避免大亏
- 轻仓顺势，稳健盈利
""",

        "量化投资": """# 量化投资理论

## 概念
量化投资使用数学模型和计算机程序进行投资决策，特点是：
- 系统性：基于固定规则
- 纪律性：严格执行策略
- 可复制性：策略可大规模执行

## 主要策略
1. 阿尔法策略：寻找超额收益
2. 贝塔策略：跟踪指数获取市场收益
3. 多因子模型：利用多个因子选股
4. 高频交易：利用微小价格波动获利

## 常用因子
- 价值因子：PE、PB、PS
- 成长因子：营收增速、利润增速
- 质量因子：ROE、资产负债率
- 动量因子：过去收益率
- 规模因子：市值大小

## 风险提示
- 模型过拟合风险
- 市场风格切换风险
- 流动性风险
"""
    }

    for name, content in theories.items():
        file_path = FINANCIAL_THEORY_DIR / f"{name}.txt"
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

    print(f"  ✓ 已生成 {len(theories)} 个理论文档")
    return True


def generate_sample_research_report():
    """生成样本研报"""
    print("[6/6] 生成样本研报...")

    reports = [
        {
            "filename": "银行行业深度报告.txt",
            "title": "银行行业深度报告：估值修复与业绩增长",
            "content": """# 银行行业深度报告

## 行业概述
银行业是我国金融体系的核心，资产规模庞大。2024年以来，银行板块估值持续低位，具备配置价值。

## 核心观点
1. **估值低位**：银行板块PB仅为0.6倍，处于历史底部
2. **业绩稳定**：息差企稳回升，业绩增长稳健
3. **政策支持**：资本市场改革利好银行
4. **分红丰厚**：多家银行股息率超过5%

## 重点标的
- **招商银行**：零售业务领先，资产质量优
- **宁波银行**：区域龙头，成长性突出
- **工商银行**：大行稳健，股息率最高

## 风险提示
- 资产质量恶化风险
- 净息差收窄风险
- 政策调控风险
"""
        },
        {
            "filename": "新能源汽车行业报告.txt",
            "title": "新能源汽车行业：电动化趋势不可逆",
            "content": """# 新能源汽车行业研究报告

## 行业趋势
1. 电动化率持续提升，2024年有望突破40%
2. 插混车型快速增长，成为重要增量
3. 出口市场持续扩大

## 竞争格局
- 比亚迪：全产业链优势，销量领先
- 特斯拉：品牌与技术优势
- 新势力：蔚来、小鹏、理想

## 投资建议
- 整车：关注产品力强、销量增长快的车企
- 零部件：电池产业链、智能驾驶
- 充换电：充电桩、换电站运营

## 风险提示
- 价格战加剧
- 原材料价格波动
- 政策退坡
"""
        }
    ]

    for report in reports:
        file_path = RESEARCH_REPORTS_DIR / report["filename"]
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(report["content"])

    print(f"  ✓ 已生成 {len(reports)} 篇样本研报")
    return True


def main():
    print("=" * 60)
    print("AKShare 金融数据采集")
    print("=" * 60)
    print()

    results = []
    results.append(("A股实时行情", fetch_stock_spot_data()))
    results.append(("主要指数", fetch_index_data()))
    results.append(("股票历史", fetch_stock_history_sample()))
    results.append(("宏观数据", fetch_macro_data()))
    results.append(("投资理论", fetch_financial_theory()))
    results.append(("样本研报", generate_sample_research_report()))

    print()
    print("=" * 60)
    print("采集完成！")
    print("=" * 60)
    for name, success in results:
        status = "✓ 成功" if success else "✗ 失败"
        print(f"  {name}: {status}")

    print()
    print(f"数据已保存到: {MARKET_DATA_DIR}")
    print(f"研报已保存到: {RESEARCH_REPORTS_DIR}")
    print(f"理论已保存到: {FINANCIAL_THEORY_DIR}")


if __name__ == "__main__":
    main()
