import os
import requests
import akshare as ak
import pandas as pd
from tqdm import tqdm
from datetime import datetime, timedelta


def akshareK(index_code='sh000001'):
    idx_df = ak.stock_zh_index_daily(symbol=index_code)
    idx_df['date'] = pd.to_datetime(idx_df['date'])
    idx_df.set_index('date', inplace=True)
    idx_df.sort_index(inplace=True)
    return idx_df

def get_default_dates(start_date=None, end_date=None):
    if end_date is None:
        end_date = datetime.now()
    if start_date is None:
        start_date = end_date - timedelta(days=365*2)
    return start_date, end_date


def eastmoney_topics():
    headers = {
        'User-Agent': 'Mozilla',
        'Referer': 'https://gubatopic.eastmoney.com/',
    }
    url = 'https://gubatopic.eastmoney.com/interface/GetData.aspx?path=newtopic/api/Topic/HomePageListRead'
    data = {
        'param': 'ps=10&p=1&type=0',
        'path': 'newtopic/api/Topic/HomePageListRead',
        'env': '2',
    }

    response = requests.post(url, headers=headers, data=data)

    if response.status_code != 200:
        print(f"请求失��，状态码: {response.status_code}")
        return None

    api_data = response.json()

    parsed_results = []
    added_stocks = set()
    for item in api_data.get('re', []):
        title = item.get('nickname', '无标题')
        desc = item.get('desc', '无描述')
        stocks = item.get('stock_list', [])

        related_stocks = []
        for stock in stocks:
            name = stock.get('name', '未知股票')
            qcode = stock.get('qcode', '未知代码')
            stock_info = f"{qcode}{name}"
            if stock_info not in added_stocks:
                related_stocks.append(stock_info)
                added_stocks.add(stock_info)

        related_stocks_str = " ".join(related_stocks) if related_stocks else "无关联股票"

        paragraph = f"### {title}\n{desc}\n关联股：{related_stocks_str}\n"
        parsed_results.append(paragraph)

    return "\n".join(parsed_results)

def fetch_continuous_up_limit_data(date):
    cookies = {
        'v': 'A_qep1WoSX1KS8URSL2E8wAGTSIZq39q8CzyKQTzpahYsJQV7DvOlcC_QirX',
    }
    url = f'https://data.10jqka.com.cn/dataapi/limit_up/continuous_limit_up?filter=HS,GEM2STAR&date={date}'
    response = requests.get(url, headers={'User-Agent':'Mozilla'}, cookies=cookies)
    
    if response.status_code == 200:
        data = response.json()
        if data["status_code"] == 0:
            df = pd.json_normalize(data['data'], record_path='code_list', meta=['height', 'number'])
            df['date'] = date
            return df
    return None

def continuous_up_limit_data(start_date=None, end_date=None):
    start_date, end_date = get_default_dates(start_date, end_date)
    end_date_str = end_date.strftime('%Y%m%d')
    
    csv_file = 'continuous_up_limit_data.csv'
    if os.path.exists(csv_file) and os.path.getsize(csv_file) > 0:
        existing_df = pd.read_csv(csv_file,dtype={'code': str})
        existing_df['date'] = pd.to_datetime(existing_df['date'], format='%Y%m%d')
        last_date = existing_df['date'].max()
        start_date = last_date + timedelta(days=1)
        print(f"已找现有数据，最后更新日期为 {last_date.strftime('%Y%m%d')}")
    else:
        existing_df = pd.DataFrame()
        print("未找到现有数据，将创建新的数据文件")

    start_date_str = start_date.strftime('%Y%m%d')
    if start_date > end_date:
        calculate_upscore(existing_df)
        print("数据已是最新，无需更新")
        return

    print(f"正在获取从 {start_date_str} 到 {end_date_str} 的数据")
    
    trading_days = ak.stock_zh_index_daily_em(symbol="sh000001", start_date=start_date_str, end_date=end_date_str)
    trading_days['date'] = pd.to_datetime(trading_days['date'])
    trading_days = trading_days['date'].dt.strftime('%Y%m%d').tolist()
    
    total_new_rows = 0
    for trading_day in tqdm(trading_days, desc="获取数据进度"):
        daily_data = fetch_continuous_up_limit_data(trading_day)
        if daily_data is not None and not daily_data.empty:
            daily_data.to_csv(csv_file, mode='a', header=not os.path.exists(csv_file), index=False, encoding='utf_8_sig')
            total_new_rows += len(daily_data)

    if total_new_rows > 0:
        print(f"数据更新完成。总共添加了 {total_new_rows} 行新数据到: {csv_file}")
    else:
        print("未获取到新数据。")

    # 验证最终的CSV文件
    if os.path.exists(csv_file):
        final_df = pd.read_csv(csv_file, dtype={'code': str})
        calculate_upscore(final_df)
               

def calculate_upscore(df):
    df['code'] = df['code'].astype(str)
    
    upscore_df = df.groupby('code').agg({
        'continue_num': 'sum',
        'name': 'first'
    }).reset_index()
    
    # 对于以300和688开头的股票，continue_num乘以2
    upscore_df['upscore'] = upscore_df.apply(
        lambda row: row['continue_num'] * 2 if row['code'].startswith(('300', '688')) else row['continue_num'],
        axis=1
    )
    
    # 按upscore从大到小排序
    upscore_df = upscore_df.sort_values('upscore', ascending=False)[['code', 'name', 'upscore']]
    upscore_csv_file = 'upscore_data.csv'
    upscore_df.to_csv(upscore_csv_file, index=False,encoding='utf_8_sig')
    print(f"upscore数据已保存到: {upscore_csv_file}")


if __name__ == "__main__":
    continuous_up_limit_data(start_date=datetime(2024, 9, 1))