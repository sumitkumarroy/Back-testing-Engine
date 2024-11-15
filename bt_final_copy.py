import pandas as pd
import streamlit as st
import os
import ta
import mplfinance as mpf
import numpy as np
import datetime


def bb(country,exchange,name,initialCapital,indicator,window,type,Position,start,end,volume):
    if country== "India":
              
        if exchange=="NSE":
            path = f"Stocks Data/India/NSE/{name}.csv"
        elif exchange=="BSE":
            path = f"Stocks Data/India/BSE/{name}.csv"
        price = " RS"
        symbol="₹ "

    elif country == "USA":
        path = f"Stocks Data/USA/{name}.csv"
        price=" Doller"
        symbol ="$ "

    elif country == "Japan":
        path = f"Stocks Data/Japan/{name}.csv"
        price=" Yen"
        symbol="¥ "
    
    else:
        print("Select a valid country")
    if os.path.exists(path):
        data =pd.read_csv(path)

        data['Date'] = pd.to_datetime(data['Date']).dt.tz_localize(None)
        starting = pd.to_datetime(start,format='mixed')
        ending = pd.to_datetime(end,format='mixed')

        if volume.strip().lower()=="true":
            volume = True
        elif volume.strip().lower()=="false":
            volume = False

        if starting not in data['Date'].dt.normalize().values:
            print("starting date is invalid")

        elif ending not in data['Date'].dt.normalize().values:
            print("ending date is invalid")

        elif starting<ending:
            if indicator == "Bollinger Band" :
                data = data[(data['Date']>=starting)&(data['Date']<=ending)]
                data['bb'] = ta.volatility.bollinger_mavg(data['Close'],window=window)
                data['ubb'] = ta.volatility.bollinger_hband(data['Close'],window=window,window_dev=2)
                data['lbb'] = ta.volatility.bollinger_lband(data['Close'],window=window,window_dev=2)

                if type == "aggressive":
                    buy = 0.95
                    sell = 1.05

                elif type == "moderate":
                    buy = 0.98
                    sell = 1.02

                else:
                    buy = 1
                    sell = 1

                if Position =="long":
                    capital = initialCapital
                    holding = 0
                    tradeHistory = []

                    for index, row in data.iterrows():
                        ClosePrise = row['Close']

                        if (ClosePrise<row['lbb']*buy) and capital> ClosePrise:
                            shearToBuy = capital//ClosePrise
                            capital -= shearToBuy*ClosePrise
                            holding += shearToBuy
                            tradeHistory.append((row['Date'],"Buy",ClosePrise,holding))


                        elif (ClosePrise > row['ubb']*sell) and holding >0:
                            capital += holding*ClosePrise
                            tradeHistory.append((row['Date'],"Sell",ClosePrise,holding))
                            holding = 0

                    portfolio = capital + (holding * data.iloc[-1]['Close'])

                    netPosition = portfolio-initialCapital
                    
                    
                    fig1,ax = mpf.plot(data.set_index('Date'),
                                        type='candle',
                                        style='charles',
                                        title='Stock Price Candlestick Chart',
                                        ylabel=f'Price {price}',
                                        volume=volume,returnfig=True)
                    
                    buy_yvalues = np.nan * np.ones(len(data))
                    sell_yvalues = np.nan * np.ones(len(data))

                    for i, date in enumerate(data['Date']):
                        for t in tradeHistory:
                            if t[0]  == date and t[1] =="Buy":
                                buy_yvalues[data['Date'] == date] = t[2]

                            if t[0] == date and t[1] == "Sell":
                                sell_yvalues[data['Date'] == date] = t[2]
                    
                    
                    buy_plot = mpf.make_addplot(buy_yvalues, scatter=True, markersize=100, marker='^', color='g', panel=0, secondary_y=False)
                    sell_plot = mpf.make_addplot(sell_yvalues, scatter=True, markersize=100, marker='v', color='r', panel=0, secondary_y=False)

                    fig2,ax=mpf.plot(data.set_index('Date'),
                            type='candle',
                            style='charles',
                            title='Bollenger Band long position on the chart',
                            ylabel=f'Price {price}',
                            volume=volume,
                            addplot=[buy_plot, sell_plot],
                            returnfig=True) 
                    st.pyplot(fig1)              
                    st.pyplot(fig2)

                    return f"By {Position} position in the stock {name} with the initial capital: {symbol}{initialCapital} and the indicator: {indicator} the portfolio is :{symbol}{portfolio:.2f} and the net position is :{symbol}{netPosition:.2f}"


                elif Position == "short":
                    capital = initialCapital
                    holding = 0
                    tradeHistory = []

                    for index, row in data.iterrows():
                        ClosePrise = row['Close']

                        if (ClosePrise>row['ubb']*sell) and holding==0:
                            shearToSell = capital//ClosePrise
                            capital += shearToSell*ClosePrise
                            holding -= shearToSell
                            tradeHistory.append((row['Date'],"Sell",ClosePrise,holding))

                        elif (ClosePrise<row['lbb']*buy) and holding<0:
                            abs_holding = abs(holding)
                            capital -= abs_holding*ClosePrise
                            tradeHistory.append((row['Date'],"Buy",ClosePrise,holding))
                            holding = 0

                    unrealized_pnl = abs(holding) * data.iloc[-1]['Close'] if holding < 0 else 0
                    portfolio = capital + unrealized_pnl
                    netPosition = portfolio - initialCapital

                    fig1,ax = mpf.plot(data.set_index('Date'),
                                        type='candle',
                                        style='charles',
                                        title='Stock Price Candlestick Chart',
                                        ylabel=f'Price {price}',
                                        volume=volume,returnfig=True)
                                        
                    buy_yvalues = np.nan * np.ones(len(data))
                    sell_yvalues = np.nan * np.ones(len(data))

                    for i, date in enumerate(data['Date']):
                        for t in tradeHistory:
                            if t[0]  == date and t[1] =="Buy":
                                buy_yvalues[data['Date'] == date] = t[2]

                            if t[0] == date and t[1] == "Sell":
                                sell_yvalues[data['Date'] == date] = t[2]
    
                    buy_plot = mpf.make_addplot(buy_yvalues, scatter=True, markersize=100, marker='^', color='g', panel=0, secondary_y=False)
                    sell_plot = mpf.make_addplot(sell_yvalues, scatter=True, markersize=100, marker='v', color='r', panel=0, secondary_y=False)

                    fig2,ax=mpf.plot(data.set_index('Date'),
                            type='candle',
                            style='charles',
                            title='Bollenger Band short position on the chart',
                            ylabel=f'Price {price}',
                            volume=volume,
                            addplot=[buy_plot, sell_plot],
                            returnfig=True) 
                    st.pyplot(fig1)              
                    st.pyplot(fig2)
                    
                    return f"By {Position} position in the stock {name} with the initial capital: {symbol}{initialCapital} and the indicator: {indicator} the portfolio is :{symbol}{portfolio:.2f} and the net position is :{symbol}{netPosition:.2f}"
                
            if indicator == "RSI" :
                data = data[(data['Date']>=starting)&(data['Date']<=ending)]
                data['RSI'] = ta.momentum.rsi(data['Close'], window = window,)
                
                if type == "aggressive":
                    buy = 30
                    sell = 80

                elif type == "moderate":
                    buy = 25
                    sell = 75

                else:
                    buy = 20
                    sell = 70

                if Position == "long":                    
                    capital = initialCapital
                    holding = 0
                    trade_history = []

                    for index, row in data.iterrows():
                        ClosePrise=row['Close']

                        if (row['RSI']<buy) and capital>ClosePrise:
                            shares_to_buy = capital // ClosePrise
                            capital -= shares_to_buy * ClosePrise
                            holding += shares_to_buy
                            trade_history.append((row['Date'], 'Buy', ClosePrise, holding))
                        
                        elif(row['RSI']>sell) and holding>0:
                            capital += holding * ClosePrise
                            trade_history.append((row['Date'], 'Sell', ClosePrise, holding))
                            holding = 0
                        

                    portfolio = capital + (holding * data.iloc[-1]['Close'])
                    netPosition = portfolio-initialCapital

                    data = data[(data['Date']>=starting)&(data['Date']<=ending)]
                    fig1,ax = mpf.plot(data.set_index('Date'),
                                        type='candle',
                                        style='charles',
                                        title='Stock Price Candlestick Chart',
                                        ylabel=f'Price {price}',
                                        volume=volume,returnfig=True)
                    
                    buy_yvalues = np.nan * np.ones(len(data))
                    sell_yvalues = np.nan * np.ones(len(data))

                    for i, date in enumerate(data['Date']):
                        for t in trade_history:
                            if t[0]  == date and t[1] =="Buy":
                                buy_yvalues[data['Date'] == date] = t[2]

                            if t[0] == date and t[1] == "Sell":
                                sell_yvalues[data['Date'] == date] = t[2]

                    buy_plot = mpf.make_addplot(buy_yvalues, scatter=True, markersize=100, marker='^', color='g', panel=0, secondary_y=False)
                    sell_plot = mpf.make_addplot(sell_yvalues, scatter=True, markersize=100, marker='v', color='r', panel=0, secondary_y=False)

                    fig2,ax=mpf.plot(data.set_index('Date'),
                            type='candle',
                            style='charles',
                            title='RSI long position on the chart',
                            ylabel=f'Price {price}',
                            volume=volume,
                            addplot=[buy_plot, sell_plot],
                            returnfig=True) 
                    st.pyplot(fig1)              
                    st.pyplot(fig2)

                    return f"By {Position} position in the stock {name} with the initial capital: {symbol}{initialCapital} and the indicator: {indicator} the portfolio is :{symbol}{portfolio:.2f} and the net position is :{symbol}{netPosition:.2f}"

                if Position == "short":
                    
                    capital = initialCapital
                    holding = 0
                    trade_history = []

                    for index, row in data.iterrows():
                        ClosePrise=row['Close']

                        if (row['RSI']>sell) and holding==0:
                            shares_to_sell = capital // ClosePrise
                            capital += shares_to_sell * ClosePrise
                            holding -= shares_to_sell
                            trade_history.append((row['Date'], 'Sell', ClosePrise, holding))
                        
                        elif(row['RSI']<buy) and holding<0:
                            abs_holding = abs(holding)
                            capital -= abs_holding * ClosePrise
                            trade_history.append((row['Date'], 'Buy', ClosePrise, holding))
                            holding = 0
                        
                    unrealized_pnl = holding * data.iloc[-1]['Close'] if holding < 0 else 0
                    portfolio = capital + unrealized_pnl
                    netPosition = portfolio - initialCapital

                    fig1, ax =mpf.plot(data.set_index('Date'), 
                                       type='candle', 
                                       style='charles', 
                                       title='Stock Price Candlestick Chart',
                                       ylabel=f'Price {price}',
                                       volume=volume,
                                       returnfig=True)

                    
                    buy_yvalues = np.nan * np.ones(len(data))
                    sell_yvalues = np.nan * np.ones(len(data))

                    for i, date in enumerate(data['Date']):
                        for t in trade_history:
                            if t[0]  == date and t[1] =="Buy":
                                buy_yvalues[data['Date'] == date] = t[2]

                            if t[0] == date and t[1] == "Sell":
                                sell_yvalues[data['Date'] == date] = t[2]

                    
                    buy_plot = mpf.make_addplot(buy_yvalues, scatter=True, markersize=100, marker='^', color='g', panel=0, secondary_y=False)
                    sell_plot = mpf.make_addplot(sell_yvalues, scatter=True, markersize=100, marker='v', color='r', panel=0, secondary_y=False)

                    fig2, ax = mpf.plot(data.set_index('Date'),
                                type='candle',
                                style='charles',
                                title='RSI short position on the chart',
                                ylabel=f'Price {price}',
                                volume=volume,
                                addplot=[buy_plot, sell_plot],
                                returnfig=True)
                    st.pyplot(fig1)
                    st.pyplot(fig2)

                    return f"By {Position} position in the stock {name} with the initial capital: {symbol}{initialCapital} and the indicator: {indicator} the portfolio is :{symbol}{portfolio:.2f} and the net position is :{symbol}{netPosition:.2f}"

            if indicator=="VWAP":
                data = data[(data['Date']>=starting)&(data['Date']<=ending)]
                data['VWAP'] = ta.volume.volume_weighted_average_price(data['High'],data['Low'],data['Close'],data['Volume'],window=window)
                if type == "aggressive":
                        buy = 0.98
                        sell = 1.04

                elif type == "moderate":
                    buy = 0.96
                    sell = 1.03

                else:
                    buy = 0.95
                    sell = 1.02  


                if Position == "long":
                    capital = initialCapital
                    holding = 0
                    trade_history = []

                    for index, row in data.iterrows():
                        ClosePrise=row['Close']

                        if (ClosePrise<row['VWAP']*buy) and capital>ClosePrise:
                            shares_to_buy = capital // ClosePrise
                            capital -= shares_to_buy * ClosePrise
                            holding += shares_to_buy
                            trade_history.append((row['Date'], 'Buy', ClosePrise, holding))
                        
                        elif(ClosePrise>row['VWAP']*sell) and holding>0:
                            capital += holding * ClosePrise
                            trade_history.append((row['Date'], 'Sell', ClosePrise, holding))
                            holding = 0
                        

                    portfolio = capital + (holding * data.iloc[-1]['Close'])
                    netPosition = portfolio-initialCapital

                    data = data[(data['Date']>=starting)&(data['Date']<=ending)]
                    fig1,ax = mpf.plot(data.set_index('Date'),
                                        type='candle',
                                        style='charles',
                                        title='Stock Price Candlestick Chart',
                                        ylabel=f'Price {price}',
                                        volume=volume,returnfig=True)
                    
                    buy_yvalues = np.nan * np.ones(len(data))
                    sell_yvalues = np.nan * np.ones(len(data))

                    for i, date in enumerate(data['Date']):
                        for t in trade_history:
                            if t[0]  == date and t[1] =="Buy":
                                buy_yvalues[data['Date'] == date] = t[2]

                            if t[0] == date and t[1] == "Sell":
                                sell_yvalues[data['Date'] == date] = t[2]

                    buy_plot = mpf.make_addplot(buy_yvalues, scatter=True, markersize=100, marker='^', color='g', panel=0, secondary_y=False)
                    sell_plot = mpf.make_addplot(sell_yvalues, scatter=True, markersize=100, marker='v', color='r', panel=0, secondary_y=False)

                    fig2,ax=mpf.plot(data.set_index('Date'),
                            type='candle',
                            style='charles',
                            title='VWAP long position on the chart',
                            ylabel=f'Price {price}',
                            volume=volume,
                            addplot=[buy_plot, sell_plot],
                            returnfig=True) 
                    st.pyplot(fig1)              
                    st.pyplot(fig2)

                    return f"By {Position} position in the stock {name} with the initial capital: {symbol}{initialCapital} and the indicator: {indicator} the portfolio is :{symbol}{portfolio:.2f} and the net position is :{symbol}{netPosition:.2f}"
                
                if Position == "short":

                    capital = initialCapital
                    holding = 0
                    trade_history = []

                    for index, row in data.iterrows():
                        ClosePrise=row['Close']

                        if (ClosePrise>row['VWAP']*sell) and holding==0:
                            shares_to_sell = capital // ClosePrise
                            capital += shares_to_sell * ClosePrise
                            holding -= shares_to_sell
                            trade_history.append((row['Date'], 'Sell', ClosePrise, holding))
                        
                        elif(ClosePrise>row['VWAP']*buy) and holding<0:
                            abs_holding=abs(holding)
                            capital -= abs_holding * ClosePrise
                            trade_history.append((row['Date'], 'Buy', ClosePrise, holding))
                            holding = 0
                        

                    unrealized_pnl = abs(holding) * data.iloc[-1]['Close'] if holding < 0 else 0
                    portfolio = capital + unrealized_pnl
                    netPosition = portfolio - initialCapital

                    data = data[(data['Date']>=starting)&(data['Date']<=ending)]
                    fig1,ax = mpf.plot(data.set_index('Date'),
                                        type='candle',
                                        style='charles',
                                        title='Stock Price Candlestick Chart',
                                        ylabel=f'Price {price}',
                                        volume=volume,returnfig=True)
                    
                    buy_yvalues = np.nan * np.ones(len(data))
                    sell_yvalues = np.nan * np.ones(len(data))

                    for i, date in enumerate(data['Date']):
                        for t in trade_history:
                            if t[0]  == date and t[1] =="Buy":
                                buy_yvalues[data['Date'] == date] = t[2]

                            if t[0] == date and t[1] == "Sell":
                                sell_yvalues[data['Date'] == date] = t[2]

                    buy_plot = mpf.make_addplot(buy_yvalues, scatter=True, markersize=100, marker='^', color='g', panel=0, secondary_y=False)
                    sell_plot = mpf.make_addplot(sell_yvalues, scatter=True, markersize=100, marker='v', color='r', panel=0, secondary_y=False)

                    fig2,ax=mpf.plot(data.set_index('Date'),
                            type='candle',
                            style='charles',
                            title='VWAP short position on the chart',
                            ylabel=f'Price {price}',
                            volume=volume,
                            addplot=[buy_plot, sell_plot],
                            returnfig=True) 
                    st.pyplot(fig1)              
                    st.pyplot(fig2)

                    return f"By {Position} position in the stock {name} with the initial capital: {symbol}{initialCapital} and the indicator: {indicator} the portfolio is :{symbol}{portfolio:.2f} and the net position is :{symbol}{netPosition:.2f}"
                
            if indicator=="EMA":
                data = data[(data['Date']>=starting)&(data['Date']<=ending)]
                data['EMA'] = ta.trend.sma_indicator(data['Close'], window=window)
                if type == "aggressive":
                    buy = 0.98
                    sell = 1.04

                elif type == "moderate":
                    buy = 0.96
                    sell = 1.03

                else:
                    buy = 0.95
                    sell = 1.02

                        
                if Position == "long":
                    capital = initialCapital
                    holding = 0
                    trade_history = []

                    for index, row in data.iterrows():
                        ClosePrise=row['Close']

                        if (ClosePrise<row['EMA']*buy) and capital>ClosePrise:
                            shares_to_buy = capital // ClosePrise
                            capital -= shares_to_buy * ClosePrise
                            holding += shares_to_buy
                            trade_history.append((row['Date'], 'Buy', ClosePrise, holding))
                        
                        elif(ClosePrise>row['EMA']*sell) and holding>0:
                            capital += holding * ClosePrise
                            trade_history.append((row['Date'], 'Sell', ClosePrise, holding))
                            holding = 0
                        

                    portfolio = capital + (holding * data.iloc[-1]['Close'])
                    netPosition = portfolio-initialCapital

                    data = data[(data['Date']>=starting)&(data['Date']<=ending)]
                    fig1,ax = mpf.plot(data.set_index('Date'),
                                        type='candle',
                                        style='charles',
                                        title='Stock Price Candlestick Chart',
                                        ylabel=f'Price {price}',
                                        volume=volume,returnfig=True)
                    
                    buy_yvalues = np.nan * np.ones(len(data))
                    sell_yvalues = np.nan * np.ones(len(data))

                    for i, date in enumerate(data['Date']):
                        for t in trade_history:
                            if t[0]  == date and t[1] =="Buy":
                                buy_yvalues[data['Date'] == date] = t[2]

                            if t[0] == date and t[1] == "Sell":
                                sell_yvalues[data['Date'] == date] = t[2]

                    buy_plot = mpf.make_addplot(buy_yvalues, scatter=True, markersize=100, marker='^', color='g', panel=0, secondary_y=False)
                    sell_plot = mpf.make_addplot(sell_yvalues, scatter=True, markersize=100, marker='v', color='r', panel=0, secondary_y=False)

                    fig2,ax=mpf.plot(data.set_index('Date'),
                            type='candle',
                            style='charles',
                            title='EMA long position on the chart',
                            ylabel=f'Price {price}',
                            volume=volume,
                            addplot=[buy_plot, sell_plot],
                            returnfig=True) 
                    st.pyplot(fig1)              
                    st.pyplot(fig2)

                    return f"By {Position} position in the stock {name} with the initial capital: {symbol}{initialCapital} and the indicator: {indicator} the portfolio is :{symbol}{portfolio:.2f} and the net position is :{symbol}{netPosition:.2f}"
                
                if Position == "short":

                    capital = initialCapital
                    holding = 0
                    trade_history = []

                    for index, row in data.iterrows():
                        ClosePrise=row['Close']

                        if (ClosePrise>row['EMA']*sell) and holding==0:
                            shares_to_sell = capital // ClosePrise
                            capital += shares_to_sell * ClosePrise
                            holding -= shares_to_sell
                            trade_history.append((row['Date'], 'Sell', ClosePrise, holding))
                        
                        elif(ClosePrise>row['EMA']*buy) and holding<0:
                            abs_holding=abs(holding)
                            capital -= abs_holding * ClosePrise
                            trade_history.append((row['Date'], 'Buy', ClosePrise, holding))
                            holding = 0
                        

                    unrealized_pnl = holding * data.iloc[-1]['Close'] if holding < 0 else 0
                    portfolio = capital + unrealized_pnl
                    netPosition = portfolio - initialCapital

                    data = data[(data['Date']>=starting)&(data['Date']<=ending)]
                    fig1,ax = mpf.plot(data.set_index('Date'),
                                        type='candle',
                                        style='charles',
                                        title='Stock Price Candlestick Chart',
                                        ylabel=f'Price {price}',
                                        volume=volume,returnfig=True)
                    
                    buy_yvalues = np.nan * np.ones(len(data))
                    sell_yvalues = np.nan * np.ones(len(data))

                    for i, date in enumerate(data['Date']):
                        for t in trade_history:
                            if t[0]  == date and t[1] =="Buy":
                                buy_yvalues[data['Date'] == date] = t[2]

                            if t[0] == date and t[1] == "Sell":
                                sell_yvalues[data['Date'] == date] = t[2]

                    buy_plot = mpf.make_addplot(buy_yvalues, scatter=True, markersize=100, marker='^', color='g', panel=0, secondary_y=False)
                    sell_plot = mpf.make_addplot(sell_yvalues, scatter=True, markersize=100, marker='v', color='r', panel=0, secondary_y=False)

                    fig2,ax=mpf.plot(data.set_index('Date'),
                            type='candle',
                            style='charles',
                            title='EMA short position on the chart',
                            ylabel=f'Price {price}',
                            volume=volume,
                            addplot=[buy_plot, sell_plot],
                            returnfig=True) 
                    st.pyplot(fig1)              
                    st.pyplot(fig2)
                    return f"By {Position} position in the stock {name} with the initial capital: {symbol}{initialCapital} and the indicator: {indicator} the portfolio is :{symbol}{portfolio:.2f} and the net position is :{symbol}{netPosition:.2f}"

            if indicator == "MACD":

                data = data[(data['Date']>=starting)&(data['Date']<=ending)]
                data['MACD'] = ta.trend.macd(data['Close'])
                data['signal'] = ta.trend.macd_signal(data['Close'])

                if type == "aggressive":
                    buy = 0.98
                    sell = 1.04

                elif type == "moderate":
                    buy = 0.97
                    sell = 1.03

                else:
                    buy = 0.96
                    sell = 1.02

                if Position  == "long":
                    
                    capital = initialCapital
                    holding = 0
                    trade_history = []

                    for index, row in data.iterrows():
                        ClosePrise=row['Close']

                        if (row['MACD']>row['signal']*buy) and capital>ClosePrise:
                            shares_to_buy = capital // ClosePrise
                            capital -= shares_to_buy * ClosePrise
                            holding += shares_to_buy
                            trade_history.append((row['Date'], 'Buy', ClosePrise, holding))
                        
                        elif(row['MACD']<row['signal']*sell) and holding>0:
                            capital += holding * ClosePrise
                            trade_history.append((row['Date'], 'Sell', ClosePrise, holding))
                            holding = 0
                        

                    portfolio = capital + (holding * data.iloc[-1]['Close'])
                    netPosition = portfolio-initialCapital

                    data = data[(data['Date']>=starting)&(data['Date']<=ending)]
                    fig1,ax = mpf.plot(data.set_index('Date'),
                                        type='candle',
                                        style='charles',
                                        title='Stock Price Candlestick Chart',
                                        ylabel=f'Price {price}',
                                        volume=volume,returnfig=True)
                    
                    buy_yvalues = np.nan * np.ones(len(data))
                    sell_yvalues = np.nan * np.ones(len(data))

                    for i, date in enumerate(data['Date']):
                        for t in trade_history:
                            if t[0]  == date and t[1] =="Buy":
                                buy_yvalues[data['Date'] == date] = t[2]

                            if t[0] == date and t[1] == "Sell":
                                sell_yvalues[data['Date'] == date] = t[2]

                    buy_plot = mpf.make_addplot(buy_yvalues, scatter=True, markersize=100, marker='^', color='g', panel=0, secondary_y=False)
                    sell_plot = mpf.make_addplot(sell_yvalues, scatter=True, markersize=100, marker='v', color='r', panel=0, secondary_y=False)

                    fig2,ax=mpf.plot(data.set_index('Date'),
                            type='candle',
                            style='charles',
                            title='MACD long position on the chart',
                            ylabel=f'Price {price}',
                            volume=volume,
                            addplot=[buy_plot, sell_plot],
                            returnfig=True) 
                    
                    st.pyplot(fig1)              
                    st.pyplot(fig2)

                    return f"By {Position} position in the stock {name} with the initial capital: {symbol}{initialCapital} and the indicator: {indicator} the portfolio is :{symbol}{portfolio:.2f} and the net position is :{symbol}{netPosition:.2f}"

                if Position  == "short":
                    
                    capital = initialCapital
                    holding = 0
                    trade_history = []

                    for index, row in data.iterrows():
                        ClosePrise=row['Close']

                        if (row['MACD']<row['signal']*sell) and holding==0:
                            shares_to_sell = capital // ClosePrise
                            capital += shares_to_sell * ClosePrise
                            holding -= shares_to_sell
                            trade_history.append((row['Date'], 'Sell', ClosePrise, holding))
                        
                        elif(row['MACD']>row['signal']*buy) and holding<0:
                            abs_holding=abs(holding)
                            capital -= abs_holding * ClosePrise
                            trade_history.append((row['Date'], 'Buy', ClosePrise, holding))
                            holding = 0
                        

                    unrealized_pnl = holding * data.iloc[-1]['Close'] if holding < 0 else 0
                    portfolio = capital + unrealized_pnl
                    netPosition = portfolio - initialCapital

                    data = data[(data['Date']>=starting)&(data['Date']<=ending)]
                    fig1,ax = mpf.plot(data.set_index('Date'),
                                        type='candle',
                                        style='charles',
                                        title='Stock Price Candlestick Chart',
                                        ylabel=f'Price {price}',
                                        volume=volume,returnfig=True)
                    
                    buy_yvalues = np.nan * np.ones(len(data))
                    sell_yvalues = np.nan * np.ones(len(data))

                    for i, date in enumerate(data['Date']):
                        for t in trade_history:
                            if t[0]  == date and t[1] =="Buy":
                                buy_yvalues[data['Date'] == date] = t[2]

                            if t[0] == date and t[1] == "Sell":
                                sell_yvalues[data['Date'] == date] = t[2]

                    buy_plot = mpf.make_addplot(buy_yvalues, scatter=True, markersize=100, marker='^', color='g', panel=0, secondary_y=False)
                    sell_plot = mpf.make_addplot(sell_yvalues, scatter=True, markersize=100, marker='v', color='r', panel=0, secondary_y=False)

                    fig2,ax=mpf.plot(data.set_index('Date'),
                            type='candle',
                            style='charles',
                            title='MACD short position on the chart',
                            ylabel=f'Price {price}',
                            volume=volume,
                            addplot=[buy_plot, sell_plot],
                            returnfig=True) 
                    st.pyplot(fig1)              
                    st.pyplot(fig2)

                    return f"By {Position} position in the stock {name} with the initial capital: {symbol}{initialCapital} and the indicator: {indicator} the portfolio is :{symbol}{portfolio:.2f} and the net position is :{symbol}{netPosition:.2f}"

        elif starting>ending:
            print(f"{starting} date is greater then {ending} date")
        
    else:
        return f"{path} didn't exist"


