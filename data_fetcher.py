import akshare as ak
import pandas as pd
from datetime import datetime, timedelta
import requests
import os
from tqdm import tqdm

# 定义 headers
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36',
    'Accept': 'application/json',
}

def get_default_dates(start_date=None, end_date=None):
    if end_date is None:
        end_date = datetime.now()
    if start_date is None:
        start_date = end_date - timedelta(days=365*2)
    return start_date, end_date

def download_index_data(index_codes, start_date=None, end_date=None):
    start_date, end_date = get_default_dates(start_date, end_date)
    data = {}
    for code in index_codes:
        df = ak.stock_zh_index_daily_em(symbol=code)
        df['date'] = pd.to_datetime(df['date'])
        df = df[['date', 'close', 'amount']]
        df.columns = ['date', f'{code}_close', f'{code}_amount']
        data[code] = df
    return data

def get_index_data():
    start_date, end_date = get_default_dates()
    
    index_codes = ["sh000300", "sh000905", "sh000852"]
    data = download_index_data(index_codes, start_date, end_date)
    
    merged_df = data[index_codes[0]]
    for code in index_codes[1:]:
        merged_df = pd.merge(merged_df, data[code], on='date', how='outer')

    merged_df = merged_df.sort_values('date')

    for code in index_codes:
        base_price = merged_df[f'{code}_close'].iloc[0]
        merged_df[f'{code}_change'] = (merged_df[f'{code}_close'] / base_price - 1) * 100

    # 保存涨跌幅数据
    change_df = merged_df[['date', 'sh000300_change', 'sh000905_change', 'sh000852_change']]
    change_df.columns = ['日期', '沪深300涨跌幅', '中证500涨跌幅', '中证1000涨跌幅']
    change_df.to_csv('index_changes.csv', index=False, encoding='utf-8-sig')

    # 保存成交额数据
    amount_df = merged_df[['date', 'sh000300_amount', 'sh000905_amount', 'sh000852_amount']]
    amount_df.columns = ['日期', '沪深300成交额', '中证500成交额', '中证1000成交额']
    amount_df.to_csv('index_trading_amounts.csv', index=False, encoding='utf-8-sig')

    print("数据已保存到 index_changes.csv 和 index_trading_amounts.csv 文件中。")

    return merged_df

def akshareK(index_code='sh000001'):
    idx_df = ak.stock_zh_index_daily(symbol=index_code)
    idx_df['date'] = pd.to_datetime(idx_df['date'])
    idx_df.set_index('date', inplace=True)
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
        'Referer': 'https://data.10jqka.com.cn.cn/datacenterph/limitup/limtupInfo.html',
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

def updateLimits(start_date='20231231'):
    csv_file = 'uplimit10jqka.csv'
    
    if os.path.exists(csv_file) and os.path.getsize(csv_file) > 0:
        df = pd.read_csv(csv_file)
        df['date'] = pd.to_datetime(df['date'])
        dfDates = df['date'].values
    else:
        df = pd.DataFrame(columns=['name', 'code', 'change_rate', 'latest', 'reason_type', 'high_days', 'is_again_limit', 'currency_value', 'date'])
        dfDates = [pd.to_datetime(start_date) - pd.Timedelta(days=1)]

    idx = akshareK('sh000001')
    idx = idx.sort_index()
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

def get_currency_data(symbol="美元", save_to_csv=True, start_date=None, end_date=None):
    start_date, end_date = get_default_dates(start_date, end_date)
    start_date_str = start_date.strftime("%Y%m%d")
    end_date_str = end_date.strftime("%Y%m%d")
    
    currency_df = ak.currency_boc_sina(symbol=symbol, start_date=start_date_str, end_date=end_date_str)
    currency_df = currency_df[['日期', '央行中间价']]
    currency_df['央行中间价'] = currency_df['央行中间价'] / 100

    if save_to_csv:
        csv_filename = 'currency_mid_prices.csv'
        currency_df.to_csv(csv_filename, index=False, encoding='utf-8-sig')
        print(f"数据已保存到 {csv_filename} 文件中。")

    return currency_df

def fetch_limit_up_data(date):
    cookies = {
        'v': 'A_qep1WoSX1KS8URSL2E8wAGTSIZq39q8CzyKQTzpahYsJQV7DvOlcC_QirX',
    }
    url = f'https://data.10jqka.com.cn/dataapi/limit_up/continuous_limit_up?filter=HS,GEM2STAR&date={date}'
    response = requests.get(url, headers=headers, cookies=cookies)
    
    if response.status_code == 200:
        data = response.json()
        if data["status_code"] == 0:
            df = pd.json_normalize(data['data'], record_path='code_list', meta=['height', 'number'])
            df['date'] = date
            return df
    return None

def fetch_and_save_limit_up_data(start_date=None, end_date=None):
    start_date, end_date = get_default_dates(start_date, end_date)
    end_date_str = end_date.strftime('%Y%m%d')
    
    csv_file = 'limit_up_data.csv'
    summary_csv_file = 'limit_up_summary.csv'
    
    if os.path.exists(csv_file) and os.path.getsize(csv_file) > 0:
        existing_df = pd.read_csv(csv_file)
        existing_df['date'] = pd.to_datetime(existing_df['date'])
        last_date = existing_df['date'].max()
        start_date = last_date + timedelta(days=1)
    else:
        existing_df = pd.DataFrame()
    
    start_date_str = start_date.strftime('%Y%m%d')
    
    print(f"正在获取从 {start_date_str} 到 {end_date_str} 的数据")
    
    trading_days = ak.stock_zh_index_daily_em(symbol="sh000001", start_date=start_date_str, end_date=end_date_str)
    trading_days['date'] = pd.to_datetime(trading_days['date'])
    trading_days = trading_days['date'].dt.strftime('%Y%m%d').tolist()
    
    new_data = []
    for trading_day in tqdm(trading_days, desc="获取数据进度"):
        daily_data = fetch_limit_up_data(trading_day)
        if daily_data is not None:
            new_data.append(daily_data)

    if new_data:
        new_df = pd.concat(new_data, ignore_index=True)
        big_df = pd.concat([existing_df, new_df], ignore_index=True)
        big_df.to_csv(csv_file, index=False)

        summary_df = big_df.groupby(['date', 'continue_num']).size().unstack(fill_value=0)
        summary_df['continue_7plus'] = summary_df.loc[:, 7:].sum(axis=1)
        summary_df = summary_df.reindex(columns=[2, 3, 4, 5, 6, 7, 'continue_7plus'], fill_value=0)
        summary_df.columns = ['continue_2', 'continue_3', 'continue_4', 'continue_5', 'continue_6', 'continue_7', 'continue_7plus']
        summary_df = summary_df.reset_index()

        summary_df.to_csv(summary_csv_file, index=False)
        
        print(f"原始数据已保存到: {csv_file}")
        print(f"汇总表已保存到: {summary_csv_file}")
    else:
        print("未获取到新数据。")
