import akshare as ak
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
from fasthtml.common import serve, fast_app
from fh_plotly import plotly_headers, plotly2fasthtml
import asyncio
import os
from data_fetcher import get_index_data, save_data_to_csv

# 创建FastHTML应用
app, rt = fast_app(hdrs=plotly_headers)

def download_index_data(index_codes, start_date, end_date):
    data = {}
    for code in index_codes:
        df = ak.stock_zh_index_daily_em(symbol=code)
        df['date'] = pd.to_datetime(df['date'])
        df = df[(df['date'] >= start_date) & (df['date'] <= end_date)]
        df = df[['date', 'close', 'amount']]
        df.columns = ['date', f'{code}_close', f'{code}_amount']
        data[code] = df
    return data

def get_index_data():
    # 计算两年前的日期
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365*2)
    
    index_codes = ["sh000300", "sh000905", "sh000852"]
    data = download_index_data(index_codes, start_date, end_date)
    
    # 合并数据
    merged_df = data[index_codes[0]]
    for code in index_codes[1:]:
        merged_df = pd.merge(merged_df, data[code], on='date', how='outer')

    # 按日期排序
    merged_df = merged_df.sort_values('date')

    # 计算涨跌幅
    for code in index_codes:
        base_price = merged_df[f'{code}_close'].iloc[0]
        merged_df[f'{code}_change'] = (merged_df[f'{code}_close'] / base_price - 1) * 100

    return merged_df

# 添加新的API函数来抓取数据并保存CSV
@rt('/fetch_data')
async def fetch_data_api():
    asyncio.create_task(fetch_and_save_data())
    return "数据抓取已开始,请稍后查看结果"

async def fetch_and_save_data():
    merged_df = get_index_data()
    save_data_to_csv(merged_df)

# 修改主页面函数,从CSV读取数据
@rt('/')
def index():
    # 检查CSV文件是否存在
    if not os.path.exists('index_changes.csv') or not os.path.exists('index_trading_amounts.csv'):
        # 如果文件不存在,返回提示信息
        return "数据文件不存在,请先访问 /fetch_data 接口抓取数据"
    
    try:
        # 尝试从CSV读取数据
        change_df = pd.read_csv('index_changes.csv')
        amount_df = pd.read_csv('index_trading_amounts.csv')
        
        # 创建涨跌幅折线图
        change_chart = create_line_chart(change_df, '指数涨跌幅走势', '涨跌幅 (%)')
        
        # 创建成交额折线图
        amount_chart = create_line_chart(amount_df, '指数成交额走势', '成交额')
        
        return [
            change_chart,
            amount_chart
        ]
    except Exception as e:
        # 如果读取或处理数据时出错,返回错误信息
        return f"读取或处理数据时出错: {str(e)}"

# 添加绘图函数
def create_line_chart(df, title, y_axis_title):
    fig = px.line(df, x='日期', y=df.columns[1:], title=title)
    fig.update_layout(yaxis_title=y_axis_title)
    return plotly2fasthtml(fig)

serve()