min_date = datetime.date(201,1,1)
max_date = datetime.date(2023,12,31)

st.title("Stock Analysis with Bollinger Bands")
st.sidebar.header("Input Parameters")

# Sidebar inputs
country = st.sidebar.selectbox("Select the country",["India","USA","Japan"])
if country == "India":
    
    exchange = st.sidebar.selectbox ("Sekect an exchange",["NSE","BSE"])
    if exchange == "NSE":
        stock_name = st.sidebar.selectbox("Enter stock name",['Asian Paints', 'Axis Bank', 'Bajaj Finance', 'Bajaj Finserv', 'Bharti Airtel', 'Dr. Reddy’s Laboratories', 'HCL Technologies', 'HDFC Bank', 'HDFC Life', 'Hero MotoCorp', 'Hindustan Unilever', 'ICICI Bank', 'Infosys', 'ITC', 'JSW Steel', 'Kotak Mahindra Bank', 'Larsen and Toubro', 'Mahindra and Mahindra', 'Maruti Suzuki', 'NTPC', 'ONGC', 'Power Grid Corporation', 'Reliance Industries', 'State Bank of India', 'Sun Pharma', 'Tata Motors', 'Tata Steel', 'TCS', 'UltraTech Cement', 'Wipro'] )
    elif exchange == "BSE":
        stock_name = st.sidebar.selectbox("Enter stock name",['APOLLO TYRE', 'ASHOK LEYLAND', 'ATUL AUTO', 'BAJAJ AUTO', 'BOSCH', 'CEAT TYRES', 'EICHER MOTORS', 'ESCORTS MOTORS', 'EXIDE IND', 'FORCE MOTORS', 'HERO MOTO CORP', 'JK TYRE', 'Mahindra & Mahindra', 'MARUTI', 'MRF TYRES', 'SML ISUZU', 'SONA COMSTAR', 'TATA MOTORS', 'TATA POWER', 'TVS MOTORS'] )
