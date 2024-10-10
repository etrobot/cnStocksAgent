import akshare as ak
import pandas as pd
from datetime import datetime, timedelta
import requests
import os
from tqdm import tqdm

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
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365*2)
    
    index_codes = ["sh000300", "sh000905", "sh000852"]
    data = download_index_data(index_codes, start_date, end_date)
    
    merged_df = data[index_codes[0]]
    for code in index_codes[1:]:
        merged_df = pd.merge(merged_df, data[code], on='date', how='outer')

    merged_df = merged_df.sort_values('date')

    for code in index_codes:
        base_price = merged_df[f'{code}_close'].iloc[0]
        merged_df[f'{code}_change'] = (merged_df[f'{code}_close'] / base_price - 1) * 100

    return merged_df

def save_data_to_csv(merged_df):
    change_df = merged_df[['date', 'sh000300_change', 'sh000905_change', 'sh000852_change']]
    change_df.columns = ['日期', '沪深300涨跌幅', '中证500涨跌幅', '中证1000涨跌幅']

    amount_df = merged_df[['date', 'sh000300_amount', 'sh000905_amount', 'sh000852_amount']]
    amount_df.columns = ['日期', '沪深300成交额', '中证500成交额', '中证1000成交额']

    change_df.to_csv('index_changes.csv', index=False, encoding='utf-8-sig')
    amount_df.to_csv('index_trading_amounts.csv', index=False, encoding='utf-8-sig')

    print("数据已保存到 index_changes.csv 和 index_trading_amounts.csv 文件中。")

def akshareK(index_code='sh000001'):
    # Use akshare to get index data
    idx_df = ak.stock_zh_index_daily(symbol=index_code)
    
    # 将日期列转换为datetime类型并设置为索引
    idx_df['date'] = pd.to_datetime(idx_df['date'])
    idx_df.set_index('date', inplace=True)
    
    # 按日期排序
    idx_df.sort_index(inplace=True)
    
    return idx_df

def uplimit10jqka(date:str='20231231'):
    cookies = {
        'v': 'AxF1-gKdEiRmQH4wnowvhu8rJh-ufoXwL_IpBPOmDVj3mj_IO86VwL9COdCA',
    }

    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-Dest': 'empty',
        'Accept-Language': 'en-GB,en;q=0.9',
        'Sec-Fetch-Mode': 'cors',
        'Host': 'data.10jqka.com.cn',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15',
        'Referer': 'https://data.10jqka.com.cn/datacenterph/limitup/limtupInfo.html',
        'Connection': 'keep-alive',
    }

    params = {
        'page': '1',
        'limit': '200',
        'field': '199112,10,9001,330323,330324,330325,9002,330329,133971,133970,1968584,3475914,9003,9004',
        'filter': 'HS,GEM2STAR',
        'order_field': '330324',
        'order_type': '0',
        'date': date,
        '_': '1728380378175',
    }

    response = requests.get(
        'https://data.10jqka.com.cn/dataapi/limit_up/limit_up_pool',
        params=params,
        cookies=cookies,
        headers=headers,
    )
    result = response.json()['data']['info']
    df = pd.DataFrame(result)
    return df

# Main function to update limits and use akshare for fetching index data
def updateLimits(start_date='20231231'):
    # 使用CSV文件替代SQLite数据库
    csv_file = 'uplimit10jqka.csv'
    
    # 如果CSV文件存在且不为空,读取数据;否则创建一个空的DataFrame
    if os.path.exists(csv_file) and os.path.getsize(csv_file) > 0:
        df = pd.read_csv(csv_file)
        df['date'] = pd.to_datetime(df['date'])
        dfDates = df['date'].values
    else:
        df = pd.DataFrame(columns=['name', 'code', 'change_rate', 'latest', 'reason_type', 'high_days', 'is_again_limit', 'currency_value', 'date'])
        dfDates = [pd.to_datetime(start_date) - pd.Timedelta(days=1)]  # 设置为起始日期的前一天

    # 使用akshare获取指数数据
    idx = akshareK('sh000001')
    idx = idx.sort_index()
    # 如果有新的指数数据,更新CSV文件
    if idx.index.values[-1] > dfDates[-1]:
        idxDates = idx[idx.index > dfDates[-1]].index.strftime('%Y%m%d')
        new_data = []
        for k in tqdm(idxDates):
            ldf = uplimit10jqka(k)
            ldf = ldf[['name', 'code', 'change_rate', 'latest', 'reason_type', 'high_days', 'is_again_limit', 'currency_value']]
            ldf['date'] = k
            ldf = ldf.fillna('')
            new_data.append(ldf)
        
        if new_data:
            new_df = pd.concat(new_data, ignore_index=True)
            df = pd.concat([df, new_df], ignore_index=True)
            df.to_csv(csv_file, index=False)

def process_highdays_data():
    csv_file = 'uplimit10jqka.csv'
    if not os.path.exists(csv_file):
        updateLimits()
    
    # 读取CSV文件
    df = pd.read_csv(csv_file)
    
    # 将日期列转换为datetime类型
    df['date'] = pd.to_datetime(df['date'], format='%Y%m%d')
    
    # 按股票代码和日期排序
    df = df.sort_values(['code', 'date'])

    # 计算连续涨停天数
    df['consecutive_limit_up'] = df.groupby('code').cumcount() + 1
    df['consecutive_limit_up'] = df.groupby('code')['consecutive_limit_up'].transform(
        lambda x: x.where((x != x.shift()).cumsum() == x.cumsum(), 1)
    )

    # 统计每日不同连续涨停天数的股票数量
    highdays_counts = df.groupby(['date', 'consecutive_limit_up']).size().unstack(fill_value=0)

    # 只保留连续涨停天数为 1 到 10 的列，如果存在的话
    valid_columns = [col for col in range(1, 11) if col in highdays_counts.columns]
    highdays_counts = highdays_counts.loc[:, valid_columns]

    # 重命名列
    highdays_counts.columns = [f'highdays_{i}' for i in valid_columns]

    # 对于缺失的列，添加全为0的列
    for i in range(1, 11):
        if f'highdays_{i}' not in highdays_counts.columns:
            highdays_counts[f'highdays_{i}'] = 0

    # 按列名排序
    highdays_counts = highdays_counts.sort_index(axis=1)

    # 保存处理后的原始数据
    df.to_csv('processed_uplimit10jqka.csv', index=False, date_format='%Y-%m-%d')
    print("处理后的涨停数据已保存到 processed_uplimit10jqka.csv 文件中。")

    # 保存统计数据
    highdays_counts.to_csv('highdays_counts.csv', date_format='%Y-%m-%d')
    print("Highdays 统计数据已保存到 highdays_counts.csv 文件中。")

    # 打印 highdays_counts 的前几行，用于调试
    print("Highdays counts preview:")
    print(highdays_counts.head())

    # 检查是否有非零值
    if highdays_counts.sum().sum() == 0:
        print("警告：highdays_counts 中所有值都为零。请检查原始数据。")

    return highdays_counts

# 如果直接运行此脚本，则执行 process_highdays_data 函数
if __name__ == "__main__":
    process_highdays_data()