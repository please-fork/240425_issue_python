import os
import requests
import pandas as pd

def get_data():
    currency = os.environ.get('currency').split(',')
    url = 'https://quotation-api-cdn.dunamu.com/v1/forex/recent'
    tmp = []
    for c in currency:
        params = dict(codes=f'FRX.KRW{c}')
        response = requests.get(url, params)
        response.raise_for_status()
        tmp.append(pd.DataFrame(response.json()))
    return tmp

def get_table():
    df = pd.concat(get_data())
    df.set_index('code', inplace=True)
    df.index = df.index.str.replace('FRX.KRW', '')
    utc = pd.to_datetime(df['timestamp'], unit='ms')
    df['datetime'] = utc + pd.Timedelta(hours=9)
    df = df[['basePrice', 'currencyUnit', 'datetime']]
    return df

def send_issue(title, body):
    token = os.getenv('GH_TOKEN')
    owner = os.getenv('GH_OWNER')
    repo = os.getenv('GH_REPO')
    url = f'https://api.github.com/repos/{owner}/{repo}/issues'
    headers = dict(Authorization=f'Bearer {token}')
    data = dict(title=title, body=body)
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()

def get_kst_time(format):
    import datetime
    utc_dt = datetime.datetime.now(datetime.timezone.utc)
    kst_dt = utc_dt + datetime.timedelta(hours=9)
    return kst_dt.strftime(format)

if __name__ == "__main__":
    df = get_table()
    title = f'환율 모니터링 ({get_kst_time("%Y-%m-%d %H:%M:%S")})'
    body = df.to_markdown()
    send_issue(title, body)
    
