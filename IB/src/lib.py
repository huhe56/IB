'''
Created on Jan 16, 2015

@author: huhe
'''

from datetime import datetime

DEBUG = False

CURRENT_EXPIRY = '20151016'

MIN_OPEN_INTEREST           = 500

DELTA_1SD                   = 0.15
DELTA_VERTICAL_SPREAD       = 0.30

# for short vertical spread
MIN_ROC_PER_DAY         = 0.011
MIN_CREDIT_SPREAD_RATIO = 0.330
# for long vertical spread
MAX_DEBIT_PER_DAY = 0.011
MAX_DEBIT_RATE    = 0.500

VERTICAL_SPREAD_TABLE_HEADER_FORMAT_STRING = "%7s [ %6s ] %5s - %7s [ %6s ] %5s (%6s,%6s = %4s, %3s ) = %2s [ %6s ] ---- [ %6s ] %7s = %6s %6s --- [ %2s ] %5s - %7s"
VERTICAL_SPREAD_TABLE_HEADER_LIST      = ["Strike1", "Price", "Delta", "Strike2", "Price", "Delta", "Ask", "Bid", "Sprd", "S%", "DS", "DSP", "Credit", "Credit%", "ROC%", "POP%", "DTE", "ROC/D", "ROC/Y"]
LONG_VERTICAL_SPREAD_TABLE_HEADER_LIST = ["Strike1", "Price", "Delta", "Strike2", "Price", "Delta", "Ask", "Bid", "Sprd", "S%", "DS", "DSP", "Debit",  "Debit%",  "ROC%", "POP%", "DTE", "DOC/D", "DOC/Y"]

VERTICAL_SPREAD_TABLE_DATA_FORMAT_STRING   = "%7.2f [ %6.2f ] %5.2f - %7.2f [ %6.2f ] %5.2f (%6.2f,%6.2f = %4.2f, %3d ) = %2d [ %6.2f ] ---- [ %6.2f ] %7.2f = %6.2f  %5.2f --- [ %3d ] %5.2f - %7.2f"



def create_current_date_string():
    current = datetime.now()
    year =  current.strftime("%Y")
    month = current.strftime("%m")
    day =   current.strftime("%d")
    return ''.join([year, month, day])
    
    
def calculate_days_difference(date_str1, date_str2):
    date_diff = datetime.strptime(date_str1, "%Y%m%d") - datetime.strptime(date_str2, "%Y%m%d")
    days_to_expiry = date_diff.days
    return days_to_expiry


def calculate_mid_price(option_chain):
    return (option_chain['ask'] + option_chain['bid'])/2


def print_vertical_spread_header():
    print VERTICAL_SPREAD_TABLE_HEADER_FORMAT_STRING % tuple(VERTICAL_SPREAD_TABLE_HEADER_LIST)
    print ""
    
    
def print_long_vertical_spread_header():
    print VERTICAL_SPREAD_TABLE_HEADER_FORMAT_STRING % tuple(LONG_VERTICAL_SPREAD_TABLE_HEADER_LIST)
    print ""
    
