#!/Library/Frameworks/Python.framework/Versions/2.7/bin/python

'''
Created on Jan 16, 2015

@author: huhe
'''

'''
puts
expirations
calls
expiry
underlying_price
underlying_id
'''

import sys
import lib
from option_chain import OptionChain
from data import option_chain_data


if __name__ == '__main__':
    
    if len(sys.argv) not in [2, 3]:
        print sys.argv[0], " ticker ", "[expiry]"
        exit
    else:
        underline_ticker = sys.argv[1].upper()
        expiry = sys.argv[2] if len(sys.argv) == 3 else lib.CURRENT_EXPIRY
        current_date_str = lib.create_current_date_string()
        days_to_expiry = lib.calculate_days_difference(expiry, current_date_str)
        
        option_chain_data_all = {}
        if lib.DEBUG:
            option_chain_data_all['P'] =  option_chain_data.put_data
            option_chain_data_all['C'] =  option_chain_data.call_data
            lib.find_straddle(underline_ticker, option_chain_data_all, days_to_expiry) 
        else:
            option_chain = OptionChain(underline_ticker)
            option_chain.download([expiry])
            underline_price = option_chain.get_price()
            option_chain_data_all['P'] = option_chain._option_chain_sorted_dict['P']
            option_chain_data_all['C'] = option_chain._option_chain_sorted_dict['C']
            lib.find_straddle(underline_ticker, underline_price, option_chain_data_all, days_to_expiry)
        
        
        
        
        
            
    
    
    
    
