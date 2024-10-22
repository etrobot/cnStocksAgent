import requests,json,re
from datetime import *
import os
from dotenv import load_dotenv
from graph_reviewer import reviewAgent

load_dotenv()

def unsbox(s):
    _0x4b082b = [15, 35, 29, 24, 33, 16, 1, 38, 10, 9, 19, 31, 40, 27, 22, 23, 25, 13, 6, 11, 39, 18, 20, 8, 14, 21, 32, 26, 2, 30, 7, 4, 17, 5, 3, 28, 34, 37, 12, 36]
    _0x4da0dc = [''] * len(_0x4b082b)
    _0x12605e = ''
    for _0x20a7bf in range(len(s)):
        _0x385ee3 = s[_0x20a7bf]
        for _0x217721 in range(len(_0x4b082b)):
            if _0x4b082b[_0x217721] == _0x20a7bf + 1:
                _0x4da0dc[_0x217721] = _0x385ee3
    _0x12605e = ''.join(_0x4da0dc)
    return _0x12605e
 
def hexXor(s1, s2):
    _0x5a5d3b = ''
    for _0xe89588 in range(0, min(len(s1), len(s2)), 2):
        _0x401af1 = int(s1[_0xe89588:_0xe89588+2], 16)
        _0x105f59 = int(s2[_0xe89588:_0xe89588+2], 16)
        _0x189e2c = hex(_0x401af1 ^ _0x105f59)[2:]
        if len(_0x189e2c) == 1:
            _0x189e2c = '0' + _0x189e2c
        _0x5a5d3b += _0x189e2c
    return _0x5a5d3b

def xqStockInfo(mkt, code:str, s, h):  # 雪球股票信息
    code=code.upper()
    data = {
        'code': str(code),
        'size': '30',
        # 'key': '47bce5c74f',
        'market': mkt,
    }
    r = s.get("https://xueqiu.com/stock/p/search.json", headers=h, params=data)
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
        self.trade_history = self.load_trade_history()
        self.portfolio_code = portfolio_code
        self.mkt = mkt
        self.position = dict()
        self.holdnum = 5
        self.session = requests.Session()
        self.session.cookies.update(self.getXueqiuCookie())
        self.p_url = 'https://xueqiu.com/P/'+portfolio_code
        self.headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'zh-CN,zh-TW;q=0.9,zh;q=0.8,en-US;q=0.7,en;q=0.6,ja;q=0.5',
            'Cache-Control': 'max-age=0',
            'Connection': 'keep-alive',
            'Referer': 'https://xueqiu.com/',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1',
        }


    def updateTrade(self,stock_symbol,trade_date:str=None):
        if trade_date is None:
            trade_date = datetime.now().strftime('%Y-%m-%d')
        self.trade_history[stock_symbol]=trade_date
        with open('trade_history.json', 'w') as f:
            json.dump(self.trade_history, f)


    def load_trade_history(self):
        try:
            with open('trade_history.json', 'r') as f:
                return json.load(f) 
        except FileNotFoundError:
            return {} 
        except json.JSONDecodeError:
            return {}

    def getXueqiuCookie(self):
        sbCookie = open('cookies.txt','r').read()
        cookie_dict = {}
        for record in sbCookie.split(";"):
            key, value = record.strip().split("=", 1)
            cookie_dict[key] = value
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
        resp = self.session.get(self.p_url, headers=self.headers)
        arg1 = re.findall("var arg1='(.*?)';",resp.text)
        if len(arg1)==1:
            arg1=arg1[0]
            _0x23a392 = unsbox(arg1)
            _0x5e8b26 = '3000176000856006061501533003690027800375'
            arg2 = hexXor(_0x23a392, _0x5e8b26)
            self.session.cookies.update({'acw_sc__v2': arg2})
            resp = self.session.get(self.p_url, headers=self.headers)
        portfolio_text = re.search(r'SNB\.cubeInfo\s*=\s*(\{.*?\})\n', resp.text, re.DOTALL).group(1)
        portfolio_info = json.loads(portfolio_text)
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
            code = position['stock_symbol']
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
    xueqiuP = xueqiuPortfolio('cn',os.environ['XUEQIU_PORTFOLIO_CODE'])
    position = xueqiuP.getPosition()
    print(position)
