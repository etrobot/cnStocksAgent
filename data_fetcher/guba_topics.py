from datetime import datetime, timedelta
import akshare as ak
import pandas as pd
import requests

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

print(eastmoney_topics())