import datetime
import pandas as pd 
import pdb
import xlwings as xw 
from pprint import pprint
import os



watchlist = ['TATAMOTORS','ADANIPORTS']
data_path = r'C:\Users\sandeshb\Downloads\Python Learning\Algo Trading\TRADEHULL\MyScripts\Ticker_data\5 mins'

status = {	'name': None, 
			'date': None, 
			'entry_time': None, 
			'entry_price':	None, 
			'buy_sell': None, 
			'qty': None, 
			'sl': None, 
			'exit_time': None,
			'exit_price': None, 
			'pnl': None, 
			'remark': None, 
			'traded': None, 
			'buyfirsttime ':None, 
			'sellfirsttime ':None
			}

orb_value = {}
df1 = pd.DataFrame()


def time_extract(data):
	time = data[10:16]
	return time

def date_extract(data):
	date = data[0:10]
	return date

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

qty = 1
trade_number = 1
sl_percent = 0.005
tg_percent_buy = 1.009 
tg_percent_sell = 0.009



for name in watchlist:
	data = pd.read_csv(data_path + "\\" + name + ".csv")
	data = data[['date','open','high','low','close','volume']]
	data['time'] = data['date'].apply(time_extract)
	data['dated'] = data['date'].apply(date_extract)
	data = data.set_index('date')
	data = data[['dated','time','open','high','low','close','volume']]
	print(name)
	print(data)
	data = data
	#print(data)

	for index, row in data.iterrows():
		if row.loc['time'] in [' 09:15',' 09:20',' 09:25']:
			df1 = df1.append(row)
			temp = df1.sort_values(by=['high']).tail(1)
			day_high = (temp['high'].values[0])
			temp = df1.sort_values(by=['low']).head(1)
			day_low = (temp['low'].values[0])		

			#print(index,day_high)
			continue
# BUYING ENTRY 
		if (row.loc['close'] > day_high) and (status['traded'] is None):
			#pdb.set_trace()
			pprint(f' Trade : {trade_number} : Found an entr point at {index}. Placing the order for {name} ')
			status['traded'] = 'YES'
			status['name'] = name
			status['date'] = row.loc['dated']
			status['entry_time'] = row.loc['time']
			status['entry_price'] = row.loc['close']
			status['buy_sell'] = 'BUY'
			status['qty'] = qty
			status['sl'] = (row.loc['close'] - (row.loc['close']*sl_percent))
			status['exit_time'] = None
			status['exit_price'] = None
			status['pnl'] = None 
			status['remark'] = None 
			status['target_price'] = round(abs(row.loc['close']*tg_percent_buy),2)
			trade_number = trade_number + 1 
			status['trade_number'] = trade_number
			#pdb.set_trace()
#SELLING ENTRY
		if (row.loc['close'] < day_low) and (status['traded'] is None):
			pprint(f' Trade : {trade_number} : Found an entr point at {index}. Placing the order for {name} ')
			status['traded'] = 'YES'
			status['name'] = name
			status['date'] = row.loc['dated']
			status['entry_time'] = row.loc['time']
			status['entry_price'] = row.loc['close']
			status['buy_sell'] = 'SELL'
			status['qty'] = qty
			status['sl'] = (row.loc['close'] + (row.loc['close']*sl_percent))
			status['exit_time'] = None
			status['exit_price'] = None
			status['pnl'] = None 
			status['remark'] = None 
			status['target_price'] = abs(round((row.loc['close']) - (row.loc['close']*tg_percent_sell),2))
			trade_number = trade_number + 1 
			status['trade_number'] = trade_number			
			
#SELLING AN ALREADY 'BUY' STOCK
		if  (status['traded'] is 'YES') and (status['buy_sell'] is 'BUY'):
			#diff = round(row.loc['high'] - day_high,2)
			if row.loc['high'] >= status['target_price']:
				print(" Target hit - Placing the sell order ",index)
				status['exit_time'] = row.loc['time']
				status['exit_price'] = status['target_price']
				status['pnl'] = round(status['target_price'] - status['entry_price'],2)
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
				#print(final)

				continue
				#pdb.set_trace()

			if row.loc['low'] <= status['sl']:
				pprint(f'Stop loss hit for {name} at {index}')
				status['exit_time'] = row.loc['time']
				status['exit_price'] = status['sl']
				status['pnl'] = round(status['sl'] - status['entry_price'],2)
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
				#print(final)
				continue
#SELLING AN ALREADY 'SELL' SHARE 
		if  (status['traded'] is 'YES') and (status['buy_sell'] is 'SELL'):
			if row.loc['low'] <= status['target_price']:
				print(" Target hit - Placing the sell order ",index)
				status['exit_time'] = row.loc['time']
				status['exit_price'] = status['target_price']
				status['pnl'] = abs(status['target_price'] - status['entry_price'])
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
				#print(final)

				continue

			if row.loc['high'] >= status['sl']:
				pprint(f'Stop loss hit for {name} at {index}')
				status['exit_time'] = row.loc['time']
				status['exit_price'] = status['sl']
				status['pnl'] = status['entry_price'] - status['sl']
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


final_df = pd.DataFrame.from_dict(final, orient='columns')
final_df.to_csv("final.csv") 
pprint(final_df)