def find_vertical_spread(underline_ticker, option_chain_data, days_to_expiry, is_put):
    found = False
    found_short_strike = False
    underline_price = option_chain_data[0]['underline_price']
    short_strike_option = find_vertical_spread_short_option(option_chain_data, is_put)
    if not short_strike_option: return None
    short_strike = short_strike_option['strike']
    tag = 'Put' if is_put else 'Call'
    print ''
    print ''
    print '-'*45, 'Short', underline_ticker, tag, 'Vertical Spread ; Underline Price:', str(int(underline_price*100)/100.0), '-'*45
    print ''
    option_chains = option_chain_data[::-1] if is_put else option_chain_data
    strike_len = len(option_chains)
    for idx1 in range(0, strike_len):
        option_chain1 = option_chains[idx1]
        strike1 = option_chain1['strike']
        if strike1 != short_strike and not found_short_strike: continue
        else: found_short_strike = True
        open_interest1 = option_chain1['option_put_open_interest'] if is_put else option_chain1['option_call_open_interest']
        if open_interest1 < MIN_OPEN_INTEREST: continue
        bid1 = option_chain1['bid']
        ask1 = option_chain1['ask']
        if bid1 < 0 or ask1 < 0: continue
        delta1 = option_chain1['delta']
        mid_price1 = (bid1 + ask1)/2
        for idx2 in range(idx1+1, strike_len):
            option_chain2 = option_chains[idx2]
            if is_put:
                if 'option_put_open_interest' not in option_chain2.keys(): continue
            else:
                if 'option_call_open_interest' not in option_chain2.keys(): continue
            open_interest2 = option_chain2['option_put_open_interest'] if is_put else option_chain2['option_call_open_interest']
            if open_interest2 < MIN_OPEN_INTEREST: continue
            bid2 = option_chain2['bid']
            ask2 = option_chain2['ask']
            if bid2 < 0 or ask2 < 0: continue
            mid_price2 = (bid2 + ask2)/2
            strike2 = option_chain2['strike']
            delta2 = option_chain2['delta']
            strike_distance = idx2 - idx1
            strike_diff = strike1 - strike2 if is_put else strike2 - strike1
            mid_price_diff = mid_price1 - mid_price2
            credit_rate = mid_price_diff / strike_diff
            roc = mid_price_diff / (strike_diff - mid_price_diff)
            roc_per_day = roc / days_to_expiry
            roc_per_year =  roc_per_day * 365
            pop = 100 - roc*100
            spread2 = ask2 - bid2
            spread_rate2 = 100 * spread2 / ((ask2 + bid2) / 2)
            if  roc_per_day > MIN_ROC_PER_DAY or credit_rate >= MIN_CREDIT_SPREAD_RATIO:
                if not found:
                    print_vertical_spread_header()
                    found = True
                data_list = [strike1, mid_price1, delta1, strike2, mid_price2, delta2, ask2, bid2, spread2, spread_rate2, strike_distance, strike_diff, mid_price_diff, credit_rate*100, roc*100, pop, days_to_expiry, roc_per_day*100, roc_per_year*100]
                print VERTICAL_SPREAD_TABLE_DATA_FORMAT_STRING % tuple(data_list)
                   
                   
def find_vertical_spread_long(underline_ticker, option_chain_data, days_to_expiry, is_put):
    underline_price = option_chain_data[0]['underline_price']
    tag = 'PUT' if is_put else 'CALL'
    print ''
    print ''
    print '-'*45, 'Long Vertical Spread: Underline:', underline_ticker,';', tag, 'Price:', str(underline_price), '-'*45
    print ''
    option_chains = option_chain_data[::-1] if is_put else option_chain_data
    strike_len = len(option_chains)
    for idx1 in range(0, strike_len-1):
        option_chain1 = option_chains[idx1]
        option_chain2 = option_chains[idx1+1] if is_put else option_chains[idx1-1]
        strike1 = option_chain1['strike']
        strike2 = option_chain2['strike']
        delta1  = option_chain1['delta']
        delta2  = option_chain2['delta']
        if underline_price < strike1 and underline_price > strike2:
            open_interest1 = option_chain1['option_put_open_interest'] if is_put else option_chain1['option_call_open_interest']
            open_interest2 = option_chain2['option_put_open_interest'] if is_put else option_chain2['option_call_open_interest']
            if open_interest1 < MIN_OPEN_INTEREST or open_interest2 < MIN_OPEN_INTEREST: break
            bid1 = option_chain1['bid']
            ask1 = option_chain1['ask']
            if bid1 < 0 or ask1 < 0: break
            mid_price1 = (bid1 + ask1)/2
            bid2 = option_chain2['bid']
            ask2 = option_chain2['ask']
            if bid2 < 0 or ask2 < 0: break
            mid_price2 = (bid2 + ask2)/2
            strike_distance = 1
            strike_diff = strike1 - strike2
            mid_price_diff = abs(mid_price1 - mid_price2)
            debit_rate = mid_price_diff/strike_diff
            debit_rate_per_day = debit_rate / days_to_expiry
            debit_rate_per_year = debit_rate_per_day * 365
            spread2 = ask2 - bid2
            spread_rate2 = 100 * spread2 / ((ask2 + bid2) / 2)
            #if debit_rate_per_day < MAX_DEBIT_PER_DAY:
            if mid_price_diff/strike_diff < MAX_DEBIT_RATE or debit_rate < MAX_DEBIT_RATE:
                print_long_vertical_spread_header()
                data_list = [strike1, mid_price1, delta1, strike2, mid_price2, delta2, ask2, bid2, spread2, spread_rate2, strike_distance, strike_diff, mid_price_diff, debit_rate*100, 0, 0, days_to_expiry, debit_rate_per_day*100, debit_rate_per_year*100]
                print VERTICAL_SPREAD_TABLE_DATA_FORMAT_STRING % tuple(data_list)
            print ''
            break
                 
