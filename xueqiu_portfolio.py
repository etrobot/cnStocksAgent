import requests,json,re
from datetime import *
import os
from dotenv import load_dotenv
from graph_reviewer import reviewAgent

load_dotenv()


def xqStockInfo(mkt, code:str, s, h):  # 雪球股票信息
    code=code.upper()
    data = {
        'code': str(code),
        'size': '30',
        # 'key': '47bce5c74f',
        'market': mkt,
    }
    r = s.get("https://xueqiu.com/stock/p/search.json", headers=h, params=data)
    print(code,r.text)
    stocks = json.loads(r.text)
    stocks = stocks['stocks']
    stock = None
    if len(stocks) > 0:
        for info in stocks:
            if info['code']==code:
                return info
    return stock

class xueqiuPortfolio():
    def __init__(self,mkt,portfolio_code):
        self.portfolio_code = portfolio_code
        self.mkt = mkt
        self.position = dict()
        self.holdnum = 5
        self.session = requests.Session()
        self.session.cookies.update(self.getXueqiuCookie())
        self.p_url = 'https://xueqiu.com/P/'+portfolio_code
        self.headers = {
            "Connection": "close",
             "user-agent": "Mozilla",
        }


    def getXueqiuCookie(self):
        sbCookie = open('cookies.txt','r').read()
        cookie_dict = {}
        for record in sbCookie.split(";"):
            key, value = record.strip().split("=", 1)
            if 'utm' in key:
                continue
            cookie_dict[key] = value
        for k,v in requests.get('https://xueqiu.com',headers={'user-agent':'Mozilla'}).cookies.get_dict().items():
            cookie_dict[k]=v
        return cookie_dict

    def trade(self,position_list=None):  # 调仓雪球组合
        if position_list is None:
            return
        remain_weight = 100 - sum(x.get('weight') for x in position_list)
        cash = round(remain_weight, 2)
        data = {
            "cash": cash,
            "holdings": str(json.dumps(position_list)),
            "cube_symbol": str(self.portfolio_code),
            'segment': 'true',
            'comment': ""
        }
        try:
            resp = self.session.post("https://xueqiu.com/cubes/rebalancing/create.json", headers=self.headers, data=data)
        except Exception as e:
            return {'error': '调仓失败: %s ' % e}
        else:
            return resp.json()
           

    def getPosition(self):
        if len(self.position)>0:
            return self.position
        resp = self.session.get(self.p_url, headers=self.headers).text.replace('null','0')
        portfolio_info = json.loads(re.search(r'(?<=SNB.cubeInfo = ).*(?=;\n)', resp).group())
        asset_balance = float(portfolio_info['net_value'])
        position = portfolio_info['view_rebalancing']
        cash = asset_balance * float(position['cash'])  # 可用资金
        self.position['holding']=position['holdings']
        self.position['cash']=int(cash)
        self.position['last']=portfolio_info['last_success_rebalancing']['holdings']
        self.position['update']=datetime.fromtimestamp(position['updated_at']/1000).date()
        self.position['latest']=portfolio_info['sell_rebalancing']
        self.position['last']=portfolio_info['last_success_rebalancing']
        self.position['monthly_gain']=portfolio_info['monthly_gain']
        self.position['total_gain'] = portfolio_info['total_gain']
        return self.position

    def newPostition(self,mkt,symbol,wgt):
        stock = xqStockInfo(mkt, symbol, self.session, self.headers)
        return {
            "code": stock['code'],
            "name": stock['name'],
            "flag": stock['flag'],
            "current": stock['current'],
            "chg": stock['chg'],
            "stock_id": stock['stock_id'],
            "ind_id": stock['ind_id'],
            "ind_name": stock['ind_name'],
            "ind_color": stock['ind_color'],
            "textname": stock['name'],
            "segment_name": stock['ind_name'],
            "weight": wgt,  # 在这里自定义买入仓位,范围0.01到1
            "url": "/S/" + stock['code'],
            "proactive": True,
            "price": str(stock['current'])
        }

    def getCube(self):
        cubeUrl = 'https://xueqiu.com/cubes/nav_daily/all.json?cube_symbol=' + self.portfolio_code
        print(cubeUrl)
        response = self.session.get(url=cubeUrl,headers=self.headers)
        return json.loads(response.text)

    def sell_by_period(self, position_list, days=7):
        today = datetime.now().date()
        for position in position_list:
            code = position['code']
            if code in self.trade_history:
                trade_date = datetime.strptime(self.trade_history[code], '%Y-%m-%d').date()
                if (today - trade_date) >= timedelta(days=days):
                    position['weight'] = 0
        return position_list

def extract_stock_codes(text):
    # 使用正则表达式匹配股票代码
    pattern = r'https://xueqiu.com/S/(?:SH|SZ)?(\d{6})'
    matches = re.findall(pattern, text)
    
    # 处理匹配结果，补全SH或SZ前缀
    stock_codes = []
    for code in matches:
        if code.startswith('6'):
            stock_codes.append(f'SH{code}')
        else:
            stock_codes.append(f'SZ{code}')
    
    return stock_codes

def run():
    max_holding = 5
    agentPicks=[]
    while len(agentPicks)==0:
        try:
            agentPicks = extract_stock_codes(reviewAgent().invoke({"messages":[{'role':'user','content':''}]}, {"recursion_limit": 10})['review'])
        except Exception as e:
            print(e)
    print(agentPicks)
    xueqiuP = xueqiuPortfolio('cn',os.environ['XUEQIU_PORTFOLIO_CODE'])
    position = xueqiuP.getPosition()['holding']
    position = xueqiuP.sell_by_period(position,days=5)  # 使用默认的7天

    remain_position = max_holding-len([x for x in position if x['weight']>0])-1
    if remain_position>0 and xueqiuP.getPosition()['cash']>0:
        for stock_code in agentPicks[:remain_position]:
            stock = xueqiuP.newPostition('cn',stock_code,xueqiuP.getPosition()['cash']/remain_position)
            position.append(stock)
            break
    tradeResult = xueqiuP.trade(position)
    print(tradeResult)

if __name__ == "__main__":
    run()