elif country == "USA":
    stock_name = st.sidebar.selectbox("Enter stock name",['Alphabet Inc', 'Amazon', 'Apple Inc', 'Bank of America', 'Coca Cola', 'Home Depot', 'Intel', 'Johnson and Johnson', 'JPMorgan Chase', 'Mastercard', 'Meta Platforms', 'Microsoft Corp', 'NVIDIA', 'PepsiCo', 'Pfizer', 'Procter and Gamble', 'Tesla Inc', 'UnitedHealth', 'Visa', 'Walmart'])
    exchange = None

else:
    stock_name = st.sidebar.selectbox("Enter stock name",['Daiichi Sankyo Co Ltd', 'Daikin Industries Ltd', 'Fast Retailing Co Ltd', 'Hitachi Ltd', 'Honda Motor Co Ltd', 'KDDI Corp', 'Keyence Corp', 'Mitsubishi UFJ Financial Group', 'Mitsui and Co Ltd', 'Mizuho Financial Group Inc', 'Nintendo Co Ltd', 'Nippon Telegraph and Telephone Corp', 'Panasonic Holdings Corp', 'Shin-Etsu Chemical Co Ltd', 'SoftBank Group Corp', 'Sony Group Corp', 'Sumitomo Mitsui Financial Group Inc', 'Takeda Pharmaceutical Co Ltd', 'Tokyo Electron Ltd', 'Toyota Motor Corp'])
    exchange =  None