'''
DS: distance of strike
DSP: distance of strike price
'''
   
def find_1sd_option(option_chain_data, is_put):
    return find_option_by_delta(option_chain_data, DELTA_1SD, is_put)


def find_vertical_spread_short_option(option_chain_data, is_put):
    return find_option_by_delta(option_chain_data, DELTA_VERTICAL_SPREAD, is_put)

         
def find_option_by_delta(option_chain_data, detla, is_put):
    option_chains = option_chain_data if is_put else option_chain_data[::-1]
    strike_len = len(option_chains)
    idx0 = 0
    delta0 = 0
    idx_1sd = 0
    for idx1 in range(0, strike_len):
        option_chain1 = option_chains[idx1]
        delta1 = option_chain1['delta']
        if abs(delta1) == detla:
            idx_1sd = idx1
        elif abs(delta1) > detla and abs(delta0) < detla:
            delta1_diff = abs(delta1) - detla
            delta0_diff = detla - abs(delta0)
            if delta1_diff <= delta0_diff:
                idx_1sd = idx1
            else:
                idx_1sd = idx0
        if idx_1sd > 0:
            option_chain1 = option_chains[idx_1sd]
            if is_put:
                if 'option_put_open_interest' not in option_chain1.keys(): return None
            else:
                if 'option_call_open_interest' not in option_chain1.keys(): return None
            open_interest1 = option_chain1['option_put_open_interest'] if is_put else option_chain1['option_call_open_interest']
            if open_interest1 < MIN_OPEN_INTEREST: return None
            bid1 = option_chain1['bid']
            ask1 = option_chain1['ask']
            if bid1 < 0 or ask1 < 0: return None
            return option_chain1
        else:
            idx0 = idx1
            delta0 = delta1
    return None
        
        
