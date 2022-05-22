import MetaTrader5 as mt5
import pandas
import pandas as pd
import plotly.express as px
from datetime import datetime, date
import pytz
import time

if not mt5.initialize():
    print("initialize() failed, error code =", mt5.last_error())
    quit()


#dont forget to initilize a platform you have to download MetaTrader5 first on MQL5 (on your computer i guess)
timezone = pytz.timezone("Etc/UTC")
# create 'datetime' object in UTC time zone to avoid the implementation of a local time zone offset
utc_from = datetime(2020, 1, 10, tzinfo=timezone)

#PaperTrading account info
#login : 58410679
#password : ha4eavfj
#investor : obeppey0
#server : MetaQuotes-Demo


login = 58410679 #login (int) number goes here
password = 'ha4eavfj' #password (string) goes here
server = 'MetaQuotes-Demo' #server (string) goes here


#logs in to the account
mt5.login(login, password, server)

#get account info
account_info = mt5.account_info()
print(account_info)


#getting specific account data
login_number = account_info.login
balance = account_info.balance
equity = account_info.equity

print()
print("Login:",login_number)
print("Balance:", balance)
print('Equity:',equity)


#get number of symbols with symbols_total()
num_symbols = mt5.symbols_total()


#get all symbols and their specification
symbols = mt5.symbols_get()

#get current symbol price
symbol_price = mt5.symbol_info_tick("EURUSD")._asdict()
print("EURUSD price: ", symbol_price)

#ohlc_data
ohlc_data = pd.DataFrame(mt5.copy_rates_range("EURUSD",mt5.TIMEFRAME_D1,datetime(2022,1,1),datetime.now()))

fig = px.line(ohlc_data, x = ohlc_data['time'], y = ohlc_data['close'])
#fig.show()



# total number of our orders
num_orders = mt5.orders_total()
num_orders

# list of orders
orders = mt5.orders_get()


# total number of positions
num_positions = mt5.positions_total()


# list of positions
positions = mt5.positions_get()

#can also get all of these for history orders and history deals

#send order to the market
request_buy = {
    "action" : mt5.TRADE_ACTION_DEAL, #specify you want to trade
    "symbol" : "EURUSD",  #symbol
    "volume": 2.0, #FLOAT  #volume to trade
    "type": mt5.ORDER_TYPE_BUY,  #trade type i.e buy or sell
    "price": mt5.symbol_info_tick("EURUSD").ask,  #buy or sell at what price (currently the asking price)
    "sl": 0.0, #FLOAT    #stop loss (0.0 is none)
    "tp": 0.0, #FLOAT    #take profit
    "deviation": 20, #INTEGER   #will still trade if within deviation
    "magic": 234000, #INTEGER   #magic number to identify trade
    "comment" : "python script open",   #comment that will happen with trade
    "type_time" : mt5.ORDER_TIME_GTC,    #time in order (GTC means good till cancel)
    "type_filling" : mt5.ORDER_FILLING_IOC,  #IOC means immeditate or cancel, this depends on broker
}
#send in the order
# order_buy = mt5.order_send(request_buy)
# print(order_buy)

# close position
request_sell = {
    "action" : mt5.TRADE_ACTION_DEAL, #specify you want to trade
    "symbol" : "EURUSD",  #symbol
    "volume": 2.0, #FLOAT  #volume to trade
    "type": mt5.ORDER_TYPE_SELL,  #trade type i.e buy or sell
    "position" : 158622885 ,#select the postiojn you want to close, need to get this ticket number from somewhere
    "price": mt5.symbol_info_tick("EURUSD").ask,  #buy or sell at what price (currently the asking price)
    "sl": 0.0, #FLOAT    #stop loss (0.0 is none)
    "tp": 0.0, #FLOAT    #take profit
    "deviation": 20, #INTEGER   #will still trade if within deviation
    "magic": 234000, #INTEGER   #magic number to identify trade
    "comment" : "python script close",   #comment that will happen with trade
    "type_time" : mt5.ORDER_TIME_GTC,    #time in order (GTC means good till cancel)
    "type_filling" : mt5.ORDER_FILLING_IOC,  #IOC means immeditate or cancel, this depends on broker
}

#send in the order
# order_sell = mt5.order_send(request_sell)
# print(order_sell)


#candlestick class
class Candle:
    def __init__(self, open, high, low, close):
        self.open = open
        self.high = high
        self.low = low
        self.close = close

    def __eq__(self, other):
        if self.open == other.open and self.high == other.high and self.low == other.low and self.close == other.close:
            return True
        return False

    def printCandle(self):
        print("Candle: Open:", self.open, "High:", self.high, "Low:", self.low, "Close:", self.close)

class Pair:
    def __init__(self, pair_ticker):
        self.ticker = pair_ticker
        self.candle_time = "H1"
        self.cur_candle = Candle(0,0,0,0)

        self.candle_arr = []

    def updateCurCandle(self):
        self.cur_candle.printCandle()


        rates = mt5.copy_rates_from(self.ticker, mt5.TIMEFRAME_M1, time.time(), 1)

        print("Rates:", rates)

        self.cur_candle.open = rates[0][1]
        self.cur_candle.high = rates[0][2]
        self.cur_candle.low = rates[0][3]
        self.cur_candle.close = rates[0][4]

        if len(self.candle_arr) == 0:
            print("Installing first candle")
            candle_to_log = self.cur_candle
            self.candle_arr.append(candle_to_log)

        elif not (self.candle_arr[-1] == self.cur_candle):
            print("Installing additional candle")
            candle_to_log = self.cur_candle.copy()
            self.candle_arr.append(candle_to_log)

        else:
            print("UpdateCurCandle called, but candle has not changed")
        return




def sell_strategy1_scanner():
    print()



def test(pair1):
    # get 10 EURUSD H4 bars starting from 01.10.2020 in UTC time zone
    rates = mt5.copy_rates_from(pair1, mt5.TIMEFRAME_H1, time.time(), 1)

    print("Display obtained data 'as is'")
    for rate in rates:
        print(rate)

    # create DataFrame out of the obtained data
    rates_frame = pd.DataFrame(rates)

    pandas.set_option("display.max_rows", None,"display.max_columns",None)
    # convert time in seconds into the datetime format
    # rates_frame['time'] = pd.to_datetime(rates_frame['time'], unit='s')

    # display data
    test_pair = Pair(pair1)
    cur_len = 0
    cur_time = time.time()
    while True:
        if time.time() > (cur_time + 60):

            test_pair.updateCurCandle()
            if len(test_pair.candle_arr) > cur_len:
                print(len(test_pair.candle_arr))
                cur_len += 1
            cur_time = time.time()









def main():
    print()
    ##

    test("EURUSD")

if __name__ == '__main__':
    main()

