import datetime
import pandas as pd 
import pdb
import xlwings as xw 
from pprint import pprint
import os
from colorama import init
from colorama import Fore, Back, Style 
import talib



def time_extract(data):
	time = data[10:16]
	return time

def date_extract(data):
	date = data[0:10]
	return date

def apply_indicators(data):
	data['recent_volume'] = talib.MA(data['volume'], timeperiod = 30, matype=0)
	data['average_volume'] = talib.MA(data['volume'], timeperiod = 150, matype=0)
	data['average_volume_ma9'] = talib.MA(data['volume'], timeperiod = 9, matype=0)

	data['ma15'] = talib.MA(data['close'],timeperiod = 15, matype=0)
	data['ma30'] = talib.MA(data['close'],timeperiod = 30, matype=0)
	data['ma5']  = talib.MA(data['close'],timeperiod = 5, matype=0)
	data['ma8']  = talib.MA(data['close'],timeperiod = 8, matype=0)
	data['ma13'] = talib.MA(data['close'],timeperiod = 13, matype=0)

	data['rsi']  = talib.RSI(data['close'], timeperiod = 14)
	data['adx']  = talib.ADX(data['high'], data['low'], data['close'], timeperiod=14)

	data['prev_close'] = data['close'].shift(1)
	data['prev_to_prev_close'] = data['close'].shift(2)
	return data

status = {'name' : None,
		  'date' : None,
		  'entry_time' : None,
		  'entry_price': None,
		  'buy_sell' : None,
		  'qty' : None,
		  'sl' : None,
		  'exit_time' : None,
		  'exit_price' : None,
		  'pnl' : None,
		  'remark' : None,
		  'traded' : None,
		  'target_price' : None,
		  'trade_number' : None}

final = []
profit_loss_dict = {}
trades_entered = []
df_pnl = pd.DataFrame()


qty = 1000
trade_number = 0
sl_percent = 0.004 # sl_percent = 0.004 &&& tg_percent_buy = 1.006 have been proved effective so far
tg_percent_buy = 1.006
tg_percent_sell = 0.006

h_rsi = 70
l_rsi = 25

#watchlist = ['TATAMOTORS']
#watchlist = ['JSWSTEEL','TATASTEEL','HINDALCO','UPL','DRREDDY','RELIANCE','GRASIM','ULTRACEMCO','DIVISLAB']
watchlist = ['COALINDIA','GRASIM','DIVISLAB','IOC','SUNPHARMA','DRREDDY','BPCL','WIPRO','ONGC','CIPLA','SBILIFE','POWERGRID',
'INDUSINDBK','TATASTEEL','INFY','NTPC','BAJFINANCE','BRITANNIA','ITC','BHARTIARTL','HCLTECH','AXISBANK','NESTLEIND','TITAN','LT','RELIANCE',
'BAJAJFINSV','HEROMOTOCO','UPL','HDFCLIFE','EICHERMOT','JSWSTEEL','TECHM','SHREECEM','MARUTI','SBIN','ULTRACEMCO','HINDALCO','HINDUNILVR','TCS',
'ADANIPORTS','TATAMOTORS','ASIANPAINT','KOTAKBANK','ICICIBANK','HDFCBANK','HDFC' ] 


data_path = r'C:\Users\sandeshb\Downloads\Python Learning\Algo Trading\TRADEHULL\MyScripts\Ticker_data\5 mins'

for name in watchlist:
	data = pd.read_csv(data_path + "\\" + name + ".csv")
	data = data[['date','open','high','low','close','volume']]
	data['time'] = data['date'].apply(time_extract)
	data['dated'] = data['date'].apply(date_extract)
	data = data.set_index('date')
	data = data[['dated','time','open','high','low','close','volume']]	
	apply_indicators(data)

	data = data.iloc[150:]
	#pdb.set_trace()

	#data.to_csv(name +".csv")
	


	for index, row in data.iterrows(): 
		general_cond_1 = row.loc['time'] not in [' 09:15',' 09:20',' 09:25']
		general_cond_2 = status['traded'] is None

		#buy_condition_1 = row.loc['recent_volume'] > (row.loc['average_volume'])
		buy_condition_1 = row.loc['volume'] > (row.loc['average_volume_ma9'])
		buy_condition_2 = row.loc['ma15'] > row.loc['ma30']
		buy_condition_3 = row.loc['rsi'] > h_rsi
		buy_condition_4 = row.loc['close'] > row.loc['prev_close']
		buy_condition_5 = row.loc['ma5'] > row.loc['ma8'] > row.loc['ma13']
		buy_condition_6 = row.loc['prev_close'] > row.loc['prev_to_prev_close']
		buy_condition_7 = row.loc['adx'] > 25

		sell_condition_1 = row.loc['recent_volume'] > (row.loc['average_volume'])
		sell_condition_2 = row.loc['prev_close'] < row.loc['prev_to_prev_close']
		sell_condition_3 = row.loc['rsi'] < l_rsi
		sell_condition_4 = row.loc['close'] < row.loc['prev_close']


#BUYING ENTRY 
		if buy_condition_1 and buy_condition_5 and buy_condition_3 and general_cond_1 and general_cond_2 and buy_condition_4 and buy_condition_7:
			#print(index," YES FOUND AN ENTRY ")
			status['traded'] = 'YES'
			status['name'] = name
			status['date'] = row.loc['dated']
			status['entry_time'] = row.loc['time']
			status['entry_price'] = row.loc['close']
			status['buy_sell'] = 'BUY'
			status['qty'] = round(100000/status['entry_price'],0)
			status['sl'] = (row.loc['close'] - (row.loc['close']*sl_percent))
			
			status['exit_time'] = None
			status['exit_price'] = None
			status['pnl'] = None 
			status['remark'] = None 
			status['target_price'] = round(abs(row.loc['close']*tg_percent_buy),2)
			trade_number = trade_number + 1 
			status['trade_number'] = trade_number
			continue