def find_strangle(underline_ticker, underline_price, option_chain_data_all, days_to_expiry):
    put_option_chain  = find_1sd_option(option_chain_data_all['P'], True)
    call_option_chain = find_1sd_option(option_chain_data_all['C'], False)
    if not put_option_chain and not call_option_chain: return None
    
    if underline_price <= 0:
        if put_option_chain and 'underline_price' in put_option_chain.keys():
            underline_price = put_option_chain['underline_price'] 
        elif call_option_chain and 'underline_price' in call_option_chain.keys():
            underline_price = call_option_chain['underline_price'] 
        else:
            return None
    
    strategy = None
    if put_option_chain and call_option_chain:
        strategy = 'Strangle'
    elif put_option_chain:
        strategy = "Naked Put"
    else:
        strategy = "Naked Call"
    print ''
    print ''
    print '-'*50, 'Short', underline_ticker, strategy,'; Underline Price: ', str(underline_price), '-'*50
    print ''
    
    put_delta, put_strike, put_mid_price, put_buying_power = 0, 0, 0, 0
    if put_option_chain:
        put_delta = put_option_chain['delta']
        put_strike = put_option_chain['strike']
        put_bid = put_option_chain['bid']
        put_ask = put_option_chain['ask']
        put_mid_price = (put_ask + put_bid)/2
        put_buying_power = calculate_naked_option_buying_power(underline_price, put_strike, put_mid_price, True)
        put_bid_ask_spread = put_ask - put_bid
        put_bid_ask_spread_rate = 100 * put_bid_ask_spread / put_mid_price 
        print "Put :  Credit = %6.2f;  Buying Power = %8.2f;  Delta = %6.2f;  Strike = %8.2f   ( Ask =%6.2f; Bid =%6.2f; Spread = %4.2f; Rate =%3d )" % tuple([put_mid_price,  put_buying_power,  put_delta,  put_strike, put_ask, put_bid, put_bid_ask_spread, put_bid_ask_spread_rate])
        
    call_delta, call_strike, call_mid_price, call_buying_power = 0, 0, 0, 0
    if call_option_chain:
        call_delta = call_option_chain['delta']
        call_strike = call_option_chain['strike']
        call_bid = call_option_chain['bid']
        call_ask = call_option_chain['ask']
        call_mid_price = (call_ask + call_bid)/2
        call_buying_power = calculate_naked_option_buying_power(underline_price, call_strike, call_mid_price, False)
        call_bid_ask_spread = call_ask - call_bid
        call_bid_ask_spread_rate = 100 * call_bid_ask_spread / call_mid_price
        print "Call:  Credit = %6.2f;  Buying Power = %8.2f;  Delta = %6.2f;  Strike = %8.2f   ( Ask =%6.2f; Bid =%6.2f; Spread = %4.2f; Rate =%3d )" % tuple([call_mid_price, call_buying_power, call_delta, call_strike, call_ask, call_bid, call_bid_ask_spread, call_bid_ask_spread_rate])
    
    total_credit = put_mid_price + call_mid_price
    credit_price_ratio = total_credit*100 / underline_price
    total_buying_power = put_buying_power if put_buying_power > call_buying_power else call_buying_power
    roc = total_credit*100/total_buying_power
    roc_per_day = roc/days_to_expiry
    roc_per_year = roc_per_day*365
    
    print "Total: Credit = %6.2f;  Buying Power = %8.2f" % tuple([total_credit, total_buying_power])
    print ""
    print "Days to Expiry:  %5d" % (days_to_expiry)
    print "Return on Price: %5d" % (credit_price_ratio*100) 
    print "Return on Capital:          %7.2f" % (roc*100),'%'
    print "Return on Capital per Day:  %7.2f" % (roc_per_day*100),'%'
    print "Return on Capital per Year: %7.2f" % (roc_per_year*100),'%'
    print "" 
    

def find_iron_condor(underline_ticker, option_chain_data_all, days_to_expiry):
    underline_price = option_chain_data_all['P'][0]['underline_price']
    strategy = 'Iron Condor'
    print ''
    print ''
    print '-'*50, 'Short', underline_ticker, strategy,'; Underline Price: ', str(int(underline_price*100)/100.0), '-'*50
    print ''
    find_iron_condor_spread(underline_ticker, option_chain_data_all['P'], days_to_expiry, True)
    find_iron_condor_spread(underline_ticker, option_chain_data_all['C'], days_to_expiry, False)
    

