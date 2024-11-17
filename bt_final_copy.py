import pandas as pd
import streamlit as st
import os
import ta
import mplfinance as mpf
import numpy as np
import datetime
st.title('Stock Analysis')
st.title("Do you ant to use indicator")

choices = ["Yes","No"]

action = st. radio("Select an option:", choices, index=1)

if action == "Yes":

    
    def bb(country,exchange,name,initialCapital,indicator,window,type,Position,start,end,volume,hodl):
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
            st.error("Select a valid country")
            
        if os.path.exists(path):
            data =pd.read_csv(path)
    
            data['Date'] = pd.to_datetime(data['Date']).dt.tz_localize(None)
            starting = pd.to_datetime(start,format='mixed')
            ending = pd.to_datetime(end,format='mixed')
    
            if volume.strip().lower()=="true":
                volume = True
            elif volume.strip().lower()=="false":
                volume = False

            if hodl.strip().lower()=="true":
                hodl = True
            elif hodl.strip().lower()=="false":
                hodl = False
    
            if starting not in data['Date'].dt.normalize().values:
                st.error("starting date is invalid")
    
            elif ending not in data['Date'].dt.normalize().values:
                st.error("ending date is invalid")
    
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
                                tradeHistory.append((row['Date'],"Buy",ClosePrise,holding,capital))
    
    
                            elif (ClosePrise > row['ubb']*sell) and holding >0:
                                capital += holding*ClosePrise
                                tradeHistory.append((row['Date'],"Sell",ClosePrise,holding,capital))
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
                        if not tradeHistory:
                            return "No trade is happened"
                        else:
                            if hodl:
                                remcap = tradeHistory[0][4]
                                p = tradeHistory[0][2]
                                d = data.iloc[-1]['Close']
                                h = tradeHistory[0][3]
                                v = (d*h)-(p*h)
                                cap= v+remcap
                                nk=cap-initialCapital
                                return f"If you hold the stock of {name} without making any trade on the investment: {symbol}{initialCapital} you will get:{symbol} {cap:.2f} and your net position will be: {symbol}{nk:.2f}"
                                   
                            else:                    
                                st.pyplot(fig2)
                                return f"The stock {name} with the initial capital: {symbol}{initialCapital} and the indicator: {indicator} the portfolio is :{symbol}{portfolio:.2f} and the net position is :{symbol}{netPosition:.2f}"

    
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
                                tradeHistory.append((row['Date'],"Sell",ClosePrise,holding,capital))
    
                            elif (ClosePrise<row['lbb']*buy) and holding<0:
                                abs_holding = abs(holding)
                                capital -= abs_holding*ClosePrise
                                tradeHistory.append((row['Date'],"Buy",ClosePrise,holding,capital))
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
                        if not tradeHistory:
                            return "No trade is happened"
                        else:
                            if hodl:
                                remcap = tradeHistory[0][4]
                                p = tradeHistory[0][2]
                                d = data.iloc[-1]['Close']
                                h = tradeHistory[0][3]
                                v = (d*h)-(p*h)
                                cap= v+remcap
                                nk=cap-initialCapital
                                return f"If you hold the stock of {name} without making any trade on the investment: {symbol}{initialCapital} you will get:{symbol} {cap:.2f} and your net position will be: {symbol}{nk:.2f}"
        
        
                            
                            else:                    
                                st.pyplot(fig2)
                                return f"The stock {name} with the initial capital: {symbol}{initialCapital} and the indicator: {indicator} the portfolio is :{symbol}{portfolio:.2f} and the net position is :{symbol}{netPosition:.2f}"
         
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
                        tradeHistory = []
    
                        for index, row in data.iterrows():
                            ClosePrise=row['Close']
    
                            if (row['RSI']<buy) and capital>ClosePrise:
                                shares_to_buy = capital // ClosePrise
                                capital -= shares_to_buy * ClosePrise
                                holding += shares_to_buy
                                tradeHistory.append((row['Date'], 'Buy', ClosePrise, holding,capital))
                            
                            elif(row['RSI']>sell) and holding>0:
                                capital += holding * ClosePrise
                                tradeHistory.append((row['Date'], 'Sell', ClosePrise, holding,capital))
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
                                title='RSI long position on the chart',
                                ylabel=f'Price {price}',
                                volume=volume,
                                addplot=[buy_plot, sell_plot],
                                returnfig=True) 
                        st.pyplot(fig1)              
                        if not tradeHistory:
                            return "No trade is happend"
                        else:
                            if hodl:
                                remcap = tradeHistory[0][4]
                                p = tradeHistory[0][2]
                                d = data.iloc[-1]['Close']
                                h = tradeHistory[0][3]
                                v = (d*h)-(p*h)
                                cap= v+remcap
                                nk=cap-initialCapital
                                return f"If you hold the stock of {name} without making any trade on the investment: {symbol}{initialCapital} you will get:{symbol} {cap:.2f} and your net position will be: {symbol}{nk:.2f}"
        
        
                            
                            else:                    
                                st.pyplot(fig2)
                                return f"The stock {name} with the initial capital: {symbol}{initialCapital} and the indicator: {indicator} the portfolio is :{symbol}{portfolio:.2f} and the net position is :{symbol}{netPosition:.2f}"
         
                    if Position == "short":
                        
                        capital = initialCapital
                        holding = 0
                        tradeHistory = []
    
                        for index, row in data.iterrows():
                            ClosePrise=row['Close']
    
                            if (row['RSI']>sell) and holding==0:
                                shares_to_sell = capital // ClosePrise
                                capital += shares_to_sell * ClosePrise
                                holding -= shares_to_sell
                                tradeHistory.append((row['Date'], 'Sell', ClosePrise, holding,capital))
                            
                            elif(row['RSI']<buy) and holding<0:
                                abs_holding = abs(holding)
                                capital -= abs_holding * ClosePrise
                                tradeHistory.append((row['Date'], 'Buy', ClosePrise, holding,capital))
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
                            for t in tradeHistory:
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
                        if not tradeHistory:
                            return "No trade is happend"
                        else:
                            if hodl:
                                remcap = tradeHistory[0][4]
                                p = tradeHistory[0][2]
                                d = data.iloc[-1]['Close']
                                h = tradeHistory[0][3]
                                v = (d*h)-(p*h)
                                cap= v+remcap
                                nk=cap-initialCapital
                                return f"If you hold the stock of {name} without making any trade on the investment: {symbol}{initialCapital} you will get:{symbol} {cap:.2f} and your net position will be: {symbol}{nk:.2f}"
        
                            else:                    
                                st.pyplot(fig2)
                                return f"The stock {name} with the initial capital: {symbol}{initialCapital} and the indicator: {indicator} the portfolio is :{symbol}{portfolio:.2f} and the net position is :{symbol}{netPosition:.2f}"
          
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
                        tradeHistory = []
    
                        for index, row in data.iterrows():
                            ClosePrise=row['Close']
    
                            if (ClosePrise<row['VWAP']*buy) and capital>ClosePrise:
                                shares_to_buy = capital // ClosePrise
                                capital -= shares_to_buy * ClosePrise
                                holding += shares_to_buy
                                tradeHistory.append((row['Date'], 'Buy', ClosePrise, holding,capital))
                            
                            elif(ClosePrise>row['VWAP']*sell) and holding>0:
                                capital += holding * ClosePrise
                                tradeHistory.append((row['Date'], 'Sell', ClosePrise, holding,capital))
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
                                title='VWAP long position on the chart',
                                ylabel=f'Price {price}',
                                volume=volume,
                                addplot=[buy_plot, sell_plot],
                                returnfig=True) 
                        st.pyplot(fig1)              
                        if not tradeHistory:
                            return "No trade is happend"
                        else:
                            if hodl:
                                remcap = tradeHistory[0][4]
                                p = tradeHistory[0][2]
                                d = data.iloc[-1]['Close']
                                h = tradeHistory[0][3]
                                v = (d*h)-(p*h)
                                cap= v+remcap
                                nk=cap-initialCapital
                                return f"If you hold the stock of {name} without making any trade on the investment: {symbol}{initialCapital} you will get:{symbol} {cap:.2f} and your net position will be: {symbol}{nk:.2f}"
        
        
                            
                            else:                    
                                st.pyplot(fig2)
                                return f"The stock {name} with the initial capital: {symbol}{initialCapital} and the indicator: {indicator} the portfolio is :{symbol}{portfolio:.2f} and the net position is :{symbol}{netPosition:.2f}"
         
                    if Position == "short":
    
                        capital = initialCapital
                        holding = 0
                        tradeHistory = []
    
                        for index, row in data.iterrows():
                            ClosePrise=row['Close']
    
                            if (ClosePrise>row['VWAP']*sell) and holding==0:
                                shares_to_sell = capital // ClosePrise
                                capital += shares_to_sell * ClosePrise
                                holding -= shares_to_sell
                                tradeHistory.append((row['Date'], 'Sell', ClosePrise, holding,capital))
                            
                            elif(ClosePrise>row['VWAP']*buy) and holding<0:
                                abs_holding=abs(holding)
                                capital -= abs_holding * ClosePrise
                                tradeHistory.append((row['Date'], 'Buy', ClosePrise, holding,capital))
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
                                title='VWAP short position on the chart',
                                ylabel=f'Price {price}',
                                volume=volume,
                                addplot=[buy_plot, sell_plot],
                                returnfig=True) 
                        st.pyplot(fig1)              
                        if not tradeHistory:
                            return "No trade is happend"
                        else:
                            if hodl:
                                remcap = tradeHistory[0][4]
                                p = tradeHistory[0][2]
                                d = data.iloc[-1]['Close']
                                h = tradeHistory[0][3]
                                v = (d*h)-(p*h)
                                cap= v+remcap
                                nk=cap-initialCapital
                                return f"If you hold the stock of {name} without making any trade on the investment: {symbol}{initialCapital} you will get:{symbol} {cap:.2f} and your net position will be: {symbol}{nk:.2f}"
        
        
                            
                            else:                    
                                st.pyplot(fig2)
                                return f"The stock {name} with the initial capital: {symbol}{initialCapital} and the indicator: {indicator} the portfolio is :{symbol}{portfolio:.2f} and the net position is :{symbol}{netPosition:.2f}"
         
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
                        tradeHistory = []
    
                        for index, row in data.iterrows():
                            ClosePrise=row['Close']
    
                            if (ClosePrise<row['EMA']*buy) and capital>ClosePrise:
                                shares_to_buy = capital // ClosePrise
                                capital -= shares_to_buy * ClosePrise
                                holding += shares_to_buy
                                tradeHistory.append((row['Date'], 'Buy', ClosePrise, holding,capital))
                            
                            elif(ClosePrise>row['EMA']*sell) and holding>0:
                                capital += holding * ClosePrise
                                tradeHistory.append((row['Date'], 'Sell', ClosePrise, holding,capital))
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
                                title='EMA long position on the chart',
                                ylabel=f'Price {price}',
                                volume=volume,
                                addplot=[buy_plot, sell_plot],
                                returnfig=True) 
                        st.pyplot(fig1)              
                        if not tradeHistory:
                            return "No trade is happend"
                        else:
                            if hodl:
                                remcap = tradeHistory[0][4]
                                p = tradeHistory[0][2]
                                d = data.iloc[-1]['Close']
                                h = tradeHistory[0][3]
                                v = (d*h)-(p*h)
                                cap= v+remcap
                                nk=cap-initialCapital
                                return f"If you hold the stock of {name} without making any trade on the investment: {symbol}{initialCapital} you will get:{symbol} {cap:.2f} and your net position will be: {symbol}{nk:.2f}"
        
        
                            
                            else:                    
                                st.pyplot(fig2)
                                return f"The stock {name} with the initial capital: {symbol}{initialCapital} and the indicator: {indicator} the portfolio is :{symbol}{portfolio:.2f} and the net position is :{symbol}{netPosition:.2f}"
                          
                    if Position == "short":
    
                        capital = initialCapital
                        holding = 0
                        tradeHistory = []
    
                        for index, row in data.iterrows():
                            ClosePrise=row['Close']
    
                            if (ClosePrise>row['EMA']*sell) and holding==0:
                                shares_to_sell = capital // ClosePrise
                                capital += shares_to_sell * ClosePrise
                                holding -= shares_to_sell
                                tradeHistory.append((row['Date'], 'Sell', ClosePrise, holding,capital))
                            
                            elif(ClosePrise>row['EMA']*buy) and holding<0:
                                abs_holding=abs(holding)
                                capital -= abs_holding * ClosePrise
                                tradeHistory.append((row['Date'], 'Buy', ClosePrise, holding,capital))
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
                                title='EMA short position on the chart',
                                ylabel=f'Price {price}',
                                volume=volume,
                                addplot=[buy_plot, sell_plot],
                                returnfig=True) 
                        st.pyplot(fig1)              
                        if not tradeHistory:
                            return "No trade is happend"
                        else:
                            if hodl:
                                remcap = tradeHistory[0][4]
                                p = tradeHistory[0][2]
                                d = data.iloc[-1]['Close']
                                h = tradeHistory[0][3]
                                v = (d*h)-(p*h)
                                cap= v+remcap
                                nk=cap-initialCapital
                                return f"If you hold the stock of {name} without making any trade on the investment: {symbol}{initialCapital} you will get:{symbol} {cap:.2f} and your net position will be: {symbol}{nk:.2f}"
        
        
                            
                            else:                    
                                st.pyplot(fig2)
                                return f"The stock {name} with the initial capital: {symbol}{initialCapital} and the indicator: {indicator} the portfolio is :{symbol}{portfolio:.2f} and the net position is :{symbol}{netPosition:.2f}"
         
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
                        tradeHistory = []
    
                        for index, row in data.iterrows():
                            ClosePrise=row['Close']
    
                            if (row['MACD']>row['signal']*buy) and capital>ClosePrise:
                                shares_to_buy = capital // ClosePrise
                                capital -= shares_to_buy * ClosePrise
                                holding += shares_to_buy
                                tradeHistory.append((row['Date'], 'Buy', ClosePrise, holding,capital))
                            
                            elif(row['MACD']<row['signal']*sell) and holding>0:
                                capital += holding * ClosePrise
                                tradeHistory.append((row['Date'], 'Sell', ClosePrise, holding,capital))
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
                                title='MACD long position on the chart',
                                ylabel=f'Price {price}',
                                volume=volume,
                                addplot=[buy_plot, sell_plot],
                                returnfig=True) 
                        
                        st.pyplot(fig1)              
                        if not tradeHistory:
                            return "No trade is happend"
                        else:
                            if hodl:
                                remcap = tradeHistory[0][4]
                                p = tradeHistory[0][2]
                                d = data.iloc[-1]['Close']
                                h = tradeHistory[0][3]
                                v = (d*h)-(p*h)
                                cap= v+remcap
                                nk=cap-initialCapital
                                return f"If you hold the stock of {name} without making any trade on the investment: {symbol}{initialCapital} you will get:{symbol} {cap:.2f} and your net position will be: {symbol}{nk:.2f}"
        
        
                            
                            else:                    
                                st.pyplot(fig2)
                                return f"The stock {name} with the initial capital: {symbol}{initialCapital} and the indicator: {indicator} the portfolio is :{symbol}{portfolio:.2f} and the net position is :{symbol}{netPosition:.2f}"
         
                    if Position  == "short":
                        
                        capital = initialCapital
                        holding = 0
                        tradeHistory = []
    
                        for index, row in data.iterrows():
                            ClosePrise=row['Close']
    
                            if (row['MACD']<row['signal']*sell) and holding==0:
                                shares_to_sell = capital // ClosePrise
                                capital += shares_to_sell * ClosePrise
                                holding -= shares_to_sell
                                tradeHistory.append((row['Date'], 'Sell', ClosePrise, holding,capital))
                            
                            elif(row['MACD']>row['signal']*buy) and holding<0:
                                abs_holding=abs(holding)
                                capital -= abs_holding * ClosePrise
                                tradeHistory.append((row['Date'], 'Buy', ClosePrise, holding,capital))
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
                                title='MACD short position on the chart',
                                ylabel=f'Price {price}',
                                volume=volume,
                                addplot=[buy_plot, sell_plot],
                                returnfig=True) 
                        st.pyplot(fig1)              
                        if not tradeHistory:
                            return "No trade is happend"
                        else:
                            if hodl:
                                remcap = tradeHistory[0][4]
                                p = tradeHistory[0][2]
                                d = data.iloc[-1]['Close']
                                h = tradeHistory[0][3]
                                v = (d*h)-(p*h)
                                cap= v+remcap
                                nk=cap-initialCapital
                                return f"If you hold the stock of {name} without making any trade on the investment: {symbol}{initialCapital} you will get:{symbol} {cap:.2f} and your net position will be: {symbol}{nk:.2f}"
        
        
                            
                            else:                    
                                st.pyplot(fig2)
                                return f"The stock {name} with the initial capital: {symbol}{initialCapital} and the indicator: {indicator} the portfolio is :{symbol}{portfolio:.2f} and the net position is :{symbol}{netPosition:.2f}"
         
            elif starting>ending:
                st.error(f"{starting} date is greater then {ending} date")
            
        else:
            st.error(f"{path} didn't exist")
    
    
    min_date = datetime.date(2013, 1, 1)
    max_date = datetime.date(2024,8,24)
    
    st.title("Stock Analysis with Bollinger Bands")
    st. header("Input Parameters")
    
    country = st. selectbox("Select the country",["India","USA","Japan"])
    if country == "India":
        
        exchange = st. selectbox ("Sekect an exchange",["NSE","BSE"])
        if exchange == "NSE":
            stock_name = st. selectbox("Enter stock name",['Asian Paints', 'Axis Bank', 'Bajaj Finance', 'Bajaj Finserv', 'Bharti Airtel', 'Dr. Reddy’s Laboratories', 'HCL Technologies', 'HDFC Bank', 'HDFC Life', 'Hero MotoCorp', 'Hindustan Unilever', 'ICICI Bank', 'Infosys', 'ITC', 'JSW Steel', 'Kotak Mahindra Bank', 'Larsen and Toubro', 'Mahindra and Mahindra', 'Maruti Suzuki', 'NTPC', 'ONGC', 'Power Grid Corporation', 'Reliance Industries', 'State Bank of India', 'Sun Pharma', 'Tata Motors', 'Tata Steel', 'TCS', 'UltraTech Cement', 'Wipro'] )
        elif exchange == "BSE":
            stock_name = st. selectbox("Enter stock name",['APOLLO TYRE', 'ASHOK LEYLAND', 'ATUL AUTO', 'BAJAJ AUTO', 'BOSCH', 'CEAT TYRES', 'EICHER MOTORS', 'ESCORTS MOTORS', 'EXIDE IND', 'FORCE MOTORS', 'HERO MOTO CORP', 'JK TYRE', 'Mahindra & Mahindra', 'MARUTI', 'MRF TYRES', 'SML ISUZU', 'SONA COMSTAR', 'TATA MOTORS', 'TATA POWER', 'TVS MOTORS'] )
    elif country == "USA":
        stock_name = st. selectbox("Enter stock name",['Alphabet Inc', 'Amazon', 'Apple Inc', 'Bank of America', 'Coca Cola', 'Home Depot', 'Intel', 'Johnson and Johnson', 'JPMorgan Chase', 'Mastercard', 'Meta Platforms', 'Microsoft Corp', 'NVIDIA', 'PepsiCo', 'Pfizer', 'Procter and Gamble', 'Tesla Inc', 'UnitedHealth', 'Visa', 'Walmart'])
        exchange = None
    
    else:
        stock_name = st. selectbox("Enter stock name",['Daiichi Sankyo Co Ltd', 'Daikin Industries Ltd', 'Fast Retailing Co Ltd', 'Hitachi Ltd', 'Honda Motor Co Ltd', 'KDDI Corp', 'Keyence Corp', 'Mitsubishi UFJ Financial Group', 'Mitsui and Co Ltd', 'Mizuho Financial Group Inc', 'Nintendo Co Ltd', 'Nippon Telegraph and Telephone Corp', 'Panasonic Holdings Corp', 'Shin-Etsu Chemical Co Ltd', 'SoftBank Group Corp', 'Sony Group Corp', 'Sumitomo Mitsui Financial Group Inc', 'Takeda Pharmaceutical Co Ltd', 'Tokyo Electron Ltd', 'Toyota Motor Corp'])
        exchange =  None
    
    
    initial_capital = st. number_input("Enter initial capital", min_value=0, value=100000)
    indicator = st. selectbox("Select indicator", ['Bollinger Band','RSI','VWAP','EMA','MACD'])
    window = st. number_input("Enter window size", min_value=16, value=50,max_value = 100)
    risk_type = st. selectbox("Select risk type", ["aggressive", "moderate", "low"])
    position = st. selectbox("Select position", ["long", "short"])
    start_date = st. date_input("Select start date",min_value=min_date, max_value=max_date)
    end_date = st. date_input("Select end date",min_value=min_date, max_value=max_date)
    volume = st. selectbox("Show volume?", ["True", "False"])
    hodl = st. selectbox("Want to hold without trade?", ["True", "False"])

    if st. button("Run Analysis"):
        result = bb(country,exchange,stock_name, initial_capital, indicator, window, risk_type, position, start_date, end_date, volume,hodl)
        st.write(result)
