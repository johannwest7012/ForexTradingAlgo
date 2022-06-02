import MetaTrader5 as mt5
import pandas
# import pandas as pd
# import plotly.express as px
# from datetime import datetime, date
# import pytz
import time
import copy
# import yfinance
# import matplotlib.pyplot as plt


from transitions import Machine
# import random
from logininfo import login, password, server




#get number of symbols with symbols_total()
# num_symbols = mt5.symbols_total()
#
#
# #get all symbols and their specification
# symbols = mt5.symbols_get()
#
# #get current symbol price
# symbol_price = mt5.symbol_info_tick("EURUSD")._asdict()
# print("EURUSD price: ", symbol_price)
#
# #ohlc_data
# ohlc_data = pd.DataFrame(mt5.copy_rates_range("EURUSD",mt5.TIMEFRAME_D1,datetime(2022,1,1),datetime.now()))
#
# fig = px.line(ohlc_data, x = ohlc_data['time'], y = ohlc_data['close'])
# #fig.show()



# total number of our orders
# num_orders = mt5.orders_total()
#
# # list of orders
# orders = mt5.orders_get()
#
#
# # total number of positions
# num_positions = mt5.positions_total()
#
#
# # list of positions
# positions = mt5.positions_get()

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



class Strat1Pair:
    states = ['zero', 'one', 'onefive', 'two', 'twofive', 'three', 'threefive', 'four', 'fourfive', 'foursevenfive', 'five', 'six']


    def __init__(self, pair_ticker, volume, transitions):
        self.ticker = pair_ticker
        self.volume = volume
        self.candle_time = "M1"
        self.cur_candle = Candle(0, 0, 0, 0)
        self.candle_arr = []

        self.median_line = 0
        self.high_fib_price = 0
        self.low_fib_price = 0

        self.fibonacci_618_line = 0



        self.opened = False


        """
        LOGIC FOR CHECKING STATE : 
        * Current checking state value represents the check you are 
            searching for 
        * Everytime candle is changed, it should be checked where the 
            state should go to, gonna make an FSM 
        * 12 possible states 
        * 26 possible transitions 
        
        """
        self.machine = Machine(model=self, states= Strat1Pair.states, transitions=transitions, initial='zero')



    def updateCurCandle(self):
        # self.cur_candle.printCandle()

        rates = mt5.copy_rates_from_pos(self.ticker, mt5.TIMEFRAME_M1, 1, 1)

        # print("Rates:", rates)

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
            for i in range(len(self.candle_arr)):
                print('TICKER:', self.ticker)
                print(self.candle_arr[i].printCandle())

            #Additional candle has been installed, here you will need to update state




        return

    def updateState(self):

        #breaking red
        if (self.state == 'four' or self.state == 'fourfive') and (self.cur_candle.close < self.median_line and self.cur_candle.candleColor() == 'red'):
            #red candle that breaks down past the support median line
            self.breaking_red()

        #no break green
        elif (self.state == 'foursevenfive' or self.state == 'five') and (self.cur_candle.close < self.median_line and self.cur_candle.close < self.fibonacci_618_line) and self.cur_candle.candleColor() == 'green':
            #green that does not close above median line and fibonacci line
            self.no_break_green()

        #breaking green
        elif (self.state == 'foursevenfive' or self.state == 'five') and (self.cur_candle.close > self.median_line or self.cur_candle.close > self.fibonacci_618_line) and self.cur_candle.candleColor() == 'green':
            #green that does close above median line or fibonacci line
            self.no_break_green()

        #signal red
        elif self.state == 'five' and self.cur_candle.candleColor() == 'red' and self.cur_candle.high > self.fibonacci_618_line:
            #red candle who's high breaks up through fibonacci line
            self.signal_red()

        #fail signal red
        elif self.state == 'five' and self.cur_candle.candleColor() == 'red' and self.cur_candle.high < self.fibonacci_618_line:
            #signal red but it does not break up through fibonacci line
            self.fail_signal_red()

        #green
        elif (self.state != 'foursevenfive' and self.state != 'five' and self.state != 'six') and self.cur_candle.candleColor() == 'green':
            self.green()

        #red
        elif (self.state != 'five' and self.state != 'six') and self.cur_candle.candleColor() == 'red':
            self.red()


        self.state_checks()

    def state_checks(self):
        if self.state == 'six':
            print("SATISFIED CONDITIONS, SELLING", self.ticker)
            self.opened = open_position(self.ticker, "SELL", self.volume, 300, 100)
            if self.opened == False:
                self.state == 'zero'
            else:
                print("SELL MADE EXITING LOOP")


        elif self.state == 'twofive':
            self.median_line = self.cur_candle.close

        elif self.state == 'threefive':
            self.high_fib_price = self.cur_candle.high

        elif self.state == 'foursevenfive':
            self.low_fib_price = self.cur_candle.low
            self.fibonacci_618_line = fibonacci_618(self.high_fib_price, self.low_fib_price)





