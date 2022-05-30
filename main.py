import MetaTrader5 as mt5
import pandas
import pandas as pd
import plotly.express as px
from datetime import datetime, date
import pytz
import time
import copy
import yfinance
import matplotlib.pyplot as plt


from transitions import Machine
import random

if not mt5.initialize():
    print("initialize() failed, error code =", mt5.last_error())
    quit()


#dont forget to initilize a platform you have to download MetaTrader'five' first on MQL'five' (on your computer i guess)
timezone = pytz.timezone("Etc/UTC")
# create 'datetime' object in UTC time zone to avoid the implementation of a local time zone offset
utc_from = datetime(2020, 1, 10, tzinfo=timezone)

#PaperTrading account info
#login : 'five'8'four''one''zero'679
#password : ha'four'eavfj
#investor : obeppey'zero'
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

# list of orders
orders = mt5.orders_get()


# total number of positions
num_positions = mt5.positions_total()


# list of positions
positions = mt5.positions_get()

#can also get all of these for history orders and history deals

#send order to the market
# request_buy = {
#     "action" : mt5.TRADE_ACTION_DEAL, #specify you want to trade
#     "symbol" : "EURUSD",  #symbol
#     "volume": 2.0, #FLOAT  #volume to trade
#     "type": mt5.ORDER_TYPE_BUY,  #trade type i.e buy or sell
#     "price": mt5.symbol_info_tick("EURUSD").ask,  #buy or sell at what price (currently the asking price)
#     "sl": 0.0, #FLOAT    #stop loss ('zero'.'zero' is none)
#     "tp": 0.0, #FLOAT    #take profit
#     "deviation": 20, #INTEGER   #will still trade if within deviation
#     "magic": 234000, #INTEGER   #magic number to identify trade
#     "comment" : "python script open",   #comment that will happen with trade
#     "type_time" : mt5.ORDER_TIME_GTC,    #time in order (GTC means good till cancel)
#     "type_filling" : mt5.ORDER_FILLING_IOC,  #IOC means immeditate or cancel, this depends on broker
# }
#send in the order
# order_buy = mt5.order_send(request_buy)
# print(order_buy)

#close position
# request_sell = {
#     "action" : mt5.TRADE_ACTION_DEAL, #specify you want to trade
#     "symbol" : "EURUSD",  #symbol
#     "volume": 2.0, #FLOAT  #volume to trade
#     "type": mt5.ORDER_TYPE_SELL,  #trade type i.e buy or sell
#     "position" : 158622885 ,#select the postiojn you want to close, need to get this ticket number from somewhere
#     "price": mt5.symbol_info_tick("EURUSD").ask,  #buy or sell at what price (currently the asking price)
#     "sl": 0.0, #FLOAT    #stop loss ('zero'.'zero' is none)
#     "tp": 0.0, #FLOAT    #take profit
#     "deviation": 20, #INTEGER   #will still trade if within deviation
#     "magic": 234000, #INTEGER   #magic number to identify trade
#     "comment" : "python script close",   #comment that will happen with trade
#     "type_time" : mt5.ORDER_TIME_GTC,    #time in order (GTC means good till cancel)
#     "type_filling" : mt5.ORDER_FILLING_IOC,  #IOC means immeditate or cancel, this depends on broker
# }




#candlestick class
class Candle:
    def __init__(self, open, high, low, close):
        self.open = open
        self.high = high
        self.low = low
        self.close = close
        self.state = 'blank'

    def __eq__(self, other):
        if self.open == other.open and self.high == other.high and self.low == other.low and self.close == other.close:
            return True
        return False

    def printCandle(self):
        print("Candle: Open:", self.open, "High:", self.high, "Low:", self.low, "Close:", self.close, "State:", self.state, "Candle Color:", self.candleColor())

    def candleColor(self):
        if self.open < self.close:
            return 'green'
        else:
            return 'red'



