import time
import pyupbit
import datetime
import requests
import telegram

access = "kz6RzMwD5wv6yGNfvx9gXpGVxsrxqFfxSbijx8qY"
secret = "3bm4LtCD1ISLFstfmsWJQxuMPbg7kd9j8KASJtXG"

TOKEN = '1919980133:AAG845Pwz1i4WCJvaaamRT-_QE0uezlvA9A'
ID = '1796318367'
bot = telegram.Bot(TOKEN)

def get_target_price(ticker, k):
    """변동성 돌파 전략으로 매수 목표가 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=2)
    target_price = df.iloc[0]['close'] + (df.iloc[0]['high'] - df.iloc[0]['low']) * k
    return target_price

def get_start_time(ticker):
    """시작 시간 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=1)
    start_time = df.index[0]
    return start_time

def get_ma10(ticker):
    """10개봉 이동 평균선 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=10)
    ma10 = df['close'].rolling(10).mean().iloc[-1]
    return ma10

def get_balance(ticker):
    """잔고 조회"""
    balances = upbit.get_balances()
    for b in balances:
        if b['currency'] == ticker:
            if b['balance'] is not None:
                return float(b['balance'])
            else:
                return 0
    return 0

def get_current_price(ticker):
    """현재가 조회"""
    return pyupbit.get_orderbook(tickers=ticker)[0]["orderbook_units"][0]["ask_price"]

# 로그인
upbit = pyupbit.Upbit(access, secret)
print("autotrade start")
# 시작 메세지 슬랙 전송
bot.sendMessage(ID, "DaeGaRy_autotrade start")

check_buy_XRP = True
check_buy_BTC = True

while True:
    try:
        now = datetime.datetime.now()
        start_time = get_start_time("KRW-XRP")
        end_time = start_time + datetime.timedelta(days=1)

        if start_time < now < end_time - datetime.timedelta(seconds=10):
            print("in trade time")
            target_price_XRP = get_target_price("KRW-XRP", 0.1)
            target_price_BTC = get_target_price("KRW-BTC", 0.2)
            ma10_XRP = get_ma10("KRW-XRP")
            ma10_BTC = get_ma10("KRW-BTC")
            current_price_XRP = get_current_price("KRW-XRP")
            current_price_BTC = get_current_price("KRW-BTC")
            if check_buy_XRP == False and target_price_XRP < current_price_XRP and ma10_XRP < current_price_XRP:
                krw = get_balance("KRW")
                real_target_XRP = round(target_price_XRP,-1)

                if check_buy_BTC == True and krw > 5000:
                    total_XRP = (krw * 0.9995) / real_target_XRP
                    buy_result_XRP = upbit.buy_limit_order("KRW-XRP", real_target_XRP, total_XRP)
                    bot.sendMessage(ID, "XRP_buy :"+str(buy_result_XRP))
                    check_buy_XRP = True
                elif check_buy_BTC == False and krw > 5000:
                    total_XRP = (krw * 0.5 * 0.9995) / real_target_XRP
                    buy_result_XRP = upbit.buy_limit_order("KRW-XRP", real_target_XRP, total_XRP)
                    bot.sendMessage(ID, "XRP_buy :"+str(buy_result_XRP))
                    check_buy_XRP = True

            if check_buy_BTC == False and target_price_BTC < current_price_BTC and ma10_BTC < current_price_BTC:
                krw = get_balance("KRW")
                real_target_BTC = round(target_price_BTC,-3)

                if check_buy_XRP == True and krw > 5000:
                    total_BTC = (krw * 0.9995) / real_target_BTC
                    buy_result_BTC = upbit.buy_limit_order("KRW-BTC", real_target_BTC, total_BTC)
                    bot.sendMessage(ID, "BTC_buy :"+str(buy_result_BTC))
                    check_buy_BTC = True
                elif check_buy_XRP == False and krw > 5000:
                    total_BTC = (krw * 0.5 * 0.9995) / real_target_BTC
                    buy_result_BTC = upbit.buy_limit_order("KRW-BTC", real_target_BTC, total_BTC)
                    bot.sendMessage(ID, "BTC_buy :"+str(buy_result_BTC))
                    check_buy_BTC = True
        else:
            btc_XRP = get_balance("XRP")
            btc_BTC = get_balance("BTC")
            if btc_XRP > 3.0 or btc_BTC>0.0001:
                if check_buy_XRP == True:
                    sell_result_XRP = upbit.sell_market_order("KRW-XRP", btc_XRP*0.9995)
                    bot.sendMessage(ID, "XRP_sell :"+str(sell_result_XRP))
                    check_buy_XRP = False
                if check_buy_BTC == True:
                    sell_result_BTC = upbit.sell_market_order("KRW-BTC", btc_BTC * 0.9995)
                    bot.sendMessage(ID, "BTC_sell :"+str(sell_result_BTC))
                    check_buy_BTC = False
            else:
                uuid_XRP = buy_result_XRP['uuid']
                cancel_result_XRP = upbit.cancel_order(uuid_XRP)
                bot.sendMessage(ID, "XRP_cancel :"+str(cancel_result_XRP))
                uuid_BTC = buy_result_BTC['uuid']
                cancel_result_BTC = upbit.cancel_order(uuid_BTC)
                bot.sendMessage(ID, "BTC_cancel :"+str(cancel_result_BTC))
        time.sleep(1)
    except Exception as e:
        print(e)
        bot.sendMessage(ID, str(e))
        time.sleep(1)
