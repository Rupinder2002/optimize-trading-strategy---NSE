import pandas as pd 
import pdb



adx = [20,25,30]
h_rsi = [65,70,75,80,85]

all_combination = {}
comb_no = 1 


for adx_item in adx:
	for h_rsi_item in h_rsi:
		#print({'adx' : adx_item, 'h_rsi' : h_rsi_item})
		all_combination[comb_no] = {'adx' : adx_item, 'h_rsi' : h_rsi_item}
		comb_no = comb_no + 1 

data = pd.DataFrame(all_combination).T
data.to_excel("brute_force_combi.xlsx")