class Pair:
    states = ['zero', 'one', 'onefive', 'two', 'twofive', 'three', 'threefive', 'four', 'fourfive', 'foursevenfive', 'five', 'six']


    def __init__(self, pair_ticker, transitions):
        self.ticker = pair_ticker
        self.candle_time = "M1"
        self.cur_candle = Candle(0, 0, 0, 0)
        self.candle_arr = []

        self.median_line = 0

        self.sold = False


        """
        LOGIC FOR CHECKING STATE : 
        * Current checking state value represents the check you are 
            searching for 
        * Everytime candle is changed, it should be checked where the 
            state should go to, gonna make an FSM 
        * 12 possible states 
        * 26 possible transitions 
        
        """
        self.machine = Machine(model=self, states= Pair.states, transitions=transitions, initial='zero')



    def updateCurCandle(self):
        self.cur_candle.printCandle()


        rates = mt5.copy_rates_from_pos(self.ticker, mt5.TIMEFRAME_M1, 1, 1)

        print("Rates:", rates)

        self.cur_candle.open = rates[0][1]
        self.cur_candle.high = rates[0][2]
        self.cur_candle.low = rates[0][3]
        self.cur_candle.close = rates[0][4]


        if len(self.candle_arr) == 0:
            print("Installing first candle")

            self.updateState()
            self.cur_candle.state = self.state

            self.candle_arr.append(copy.deepcopy(self.cur_candle))


        elif not (self.candle_arr[-1] == self.cur_candle):
            print("Installing additional candle")

            self.updateState()
            self.cur_candle.state = self.state

            self.candle_arr.append(copy.deepcopy(self.cur_candle))

            print("Candle arr:")
            print("len:", len(self.candle_arr))
            for i in range(len(self.candle_arr)):
                print(self.candle_arr[i].printCandle())

            #Additional candle has been installed, here you will need to update state


        else:
            print("UpdateCurCandle called, but candle has not changed")
            print("Cur candle")
            self.cur_candle.printCandle()
            print("-1 index Candle")
            self.candle_arr[-1].printCandle()

        return

    def updateState(self):

        #breaking red
        if (self.state == 'four' or self.state == 'fourfive') and (self.cur_candle.close < self.median_line and self.cur_candle.candleColor() == 'red'):
            self.breaking_red()

        #no break green
        elif (self.state == 'foursevenfive' or self.state == 'five') and (self.cur_candle.close < self.median_line and self.cur_candle.candleColor() == 'green'):
            # ^ and self.not above fibonacci line
            self.no_break_green()

        #breaking green
        elif (self.state == 'foursevenfive' or self.state == 'five') and (self.cur_candle.close > self.median_line and self.cur_candle.candleColor() == 'green'):
            # ^ and self.not above fibonacci line
            self.no_break_green()

        #signal red
        elif self.state == 'five' and self.cur_candle.candleColor() == 'red':
            # ^ and self.cur candle max above fibonacci line
            self.signal_red()

        #fail signal red
        elif self.state == 'five' and self.cur_candle.candleColor() == 'red':
            # ^ and self.cur candle max not above fibonacci line
            self.fail_signal_red()

        #green
        elif (self.state != 'foursevenfive' or self.state != 'five') and self.cur_candle.candleColor() == 'green':
            self.green()

        #red
        elif self.state != 'five' and self.cur_candle.candleColor() == 'red':
            self.red()

        if self.state == 'six':
            print("SATISFIED CONDITIONS, SELLING")
            self.sell()



    def sell(self):
        print("Selling function commencing...")
        request_sell = {
            "action" : mt5.TRADE_ACTION_DEAL, #specify you want to trade
            "symbol" : "EURUSD",  #symbol
            "volume": 20.0, #FLOAT  #volume to trade
            "type": mt5.ORDER_TYPE_SELL,  #trade type i.e buy or sell
            "position" : 158622885 ,#select the postiojn you want to close, need to get this ticket number from somewhere
            "price": mt5.symbol_info_tick("EURUSD").ask,  #buy or sell at what price (currently the asking price)
            "sl": 0.0, #FLOAT    #stop loss ('zero'.'zero' is none)
            "tp": 0.0, #FLOAT    #take profit
            "deviation": 20, #INTEGER   #will still trade if within deviation
            "magic": 234000, #INTEGER   #magic number to identify trade
            "comment" : "python script close",   #comment that will happen with trade
            "type_time" : mt5.ORDER_TIME_GTC,    #time in order (GTC means good till cancel)
            "type_filling" : mt5.ORDER_FILLING_IOC,  #IOC means immeditate or cancel, this depends on broker
        }
        # send in the order
        order_buy = mt5.order_send(request_sell)
        print(order_buy)
        self.sold = True



