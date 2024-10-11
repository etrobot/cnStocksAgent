import akshare as ak
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
from fasthtml.common import serve, fast_app, Div, H2, P
from fh_plotly import plotly_headers, plotly2fasthtml
import asyncio
import os
from data_fetcher import get_index_data, get_currency_data, fetch_and_save_limit_up_data

# 创建FastHTML应用
app, rt = fast_app(hdrs=plotly_headers)

# 添加新的API函数来抓取数据并保存CSV
@rt('/fetch_data')
async def fetch_data_api():
    asyncio.create_task(fetch_and_save_data())
    return "数据抓取已开始,请稍后查看结果"

async def fetch_and_save_data():
    get_index_data()
    get_currency_data()
    fetch_and_save_limit_up_data()

# 修改主页面函数,从CSV读取数据
@rt('/')
def index():
    charts = []
    messages = []

    data_files = [
        ('index_changes.csv', '指数涨跌幅走势', '涨跌幅 (%)'),
        ('index_trading_amounts.csv', '指数成交额走势', '成交额'),
        ('currency_mid_prices.csv', '近两年央行中间价走势', '央行中间价 (元)'),
        ('limit_up_summary.csv', '每日连板次数汇总', '股票个数')
    ]

    def parse_date(date_str):
        for fmt in ('%Y-%m-%d', '%Y%m%d'):
            try:
                return pd.to_datetime(date_str, format=fmt)
            except ValueError:
                pass
        raise ValueError(f"无法解析日期: {date_str}")

    for file_name, title, y_axis_title in data_files:
        try:
            df = pd.read_csv(file_name)
            date_column = '日期' if '日期' in df.columns else 'date'
            
            # 使用自定义函数解析日期
            df[date_column] = df[date_column].apply(parse_date)
            
            df.set_index(date_column, inplace=True)
            df.index = pd.to_datetime(df.index)
            chart = create_line_chart(df, title, y_axis_title)
            charts.append(chart)
        except FileNotFoundError:
            messages.append(Div(H2(title), P(f"{file_name} 文件不存在")))
        except Exception as e:
            messages.append(Div(H2(title), P(f"处理 {file_name} 时出错: {str(e)}")))

    if not charts:
        messages.append(Div(H2("数据图表"), P("没有可用的数据来生成图表")))

    return charts + messages

# 修改绘图函数
def create_line_chart(df, title, y_axis_title):
    fig = px.line(df, title=title)
    fig.update_layout(yaxis_title=y_axis_title, xaxis_title='日期')
    return plotly2fasthtml(fig)

def plot_summary_line_chart(summary_df):
    # 使用 Plotly 绘制折线图
    fig = px.line(
        summary_df,
        x='date',
        y=['continue_2', 'continue_3', 'continue_4', 'continue_5', 'continue_6', 'continue_7', 'continue_7plus'],
        title='每日连板次数汇总',
        labels={'value': '股票个数', 'variable': '连板次数'}
    )
    fig.update_layout(xaxis_title='日期', yaxis_title='股票个数')
    return plotly2fasthtml(fig)

serve()