def connect(login, password, server):
    mt5.initialize()
    authorized = mt5.login(login, password, server)

    if authorized:
        print("Connected: Connecting to MT5 Client")
        account_info = mt5.account_info()
        print(account_info)

        # getting specific account data
        login_number = account_info.login
        balance = account_info.balance
        equity = account_info.equity

        print()
        print("Login:", login_number)
        print("Balance:", balance)
        print('Equity:', equity)
    else:
        print("Failed to connect at account")


def open_position(pair, order_type, size, tp_distance=None, stop_distance=None):
    symbol_info = mt5.symbol_info(pair)
    if symbol_info is None:
        print(pair, "not found")
        return False

    if not symbol_info.visible:
        print(pair, "is not visible, trying to switch on")
        if not mt5.symbol_select(pair, True):
            print("symbol_select({}}) failed, exit", pair)
            return False
    print(pair, "found!")

    point = symbol_info.point

    if (order_type == "BUY"):
        order = mt5.ORDER_TYPE_BUY
        price = mt5.symbol_info_tick(pair).ask
        if (stop_distance):
            sl = price - (stop_distance * point)
        if (tp_distance):
            tp = price + (tp_distance * point)

    if (order_type == "SELL"):
        order = mt5.ORDER_TYPE_SELL
        price = mt5.symbol_info_tick(pair).bid
        if (stop_distance):
            sl = price + (stop_distance * point)
        if (tp_distance):
            tp = price - (tp_distance * point)

    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": pair,
        "volume": float(size),
        "type": order,
        "price": price,
        "sl": sl,
        "tp": tp,
        "magic": 22,
        "comment": "",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }

    result = mt5.order_send(request)

    if result.retcode != mt5.TRADE_RETCODE_DONE:
        print("Failed to send order :(")
        return False
    else:
        print("Order successfully placed!")
        return True



def fibonacci_618(high_price, low_price):
    diff = high_price - low_price
    return high_price - diff * 0.618

def sell_strategy1_scanner():
    print()



def test(pair_list, volume):
    # get 'one''zero' EURUSD H'four' bars starting from 'zero''one'.'one''zero'.'two''zero''two''zero' in UTC time zone
    # rates = mt5.copy_rates_from_pos(pair1, mt5.TIMEFRAME_M1, 1, 1)




    # print("Display obtained data 'as is'")
    # for rate in rates:
    #     print(rate)
    #
    # pandas.set_option("display.max_rows", None,"display.max_columns",None)
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





    object_list = []
    for i in pair_list:
        object_list.append(Strat1Pair(pair_ticker=i, volume=volume, transitions=strat1_transitions))

    sold = False
    while not sold:
        for i in object_list:

            i.updateCurCandle()
            sold = i.opened








    # test_pair = Strat1Pair(pair_ticker= pair1, volume= 10, transitions= strat1_transitions)
    # cur_time = time.time()
    # sold = False
    # while not sold:
    #     if time.time() > (cur_time + 60):
    #         #updates every 60 seconds, will probably need to change this to shroter time period, if that doesn't work
    #         #you can change it back to 60 because it might be working fine right now
    #
    #         test_pair.updateCurCandle()
    #         sold = test_pair.opened
    #         if sold is True:
    #             print("sold is true")
    #
    #         cur_time = time.time()
    #








def main():
    print()
    ##

    connect(login, password, server)
    test(["EURUSD"], 10.0)

main()

