import akshare as ak
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
from fasthtml.common import serve, fast_app
from fh_plotly import plotly_headers, plotly2fasthtml
import asyncio
import os
from data_fetcher import get_index_data, save_data_to_csv, process_highdays_data

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
    # 添加处理 highdays 数据的调用
    process_highdays_data()

# 修改主页面函数,从CSV读取数据
@rt('/')
def index():
    # 检查所有必要的 CSV 文件是否存在
    required_files = ['index_changes.csv', 'index_trading_amounts.csv', 'highdays_counts.csv']
    missing_files = [file for file in required_files if not os.path.exists(file)]
    
    if missing_files:
        return f"以下数据文件不存在: {', '.join(missing_files)}。请先访问 /fetch_data 接口抓取数据"
    
    try:
        # 读取数据
        change_df = pd.read_csv('index_changes.csv')
        amount_df = pd.read_csv('index_trading_amounts.csv')
        highdays_df = pd.read_csv('highdays_counts.csv')
        
        # 创建图表
        change_chart = create_line_chart(change_df, '指数涨跌幅走势', '涨跌幅 (%)', x_column='日期')
        amount_chart = create_line_chart(amount_df, '指数成交额走势', '成交额', x_column='日期')
        highdays_chart = create_line_chart(highdays_df, '每日连续涨停天数分布', '股票数量', x_column='date')
        
        return [
            change_chart,
            amount_chart,
            highdays_chart
        ]
    except Exception as e:
        return f"读取或处理数据时出错: {str(e)}"

# 修改绘图函数
def create_line_chart(df, title, y_axis_title, x_column='date'):
    fig = px.line(df, x=x_column, y=df.columns[df.columns != x_column], title=title)
    fig.update_layout(yaxis_title=y_axis_title)
    return plotly2fasthtml(fig)

serve()