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
        
        if lib.DEBUG:
            put_option_chains = option_chain_data.put_data
            lib.find_vertical_spread_long(underline_ticker, put_option_chains, days_to_expiry, True)
            call_option_chains = option_chain_data.call_data
            lib.find_vertical_spread_long(underline_ticker, call_option_chains, days_to_expiry, False)
        else:
            option_chain = OptionChain(underline_ticker)
            option_chain.download([expiry])
            put_option_chains = option_chain._option_chain_sorted_dict['P']
            lib.find_vertical_spread_long(underline_ticker, put_option_chains, days_to_expiry, True)
            call_option_chains = option_chain._option_chain_sorted_dict['C']
            lib.find_vertical_spread_long(underline_ticker, call_option_chains, days_to_expiry, False)

            
    
    
    
    