#SELLING ENTRY 
#		if sell_condition_1 and sell_condition_2 and general_cond_1 and general_cond_2 and sell_condition_4:
#
#			print(index," YES FOUND AN ENTRY ")
#			status['traded'] = 'YES'
#			status['name'] = name
#			status['date'] = row.loc['dated']
#			status['entry_time'] = row.loc['time']
#			status['entry_price'] = row.loc['close']
#			status['buy_sell'] = 'SELL'
#			status['qty'] = round(50000/status['entry_price'],0)
#			status['sl'] = (status['entry_price'] + (status['entry_price']*sl_percent))
#			status['exit_time'] = None
#			status['exit_price'] = None
#			status['pnl'] = None 
#			status['remark'] = None 
#			status['target_price'] = round(abs(row.loc['close'] - row.loc['close']*tg_percent_sell),2)
#			trade_number = trade_number + 1 
#			status['trade_number'] = trade_number
#			continue

#SELLING AN ALREADY 'BUY' STOCK

		if (status['traded'] is 'YES') and (status['buy_sell'] is 'BUY'):
			if row.loc['high'] >= status['target_price']:
				print(" Target hit - Placing the sell order ",index)
				status['exit_time'] = row.loc['time']
				status['exit_price'] = status['target_price']
				status['pnl'] = round(status['target_price'] - status['entry_price'],2)*status['qty']
				status['remark'] = None 
				final.append(status)
				status = {  'name' : None,
		  					'date' : None,
		  					'entry_time' : None,
		  					'entry_price': None,
		  					'buy_sell' : None,
		  					'sl' : None,
		  					'exit_time' : None,
		  					'exit_price' : None,
		  					'pnl' : None,
		  					'remark' : None,
		  					'traded' : None,
		  					'target_price' : None,
		  					'trade_number' : None,
		  					'qty' : None}


				continue
			if row.loc['low'] <= status['sl']:
				pprint(f'Stop loss hit for {name} at {index} ' )
				#print(row.loc['low'])
				#print(status['sl'])
				status['exit_time'] = row.loc['time']
				status['exit_price'] = status['sl']
				status['pnl'] = round(status['sl'] - status['entry_price'],2)*status['qty']
				status['remark'] = 'SL-HIT'
				final.append(status)
				status = {  'name' : None,
		  					'date' : None,
		  					'entry_time' : None,
		  					'entry_price': None,
		  					'buy_sell' : None,
		  					'sl' : None,
		  					'exit_time' : None,
		  					'exit_price' : None,
		  					'pnl' : None,
		  					'remark' : None,
		  					'traded' : None,
		  					'target_price' : None,
		  					'trade_number' : None,
		  					'qty' : None}
				continue

# BUYING AN ALREADY "SELL" STOCK
		if (status['traded'] is 'YES') and (status['buy_sell'] is 'SELL'):
			if row.loc['low'] <= status['target_price']:
				print(" Target hit - Placing the BUY order ",name,index)
				status['exit_time'] = row.loc['time']
				status['exit_price'] = status['target_price']
				status['pnl'] = round(status['target_price'] - status['entry_price'],2)*status['qty']
				status['remark'] = 'TG' 
				final.append(status)
				status = {  'name' : None,
		  					'date' : None,
		  					'entry_time' : None,
		  					'entry_price': None,
		  					'buy_sell' : None,
		  					'sl' : None,
		  					'exit_time' : None,
		  					'exit_price' : None,
		  					'pnl' : None,
		  					'remark' : None,
		  					'traded' : None,
		  					'target_price' : None,
		  					'trade_number' : None,
		  					'qty' : None}

				continue
			if row.loc['high'] >= status['sl']:
				#pprint(f'Stop loss hit for {name} at {index} ' )
				#print(row.loc['low'])
				#print(status['sl'])
				status['exit_time'] = row.loc['time']
				status['exit_price'] = status['sl']
				status['pnl'] = round(status['entry_price'] - status['sl'],2)*status['qty']
				status['remark'] = 'SL-HIT'
				final.append(status)
				status = {  'name' : None,
		  					'date' : None,
		  					'entry_time' : None,
		  					'entry_price': None,
		  					'buy_sell' : None,
		  					'sl' : None,
		  					'exit_time' : None,
		  					'exit_price' : None,
		  					'pnl' : None,
		  					'remark' : None,
		  					'traded' : None,
		  					'target_price' : None,
		  					'trade_number' : None,
		  					'qty' : None}
				continue
	if len(final) != 0:
		stock = name + "final_df"
		stock = pd.DataFrame.from_dict(final, orient='columns')

		pnl_sum = round(stock['pnl'].sum(),2)
		profit_loss_dict[name] = pnl_sum
		#pdb.set_trace()
		#pprint(stock)
		print("\n")
		pprint(f'The total profit and loss for {name} is {pnl_sum}')
		stock.to_csv(name +".csv")
	
	else:
		pprint(f'No entries for stock {name}')

	print("#"*100)
	
	final = [] 
	pnl_sum = 0

print(pd.DataFrame([profit_loss_dict]).T)

