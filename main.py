import time 
import requests
import datetime as dt
import pandas as pd

#Get input from user


#Function to get last 60 days of data
def get_data(period, start_date,end_date,symbol):
    #scrip_ID = mapping.get(symbol)
    user_id = 'VT5229'
    scrip_ID = inst.loc[symbol]['instrument_token']
    url = f"https://kite.zerodha.com/oms/instruments/historical/{scrip_ID}/{period}?user_id={user_id}&oi=1&from={start_date}&to={end_date}"
    
    #enctoken changes everytime you logoff
    token = "sP0cU2koF6AntNHSuFXXUfXZXku+iwzc9IuVtLsXDXarCdEHHk9P0s9piz7q+tyLMCrH4yWvzPrqhHeeEwIKrgg88/N6Og=="
    
    payload={}
    headers = {
      'authority': 'kite.zerodha.com',
      'pragma': 'no-cache',
      'cache-control': 'no-cache',
      'sec-ch-ua': '"Google Chrome";v="87", " Not;A Brand";v="99", "Chromium";v="87"',
      'accept': 'application/json, text/plain, */*',
      'authorization': f"enctoken {token}",
      'sec-ch-ua-mobile': '?0',
      'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36',
      'sec-fetch-site': 'same-origin',
      'sec-fetch-mode': 'cors',
      'sec-fetch-dest': 'empty',
      'referer': 'https://kite.zerodha.com/chart/web/tvc/INDICES/NIFTY%2050/256265',
      'accept-language': 'en-US,en;q=0.9',
      'cookie': '_ga=GA1.2.1237715775.1599025253; WZRK_G=35dc9bf39872453ca302ca61e69943d9; _hjid=a0fa20cf-2859-4186-addd-1ad51ce109c3; _fbp=fb.1.1599067875093.1182513860; mp_7b1e06d0192feeac86689b5599a4b024_mixpanel=%7B%22distinct_id%22%3A%20%225ef374f27072303def14c858%22%2C%22%24device_id%22%3A%20%221744fdf72e2277-05c84fb230310a-f7b1332-144000-1744fdf72e3148%22%2C%22%24initial_referrer%22%3A%20%22%24direct%22%2C%22%24initial_referring_domain%22%3A%20%22%24direct%22%2C%22%24user_id%22%3A%20%225ef374f27072303def14c858%22%2C%22__timers%22%3A%20%7B%7D%7D; __cfduid=d5db03e65a8d59b8756511c92cc839f141610687855; _gid=GA1.2.275777476.1611075594; kf_session=EQK5SCto80996B3JICoZQanok197GRGh; public_token=yu45f5lpkI9Oo2Ni91qJIMyzEv3GRh1N; user_id=VT5229; enctoken=x2FuRS3NQgllZxWymw/WjRNm+pxJbYsB+sPjTksKzwi+AwrBAGWZroZu5biMvrMe9BqZMLqxVn0NQ0q/sj6kBTTJb/bKxw=='
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    data = response.json()
    return data

#Function to scrap whole data at once
def scrap_data(scrip_name):
    df = pd.DataFrame(columns=['DateTime','Open','High','Low','Close','Volume'])
    
    final_start = "2015-01-01"
    start = dt.datetime.strptime(final_start,"%Y-%m-%d")
    end = start + dt.timedelta(60)
    
    diff = divmod((dt.datetime.today() - end).total_seconds(),86400)[0]
    
    while diff >= 0:
    
        start_date = dt.datetime.strftime(start,"%Y-%m-%d") 
        end_date = dt.datetime.strftime(end,"%Y-%m-%d")

        a = get_data('minute',start_date,end_date,scrip_name)['data']['candles']

        data = pd.DataFrame(a,columns = ['DateTime','Open','High','Low','Close','Volume','OI'])
        data.drop(columns=['OI'],inplace = True)

        df = df.append(data)

        diff = divmod((dt.datetime.today() - end).total_seconds(),86400)[0]

        if diff < 0:
            start = end + dt.timedelta(1)
            end = start + dt.timedelta(abs(diff))
        else:
            start = end + dt.timedelta(1)
            end = start + dt.timedelta(60)

    return df

#Function to transform data into new format
def transform(df):
    df.insert(1,'Date',0)
    df.insert(2,'Time',0)
    df[['Date','Time']] = df['DateTime'].str.split('T',expand = True)
    df[['Time','nan']] = df['Time'].str.split('+',expand = True)
    df.drop(['DateTime','nan'],axis = 1,inplace = True)
    
    return df

#vlookup for instrument token
instruments = pd.read_csv("https://api.kite.trade/instruments/NSE")
data = instruments[['instrument_token','tradingsymbol']]
inst = data.set_index('tradingsymbol')

#Create list of stocks/index/option/future symbol that you want the data for
stocks = ['INDIA VIX','SBIN']

#For a list of tickers
for i in stocks:
    df = scrap_data(i)
    df.insert(0,'Ticker',i)
    df = transform(df)
    df.to_csv('data/' + i + '.csv')