initial_capital = st.sidebar.number_input("Enter initial capital", min_value=0, value=100000)
indicator = st.sidebar.selectbox("Select indicator", ['Bollinger Band','RSI','VWAP','EMA','MACD'])
window = st.sidebar.number_input("Enter window size", min_value=16, value=50,max_value = 100)
risk_type = st.sidebar.selectbox("Select risk type", ["aggressive", "moderate", "low"])
position = st.sidebar.selectbox("Select position", ["long", "short"])
start_date = st.sidebar.date_input("Select start date",min_value=min_date, max_value=max_date)
end_date = st.sidebar.date_input("Select end date",min_value=min_date, max_value=max_date)
volume = st.sidebar.selectbox("Show volume?", ["True", "False"])

# Trigger analysis
if st.sidebar.button("Run Analysis"):
    result = bb(country,exchange,stock_name, initial_capital, indicator, window, risk_type, position, start_date, end_date, volume)
    st.write(result)



# name = input("Enter stock name: ")
# capital = int(input("Enter initial capital: "))
# indicator = input("Enter indicator (Bollinger Band/RSI/VWAP/EMA/MACD): ")
# window = int(input("Enter window size: "))
# risk_type = input("Enter risk type (aggressive/moderate/low): ")
# position = input("Enter your position(long/short): ")
# start_date = input("Enter start date (YYYY-MM-DD): ")
# end_date = input("Enter end date (YYYY-MM-DD): ")
# volume = input("Want to seee the volume (True/False): ")


# print(bb(name, capital,indicator,window,risk_type,position,start_date,end_date,volume))

# print(bb("Reliance Industries",20000,"MACD",17,"aggressive","short","2013-01-07","2021-03-18"," false"))

    
    