def find_iron_condor_spread(underline_ticker, option_chain_data, days_to_expiry, is_put):
    found = False
    #underline_price = option_chain_data[0]['underline_price']
    tag = 'PUT' if is_put else 'CALL'
    print ''
    print ''
    print '-'*60, tag, '-'*60
    print ''
    option_chain_1sd = find_1sd_option(option_chain_data, is_put)
    if not option_chain_1sd: return
    strike_1sd = option_chain_1sd['strike']
    ic_spreads = []
    option_chains = option_chain_data[::-1] if is_put else option_chain_data
    strike_len = len(option_chains)
    for idx1 in range(0, strike_len):
        option_chain1 = option_chains[idx1]
        strike1 = option_chain1['strike']
        if strike1 != strike_1sd: continue
        open_interest1 = option_chain1['option_put_open_interest'] if is_put else option_chain1['option_call_open_interest']
        if open_interest1 < MIN_OPEN_INTEREST: continue
        bid1 = option_chain1['bid']
        ask1 = option_chain1['ask']
        if bid1 < 0 or ask1 < 0: continue
        mid_price1 = (bid1 + ask1)/2
        delta1 = option_chain1['delta']
        print_cnt = 0
        for idx2 in range(idx1+1, strike_len):
            option_chain2 = option_chains[idx2]
            open_interest2 = option_chain2['option_put_open_interest'] if is_put else option_chain2['option_call_open_interest']
            if open_interest2 < MIN_OPEN_INTEREST: continue
            bid2 = option_chain2['bid']
            ask2 = option_chain2['ask']
            if bid2 < 0 or ask2 < 0: continue
            mid_price2 = (bid2 + ask2)/2
            strike2 = option_chain2['strike']
            delta2 = option_chain2['delta']
            strike_distance = idx2 - idx1
            strike_diff = strike1 - strike2 if is_put else strike2 - strike1
            mid_price_diff = mid_price1 - mid_price2
            credit_rate = mid_price_diff / strike_diff
            roc = mid_price_diff / (strike_diff - mid_price_diff)
            roc_per_day = roc / days_to_expiry
            roc_per_year =  roc_per_day * 365
            pop = 100 - roc*100
            spread2 = ask2 - bid2
            spread_rate2 = 100 * spread2 / ((ask2 + bid2) / 2)
            if  roc_per_day > MIN_ROC_PER_DAY/4:
                if not found:
                    print_vertical_spread_header()
                    found = True
                data_list = [strike1, mid_price1, delta1, strike2, mid_price2, delta2, ask2, bid2, spread2, spread_rate2, strike_distance, strike_diff, mid_price_diff, credit_rate*100, roc*100, pop, days_to_expiry, roc_per_day*100, roc_per_year*100]
                print VERTICAL_SPREAD_TABLE_DATA_FORMAT_STRING % tuple(data_list)
                ic_spread = {'strike1': strike1, 'strike2': strike2, 'mid_price_diff': mid_price_diff, 'roc_per_day': roc_per_day}
                ic_spreads.append(ic_spread)
                print_cnt += 1
                if print_cnt >= 2: break
    return ic_spreads


def find_atm_option(underline_price, option_chain_data, is_put):
    option_chains = option_chain_data if is_put else option_chain_data[::-1]
    strike_len = len(option_chains)
    for idx1 in range(0, strike_len):
        option_chain1 = option_chains[idx1]
        strike1 = option_chain1['strike']
        if is_put and underline_price > strike1: 
            continue
        elif not is_put and underline_price < strike1:
            continue
        open_interest1 = option_chain1['option_put_open_interest'] if is_put else option_chain1['option_call_open_interest']
        if open_interest1 >= MIN_OPEN_INTEREST:
            return option_chain1
        else:
            break
    return None


def find_option_by_strike(strike, option_chain, is_put):
    strike_len = len(option_chain)
    for idx1 in range(0, strike_len):
        option_chain1 = option_chain[idx1]
        strike1 = option_chain1['strike']
        if strike1 == strike:
            open_interest1 = option_chain1['option_put_open_interest'] if is_put else option_chain1['option_call_open_interest']
            if open_interest1 >= MIN_OPEN_INTEREST:
                return option_chain1
            else:
                return None
    

