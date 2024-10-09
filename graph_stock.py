import akshare as ak
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
from fasthtml.common import serve, fast_app
from fh_plotly import plotly_headers, plotly2fasthtml

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

# 获取指数数据
merged_df = get_index_data()

# 创建涨跌幅表
change_df = merged_df[['date', 'sh000300_change', 'sh000905_change', 'sh000852_change']]
change_df.columns = ['日期', '沪深300涨跌幅', '中证500涨跌幅', '中证1000涨跌幅']

# 创建成交额表
amount_df = merged_df[['date', 'sh000300_amount', 'sh000905_amount', 'sh000852_amount']]
amount_df.columns = ['日期', '沪深300成交额', '中证500成交额', '中证1000成交额']

# 添加绘图函数
def create_line_chart(df, title, y_axis_title):
    fig = px.line(df, x='日期', y=df.columns[1:], title=title)
    fig.update_layout(yaxis_title=y_axis_title)
    return plotly2fasthtml(fig)

# 创建FastHTML应用
app, rt = fast_app(hdrs=plotly_headers)

@rt('/')  # Change this line
def index():
    # 创建涨跌幅折线图
    change_chart = create_line_chart(change_df, '指数涨跌幅走势', '涨跌幅 (%)')
    
    # 创建成交额折线图
    amount_chart = create_line_chart(amount_df, '指数成交额走势', '成交额')
    
    return [
        change_chart,
        amount_chart
    ]

# 保存到CSV文件
change_df.to_csv('index_changes.csv', index=False, encoding='utf-8-sig')
amount_df.to_csv('index_trading_amounts.csv', index=False, encoding='utf-8-sig')

print("数据已保存到 index_changes.csv 和 index_trading_amounts.csv 文件中。")

serve()