def fibonacci_618(high_price, low_price):
    diff = high_price - low_price
    return high_price - diff * 0.618

def sell_strategy1_scanner():
    print()



def test(pair1):
    # get 'one''zero' EURUSD H'four' bars starting from 'zero''one'.'one''zero'.'two''zero''two''zero' in UTC time zone
    rates = mt5.copy_rates_from_pos(pair1, mt5.TIMEFRAME_M1, 1, 1)




    print("Display obtained data 'as is'")
    for rate in rates:
        print(rate)

    pandas.set_option("display.max_rows", None,"display.max_columns",None)
    # convert time in seconds into the datetime format
    # rates_frame['time'] = pd.to_datetime(rates_frame['time'], unit='s')

    # display data

    strat1_transitions = [
        {'trigger': 'green', 'source': 'zero', 'dest': 'one'},
        {'trigger': 'red', 'source': 'zero', 'dest': 'zero'},

        {'trigger': 'green', 'source': 'one', 'dest': 'onefive'},
        {'trigger': 'red', 'source': 'one', 'dest': 'zero'},

        {'trigger': 'green', 'source': 'onefive', 'dest': 'onefive'},
        {'trigger': 'red', 'source': 'onefive', 'dest': 'two'},

        {'trigger': 'green', 'source': 'two', 'dest': 'zero'},
        {'trigger': 'red', 'source': 'two', 'dest': 'twofive'},

        {'trigger': 'green', 'source': 'twofive', 'dest': 'three'},
        # store the close of the last red body as the support line
        {'trigger': 'red', 'source': 'twofive', 'dest': 'twofive'},

        {'trigger': 'green', 'source': 'three', 'dest': 'threefive'},
        {'trigger': 'red', 'source': 'three', 'dest': 'zero'},

        {'trigger': 'green', 'source': 'threefive', 'dest': 'threefive'},
        {'trigger': 'red', 'source': 'threefive', 'dest': 'four'},

        {'trigger': 'green', 'source': 'four', 'dest': 'zero'},
        {'trigger': 'red', 'source': 'four', 'dest': 'fourfive'},
        {'trigger': 'breaking_red', 'source': 'four', 'dest': 'foursevenfive'},

        {'trigger': 'green', 'source': 'fourfive', 'dest': 'zero'},
        {'trigger': 'red', 'source': 'fourfive', 'dest': 'fourfive'},
        {'trigger': 'breaking_red', 'source': 'fourfive', 'dest': 'foursevenfive'},

        # old support line now is stored as resistance line
        {'trigger': 'red', 'source': 'foursevenfive', 'dest': 'foursevenfive'},
        {'trigger': 'no_break_green', 'source': 'foursevenfive', 'dest': 'five'},
        {'trigger': 'breaking_green', 'source': 'foursevenfive', 'dest': 'zero'},

        {'trigger': 'breaking_green', 'source': 'five', 'dest': 'zero'},
        {'trigger': 'no_break_green', 'source': 'five', 'dest': 'five'},
        {'trigger': 'signal_red', 'source': 'five', 'dest': 'six'},
        {'trigger': 'fail_signal_red', 'source': 'five', 'dest': 'zero'},
        # SELL IF YOU HIT STATE six
    ]












    test_pair = Pair(pair1,strat1_transitions)
    cur_len = 0
    cur_time = time.time()
    sold = False
    while not sold:
        if time.time() > (cur_time + 60):

            test_pair.updateCurCandle()
            sold = test_pair.sold
            if sold is True:
                print("sold is true")
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