def find_straddle(underline_ticker, underline_price, option_chain_data_all, days_to_expiry):
    if underline_price <= 0:
        underline_price = option_chain_data_all['P'][0]['underline_price']
    put_option_chain  = find_atm_option(underline_price, option_chain_data_all['P'], True)
    if not put_option_chain: return None
    put_strike = put_option_chain['strike']
    call_option_chain = find_option_by_strike(put_strike, option_chain_data_all['C'], False)
    if not call_option_chain: return None
    
    strategy = 'Straddle'    
    print ''
    print ''
    print '-'*50, 'Short', underline_ticker, strategy,'; Underline Price: ', str(underline_price), '-'*50
    print ''
    
    put_delta, put_strike, put_mid_price, put_buying_power = 0, 0, 0, 0
    if put_option_chain:
        put_delta = put_option_chain['delta']
        put_strike = put_option_chain['strike']
        put_bid = put_option_chain['bid']
        put_ask = put_option_chain['ask']
        put_mid_price = (put_ask + put_bid)/2
        put_buying_power = calculate_naked_option_buying_power(underline_price, put_strike, put_mid_price, True)
        put_bid_ask_spread = put_ask - put_bid
        put_bid_ask_spread_rate = 100 * put_bid_ask_spread / put_mid_price 
        print "Put :  Credit = %6.2f;  Buying Power = %8.2f;  Delta = %6.2f;  Strike = %8.2f   ( Ask =%6.2f; Bid =%6.2f; Spread = %4.2f; Rate =%3d )" % tuple([put_mid_price,  put_buying_power,  put_delta,  put_strike, put_ask, put_bid, put_bid_ask_spread, put_bid_ask_spread_rate])
        
    call_delta, call_strike, call_mid_price, call_buying_power = 0, 0, 0, 0
    if call_option_chain:
        call_delta = call_option_chain['delta']
        call_strike = call_option_chain['strike']
        call_bid = call_option_chain['bid']
        call_ask = call_option_chain['ask']
        call_mid_price = (call_ask + call_bid)/2
        call_buying_power = calculate_naked_option_buying_power(underline_price, call_strike, call_mid_price, False)
        call_bid_ask_spread = call_ask - call_bid
        call_bid_ask_spread_rate = 100 * call_bid_ask_spread / call_mid_price
        print "Call:  Credit = %6.2f;  Buying Power = %8.2f;  Delta = %6.2f;  Strike = %8.2f   ( Ask =%6.2f; Bid =%6.2f; Spread = %4.2f; Rate =%3d )" % tuple([call_mid_price, call_buying_power, call_delta, call_strike, call_ask, call_bid, call_bid_ask_spread, call_bid_ask_spread_rate])
    
    total_credit = put_mid_price + call_mid_price
    credit_price_ratio = total_credit*100 / underline_price
    total_buying_power = put_buying_power if put_buying_power > call_buying_power else call_buying_power
    roc = total_credit*100/total_buying_power
    roc_per_day = roc/days_to_expiry
    roc_per_year = roc_per_day*365
    
    print "Total: Credit = %6.2f;  Buying Power = %8.2f" % tuple([total_credit, total_buying_power])
    print ""
    print "Days to Expiry:  %5d" % (days_to_expiry)
    print "Return on Price: %5d" % (credit_price_ratio*100) 
    print "Return on Capital:          %7.2f" % (roc*100),'%'
    print "Return on Capital per Day:  %7.2f" % (roc_per_day*100),'%'
    print "Return on Capital per Year: %7.2f" % (roc_per_year*100),'%'
    print "" 
    

def calculate_naked_option_buying_power(underline_price, strike_price, credit, is_put):
    bp1 = (0.2 * underline_price - abs(underline_price - strike_price) + credit) * 100 
    bp2 = (0.1 * strike_price + credit) * 100 if is_put else (0.1 * underline_price + credit) * 100 
    bp3 = 50 + credit * 100
    #print "bp1, 2, 3 = %5d, %5d, %5d" % tuple([bp1, bp2, bp3])
    bp = bp1 if bp1 >= bp2 else bp2 
    bp = bp if bp >= bp3 else bp3 
    return bp


