import requests,re


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


cookies = {
    '__utmz': '1.1669255268.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none)',
    'device_id': '302aa1a3d743216422862248a71b758e',
    's': 'af128mc8jp',
    'bid': '4b00aff9a838774878b7cd7b32843ae2_lpj6adio',
    'smidV2': '20240328083945093974cb90fe4e3325179a4c8896ac54009dce6c75b88f680',
    'xq_is_login': '1',
    'u': '4306411329',
    'cookiesu': '891724720798420',
    'xq_a_token': '5ae5fc82e9e1b13fbd0058fbcb03b04ab7bb7fa1',
    'xqat': '5ae5fc82e9e1b13fbd0058fbcb03b04ab7bb7fa1',
    'xq_id_token': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJ1aWQiOjQzMDY0MTEzMjksImlzcyI6InVjIiwiZXhwIjoxNzMxMjE1NDk0LCJjdG0iOjE3Mjg2MjM0OTQxMTAsImNpZCI6ImQ5ZDBuNEFadXAifQ.VGs5PwL_IcC3ic8qwb6CAJpi-Cdur3lYk-t8LmS6XuoUi3St9_jeXmedvTPnvGW3Zixds5ROiSJfv-ep6ks24oyZoi6_FYfcLwnK6te5NfzMD2mNOZ4rEuieslTn_-1AVYB1RDi5gZzbxqVJseNIJEbzleciTZkYmj5yzi5o_h4_DwTHVYaQuY4LpZNTL_5SNA_ZtCnhGrrzkRyFF5G3rb1heq1faKvvKFWW8KPWRwiIpTIllHKBnKVC49NiVP_00_Gvq3bkE7Cl5XtoFbwE2h4I3SGahjEFWsd5v1kS_nf8xXJfcCkQhcYxzYfXr4L6jlQEHgFDoAk3mwxrmWCbrw',
    'xq_r_token': 'bfcbad8fee3e1545b4101ad0fedd87471ca4c74f',
    'Hm_lvt_1db88642e346389874251b5a1eded6e3': '1727425607,1729504857',
    'HMACCOUNT': '202D50A3A6A95E4C',
    '__utmc': '1',
    '.thumbcache_f24b8bbe5a5934237bbc0eda20c1b6e7': 'OHN+L9WFyaHyMVQFX+WLoxgDEdhEYUJwMmJYifqbd5JseBynPMsRCjIr0PO3InV7caPlyszXopbsbWN0ayDh0A%3D%3D',
    'acw_tc': '2760827217295725444883604e716234f8491494a5ddf7f6b9b81f41dc8df0',
    'acw_sc__v2': '6717453465a68c18d355e50c56c2e41b3a5d461f',
    'ssxmod_itna': 'QqfOiKGIejxRhDUxBcxB4DKMO4+ozDP=lGpDGqIv5Ds1eTDSxGKidDqxBnW=fSxIqe0iGDLhqIQY+rKQ+08Ouvj0W1PGIDeKG2DmeDyDi5GRD09mTTDeWtD5xGoDPxDeDAjKDCg=TKDdncFCchPO+EpOnxGWmxKDmrKDRooDSeBzZr5F1DYDaxKDup5OCxi8D7FEmgY1D7pmGF3DXxKDE0+kR3dDvpO7CO21S25OcFr4jA0eVAIafmDKtGxq1nxqoAnovBW5oBietj+31jQDiERB4D==',
    'ssxmod_itna2': 'QqfOiKGIejxRhDUxBcxB4DKMO4+ozDP=lGpDGqI5ikL7Dl64QKQ08D+hoD==',
    'Hm_lpvt_1db88642e346389874251b5a1eded6e3': '1729573691',
    '__utma': '1.707656828.1669255268.1729570784.1729573691.327',
    '__utmt': '1',
    '__utmb': '1.1.10.1729573691',
}


headers = {
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
res = requests.get('https://xueqiu.com/P/ZH1353952', cookies=cookies, headers=headers)
print(res.text)
exit()
cookies.update(res.cookies.get_dict())
 
# 获取arg1参数
arg1 = re.findall("var arg1='(.*?)';",res.text)[0]
print("arg1", arg1)
 
# 根据算法获取arg2参数
_0x23a392 = unsbox(arg1)
_0x5e8b26 = '3000176000856006061501533003690027800375'
arg2 = hexXor(_0x23a392, _0x5e8b26)
print("arg2", arg2)
 
cookies.update({'acw_sc__v2': arg2})

res = requests.get('https://xueqiu.com/P/ZH1353952', cookies=cookies, headers=headers)
print(res.text)