elif action == "No":
    def portfolio(country,exchange,name, capital, starting, ending):
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
            st.error("Select a valid country")

        if os.path.exists(path):
            data = pd.read_csv(path)

            data['Date'] = pd.to_datetime(data['Date']).dt.tz_localize(None)
            starting = pd.to_datetime(starting, format="mixed")
            ending = pd.to_datetime(ending, format="mixed")
            
            if starting not in data['Date'].dt.normalize().values:
                st.error("starting date is invalid")
                
    
            elif ending not in data['Date'].dt.normalize().values:
                st.error("ending date is invalid")
                
    
            elif starting < ending:
                fil_df = data[(data['Date'] >= starting) & (data['Date'] <= ending)]
                
                if fil_df.empty:
                    st.error( f"No data available for the stock '{name}' within the selected date range ({starting} to {ending}).")

                fig,ax = mpf.plot(fil_df.set_index('Date'), type='candle', style='charles',
                        title='Stock Price Candlestick Chart', ylabel='Price (₹)', volume=True,returnfig=True)

                st.pyplot(fig)
                buyClosePrice = fil_df.iloc[0]['Close']
                sellClosePrice = fil_df.iloc[-1]['Close']

                if capital > buyClosePrice:
                    sharesCanBuy = capital // buyClosePrice
                    usedCapital = sharesCanBuy * buyClosePrice
                    remainingCapital = capital - usedCapital
                    portfolioValue = sharesCanBuy * sellClosePrice + remainingCapital
                    netPosition = portfolioValue - capital

                    return f"You can buy {sharesCanBuy} shares of {name} at ({symbol}{buyClosePrice:.2f}) each. Your portfolio value at the end will be ({symbol}{portfolioValue:.2f}) with a net position of ({symbol}{netPosition:.2f})."
                else:
                    return f"Your initial capital ({symbol}{capital:.2f}) is lower than the stock's opening price ({symbol}{buyClosePrice:.2f}). Unable to buy any shares."
            else:
                st.error(f"Starting date ({starting}) is greater than ending date ({ending}).")
        else:
            st.error(f"File for '{name}' does not exist at the path {path}.")


    min_date = datetime.date(2013, 1, 1)
    max_date = datetime.date(2024,8,24)
    st.title('Stock Analysis without Technical Indicators')

    country = st. selectbox("Select the country",["India","USA","Japan"])
    if country == "India":
        
        exchange = st. selectbox ("Sekect an exchange",["NSE","BSE"])
        if exchange == "NSE":
            stock_name = st. selectbox("Enter stock name",['Asian Paints', 'Axis Bank', 'Bajaj Finance', 'Bajaj Finserv', 'Bharti Airtel', 'Dr. Reddy’s Laboratories', 'HCL Technologies', 'HDFC Bank', 'HDFC Life', 'Hero MotoCorp', 'Hindustan Unilever', 'ICICI Bank', 'Infosys', 'ITC', 'JSW Steel', 'Kotak Mahindra Bank', 'Larsen and Toubro', 'Mahindra and Mahindra', 'Maruti Suzuki', 'NTPC', 'ONGC', 'Power Grid Corporation', 'Reliance Industries', 'State Bank of India', 'Sun Pharma', 'Tata Motors', 'Tata Steel', 'TCS', 'UltraTech Cement', 'Wipro'] )
        elif exchange == "BSE":
            stock_name = st. selectbox("Enter stock name",['APOLLO TYRE', 'ASHOK LEYLAND', 'ATUL AUTO', 'BAJAJ AUTO', 'BOSCH', 'CEAT TYRES', 'EICHER MOTORS', 'ESCORTS MOTORS', 'EXIDE IND', 'FORCE MOTORS', 'HERO MOTO CORP', 'JK TYRE', 'Mahindra & Mahindra', 'MARUTI', 'MRF TYRES', 'SML ISUZU', 'SONA COMSTAR', 'TATA MOTORS', 'TATA POWER', 'TVS MOTORS'] )
    elif country == "USA":
        stock_name = st. selectbox("Enter stock name",['Alphabet Inc', 'Amazon', 'Apple Inc', 'Bank of America', 'Coca Cola', 'Home Depot', 'Intel', 'Johnson and Johnson', 'JPMorgan Chase', 'Mastercard', 'Meta Platforms', 'Microsoft Corp', 'NVIDIA', 'PepsiCo', 'Pfizer', 'Procter and Gamble', 'Tesla Inc', 'UnitedHealth', 'Visa', 'Walmart'])
        exchange = None
    
    else:
        stock_name = st. selectbox("Enter stock name",['Daiichi Sankyo Co Ltd', 'Daikin Industries Ltd', 'Fast Retailing Co Ltd', 'Hitachi Ltd', 'Honda Motor Co Ltd', 'KDDI Corp', 'Keyence Corp', 'Mitsubishi UFJ Financial Group', 'Mitsui and Co Ltd', 'Mizuho Financial Group Inc', 'Nintendo Co Ltd', 'Nippon Telegraph and Telephone Corp', 'Panasonic Holdings Corp', 'Shin-Etsu Chemical Co Ltd', 'SoftBank Group Corp', 'Sony Group Corp', 'Sumitomo Mitsui Financial Group Inc', 'Takeda Pharmaceutical Co Ltd', 'Tokyo Electron Ltd', 'Toyota Motor Corp'])
        exchange =  None
    
    capital = st. number_input("Enter initial capital :", min_value=1, value=1000)
    start_date = st. date_input("Select start date",min_value=min_date, max_value=max_date)
    end_date = st. date_input("Select end date",min_value=min_date, max_value=max_date)

    if st. button("Analyze Stock"):
        result = portfolio(country,exchange,stock_name, capital, start_date, end_date)
        if result:
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

    
    


