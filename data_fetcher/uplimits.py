import requests
import pandas as pd
import akshare as ak
from datetime import datetime, timedelta

REF='https://data.10jqka.com.cn/datacenterph/limitup/limtupInfo.html'

def get_default_dates(start_date=None, end_date=None):
    if end_date is None:
        end_date = datetime.now()
    if start_date is None:
        start_date = end_date - timedelta(days=7*2)
    return start_date, end_date

def get_trading_days(start_date=None, end_date=None):
    start_date, end_date = get_default_dates()
    trading_days = ak.stock_zh_index_daily_em(symbol="sh000001", start_date=start_date.strftime('%Y%m%d'), end_date=end_date.strftime('%Y%m%d'))
    trading_days = pd.to_datetime(trading_days['date']).dt.strftime('%Y%m%d').tolist()
    return trading_days

def fetch_continuous_up_limit_data(date=None):
    if date is None:
        date = get_trading_days()[-1]
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
            
            # Fetch additional data from uplimit10jqka
            uplimit_data = uplimit10jqka(date)
            
            # Merge the two dataframes based on 'code' field
            merged_df = pd.merge(df, uplimit_data, left_on='code', right_on='code', how='left')
            output = merged_df[['code','name_x','continue_num','limit_up_type','reason_type']]
            # Save the merged dataframe as CSV
            csv_filename = f'continuous_up_limit_data.csv'
            output.to_csv(csv_filename, index=False, encoding='utf_8_sig')            
            print(f"Data saved to {csv_filename}")

            return output.to_csv()
    return None

def uplimit10jqka(date=None):
    if date is None:
        date = get_trading_days()[-1]
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
        'Referer': REF,
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

if __name__ == "__main__":
    fetch_continuous_up_limit_data()