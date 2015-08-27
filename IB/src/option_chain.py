'''
Created on Aug 1, 2015

@author: huhe
'''

from ib.ext.Contract import Contract
from ib.opt import ibConnection
import time
from pprint import pprint
import lib

class OptionChain(object):
    '''
    classdocs
    '''

    def __init__(self, ticker):
        '''
        Constructor
        '''
        self._snapshot = False
        
        self._price        = -1
        self._price_req_id = 999
        self._price_done   = False
        
        self._ticker = ticker
        self._wait = False
        self._con = None
        self._contracts = []
        self._expicys = []
        self._req_ids = []
        self._ticker_ids = []
        self._option_chain_dict = {}
        self._option_chain_sorted_dict = {}
        self._option_chain_sorted_dict['C'] = []
        self._option_chain_sorted_dict['P'] = []
        
    def  set_snapshot(self, snapshot):
        self._snapshot = snapshot
        
    def watcher(self, msg):
        #print '-> watcher: message type = ' + msg.typeName
        self.process_message(msg)
    
    def contract_details_handler(self, msg):
        #print 'contract_details_handler: ' + msg.typeName
        self._contracts.append(msg.contractDetails.m_summary)
    
    def contract_details_end_handler(self, msg):
        #print 'contract_details_end_handler: ' + msg.typeName
        self._wait = False
    
    def tick_price_hander(self, msg):
        #print 'tick_price_hander: ' + msg.typeName
        self.process_message(msg)
        
    def tick_size_handler(self, msg):
        #print 'tick_size_handler: ' + msg.typeName
        self.process_message(msg)
        
    def tick_string_handler(self, msg):
        #print 'tick_string_handler: ' + msg.typeName
        self.process_message(msg)
        
    def tick_option_computation_handler(self, msg):
        #print '===================================>>>>>>>>>>>>>>> tick_option_computation_handler: ' + msg.typeName
        self.process_message(msg)
        
    def tick_generic_handler(self, msg):
        #print 'tick_generic_handler: ' + msg.typeName
        self.process_message(msg)
        
    def tick_snapshot_end_handler(self, msg):
        #print 'tick_snapshot_end_handler: ' + msg.typeName
        self.process_message(msg)
        
    def print_message(self, msg):
        print ' '*4 , 
        for key, val in msg.items():
            print str(key) + " = " + str(val) + "; ", 
        print ''
        
    def process_message(self, msg):
        #self.print_message(msg)
        msg_type = msg.typeName
        msg_dict = self.convert_message(msg)
        ticker_id = msg_dict['tickerId'] if 'tickerId' in msg_dict.keys() else None
        field     = msg_dict['field'] if 'field' in msg_dict.keys() else None
        if msg_type == 'tickPrice':
            price = msg_dict['price']
            if field == 1:
                self._option_chain_dict[ticker_id]['bid'] = price
            elif field == 2:
                self._option_chain_dict[ticker_id]['ask'] = price
            elif field == 4:
                self._option_chain_dict[ticker_id]['last'] = price
            elif field == 6:
                self._option_chain_dict[ticker_id]['high'] = price
            elif field == 7:
                self._option_chain_dict[ticker_id]['low'] = price
            elif field == 9:
                self._option_chain_dict[ticker_id]['close'] = price
            elif field in [14]:
                pass
            else:
                print "ERROR: unknown field in type TickPrice: " + str(field)
                self.print_message(msg)
        elif msg_type == 'tickSize':
            size = msg_dict['size']
            if field == 0:
                self._option_chain_dict[ticker_id]['bid_size'] = size
            elif field == 3:
                self._option_chain_dict[ticker_id]['ask_size'] = size
            elif field == 5:
                self._option_chain_dict[ticker_id]['last_size'] = size
            elif field == 6:
                self._option_chain_dict[ticker_id]['high'] = size
            elif field == 7:
                self._option_chain_dict[ticker_id]['low'] = size
            elif field == 8:
                self._option_chain_dict[ticker_id]['volume'] = size
            elif field == 27:
                self._option_chain_dict[ticker_id]['option_call_open_interest'] = size
            elif field == 28:
                self._option_chain_dict[ticker_id]['option_put_open_interest'] = size
            else:
                print "ERROR: unknown field in type TickSize: " + str(field)
                self.print_message(msg)
        elif msg_type == 'tickString':
            tick_type = msg_dict['tickType']
            value = msg_dict['value']
            if tick_type == 45:
                self._option_chain_dict[ticker_id]['last_timestamp'] = value
            elif tick_type in [32, 33]:
                pass
            else:
                print "ERROR: unknown field in type TickString: " + str(field)
                self.print_message(msg)
        elif msg_type == 'tickGeneric':
            tick_type = msg_dict['tickType']
            value = msg_dict['value']
            if tick_type in [49]:
                pass
            else:
                print "ERROR: unknown field in type TickGeneric: " + str(field)
                self.print_message(msg)
        elif msg_type == 'tickSnapshotEnd':
            pass
            #print ticker_id, self._price_req_id, msg_dict['reqId']
            #if msg_dict['reqId'] == self._price_req_id:
            #    self._price_done = True
            #else:
            #    print "ERROR: unknown field in type tickSnapshotEnd: " + str(field)
            #    self.print_message(msg)
        elif msg_type == 'tickOptionComputation':
            if field == 13:
                self._option_chain_dict[ticker_id]['iv'] = msg_dict['impliedVol']
                self._option_chain_dict[ticker_id]['delta'] = msg_dict['delta']
                self._option_chain_dict[ticker_id]['option_price'] = msg_dict['optPrice']
                self._option_chain_dict[ticker_id]['dividend'] = msg_dict['pvDividend']
                self._option_chain_dict[ticker_id]['gamma'] = msg_dict['gamma']
                self._option_chain_dict[ticker_id]['vega'] = msg_dict['vega']
                self._option_chain_dict[ticker_id]['theta'] = msg_dict['theta']
                self._option_chain_dict[ticker_id]['underline_price'] = msg_dict['undPrice']
            elif field in [10, 11, 12]:
                pass
            else:
                print "ERROR: unknown field in type TickOptionComputation: " + str(field)
                self.print_message(msg)
        elif msg_type in ['error', 'managedAccounts', 'nextValidId', 'connectionClosed']:
            pass
            #print "INFO: message type = error"
            #self.print_message(msg)
        else:
            print "INFO: unprocessed type: " + msg_type
            self.print_message(msg)
        if ticker_id and ticker_id >= 1:
            if ticker_id in self._ticker_ids:
                #print 'removing ', ticker_id, ' from ', self._ticker_ids
                self._ticker_ids.remove(ticker_id)
        
    def convert_message(self, msg):
        msg_dict = {}
        for key, val in msg.items(): 
            msg_dict[key] = val
        return msg_dict
    
    def connect(self):
        self._con = ibConnection()
        self._con.registerAll(self.watcher)
        self._con.unregister(self.watcher, 'ContractDetails', 'ContractDetailsEnd', 'TickPrice', 'TickSize', 'TickString', 'TickOptionComputation', 'TickGeneric')
        self._con.register(self.contract_details_handler, 'ContractDetails')
        self._con.register(self.contract_details_end_handler, 'ContractDetailsEnd')
        self._con.register(self.tick_price_hander, 'TickPrice')
        self._con.register(self.tick_size_handler, 'TickSize')
        self._con.register(self.tick_string_handler, 'TickString')
        self._con.register(self.tick_option_computation_handler, 'TickOptionComputation')
        self._con.register(self.tick_generic_handler, 'TickGeneric')
        self._con.register(self.tick_snapshot_end_handler, 'TickSnapshotEnd')
        self._con.connect()
        
    def disconnect(self):
        self._con.disconnect()
        self._con.close()
            
    def download_contracts(self):
        contract = Contract()
        contract.m_exchange     = "SMART"
        contract.m_secType      = "OPT"
        contract.m_currency     = "USD"
        contract.m_symbol       = self._ticker
        self._con.reqContractDetails(1, contract)
        self._wait = True  
        i = 0
        while self._wait and i < 90:
            i += 1 ; print i,
            time.sleep(1)   
        print ''   
            
    def cancel_market_data(self):
        while len(self._ticker_ids) > 0:
            time.sleep(1)
            #print '*'*10, self._ticker_ids
        time.sleep(15)
        while len(self._req_ids) > 0:
            rmId = self._req_ids.pop(0)
            #print '-'*5 + "rmId: " + str(rmId)
            self._con.cancelMktData(rmId)  
            
    def reduce_contracts(self):
        if self._price <= 0: return
        new_contracts = []
        contract_dict = {}
        for expiry in self._expicys:
            contract_dict[expiry] = {}
            contract_dict[expiry]['P'] = []
            contract_dict[expiry]['C'] = []
        for c in self._contracts:
            if c.m_expiry in self._expicys:
                #print c.m_expiry + ' ' + str(c.m_strike) + ' ' + c.m_right
                contract_dict[c.m_expiry][c.m_right].append(c.m_strike)
        for expiry in contract_dict.keys():
            new_put_strike_list  = self.reduce_strike(contract_dict[expiry]['P'], expiry, True)
            new_contracts += self.find_reduced_contracts(expiry, new_put_strike_list, 'P')
            new_call_strike_list = self.reduce_strike(contract_dict[expiry]['C'], expiry, False)
            new_contracts += self.find_reduced_contracts(expiry, new_call_strike_list, 'C')
            strike_len = len(new_put_strike_list)
            print strike_len, '[', new_put_strike_list[0], ' - ', new_put_strike_list[strike_len-1], ']'
            strike_len = len(new_call_strike_list)
            print strike_len, '[', new_call_strike_list[0], ' - ', new_call_strike_list[strike_len-1], ']'
            
        self._contracts = new_contracts
            
    def find_reduced_contracts(self, expiry, strike_list, right):
        contract_list = []
        for c in self._contracts:
            if c.m_expiry in self._expicys:
                #print c.m_expiry + ' ' + str(c.m_strike) + ' ' + c.m_right
                if c.m_expiry == expiry and c.m_right == right and c.m_strike in strike_list:
                    contract_list.append(c)
        return contract_list
            
    def reduce_strike(self, strike_list, expiry, is_put):   
        current_date_str = lib.create_current_date_string()
        days_to_expiry = lib.calculate_days_difference(expiry, current_date_str)
        strike_list  = sorted(strike_list)
        otm_rate = 0
        itm_rate = 0
        if self._price <= 25:
            otm_rate = 0.50
            itm_rate = 0.20
        elif self._price <= 50:
            otm_rate = 0.40
            itm_rate = 0.15
        elif self._price <= 100:
            otm_rate = 0.36
            itm_rate = 0.10
        elif self._price <= 150:
            otm_rate = 0.33
            itm_rate = 0.10
        elif self._price <= 200:
            otm_rate = 0.28
            itm_rate = 0.10
        else:
            otm_rate = 0.25
            itm_rate = 0.10
        if is_put:
            otm_strike = self._price * (1 - otm_rate)
            itm_strike = self._price * (1 + itm_rate)
            strike_list = [x for x in strike_list if (x >= otm_strike and x <= itm_strike and int(x) == x)]
            return strike_list
        else:
            otm_strike = self._price * (1 + otm_rate)
            itm_strike = self._price * (1 - itm_rate)
            strike_list = [x for x in strike_list if (x >= itm_strike and x <= otm_strike and int(x) == x)]
            return strike_list
        
    def download_price(self):
        contract = Contract()
        contract.m_exchange = "SMART"
        contract.m_secType  = "STK"
        contract.m_currency = "USD"
        contract.m_strike   = 0.0
        contract.m_symbol   = self._ticker
        stock_req_id = self._price_req_id
        self._option_chain_dict[stock_req_id] = {}
        self._con.reqMktData(stock_req_id, contract, None, True)
        cnt = 30
        while cnt > 0:
            if 'last' in self._option_chain_dict[stock_req_id].keys() and self._option_chain_dict[stock_req_id]['last'] > 0:
                self._price = self._option_chain_dict[stock_req_id]['last']
                self._con.cancelMktData(self._price_req_id)  
                return self._price
            elif 'close' in self._option_chain_dict[stock_req_id].keys() and self._option_chain_dict[stock_req_id]['close'] > 0:
                self._price = self._option_chain_dict[stock_req_id]['close']
                self._con.cancelMktData(self._price_req_id)
                return self._price
            else:
                cnt -= 1
                time.sleep(1)
                
                
    def get_price(self):
        return self._price
    
        
    def download_option_chain(self):
        reqId = 0
        self._option_chain_dict = {}
        for c in self._contracts:
            if c.m_expiry in self._expicys:
                #print c.m_expiry + ' ' + str(c.m_strike) + ' ' + c.m_right
                reqId += 1
                #print '='*5 + "reqId: " + str(reqId)
                self._option_chain_dict[reqId] = {}
                self._option_chain_dict[reqId]['expiry'] = c.m_expiry
                self._option_chain_dict[reqId]['strike'] = c.m_strike
                self._option_chain_dict[reqId]['right']  = c.m_right
                if self._snapshot:
                    self._con.reqMktData(reqId, c, None, True)
                else:
                    self._con.reqMktData(reqId, c, '100,101,104,106,456', False)
                    self._req_ids.append(reqId)
                    self._ticker_ids.append(reqId)
                    if len(self._req_ids) == 100: 
                        self.cancel_market_data()
        if self._snapshot:
            pass
        else:
            if len(self._req_ids) > 0:
                self.cancel_market_data()
        time.sleep(5)
        
            
    def sort_option_chain(self):
        option_chain_dict_tmp = {}
        option_chain_dict_tmp['C'] = {}
        option_chain_dict_tmp['P'] = {}
        for option_chain in self._option_chain_dict.values():
            expiry = option_chain['expiry']
            right  = option_chain['right']
            strike = option_chain['strike']
            strike_str = str(strike).zfill(7)
            contract_str = ''.join([expiry, right, strike_str])
            option_chain_dict_tmp[right][contract_str] = option_chain
        self._option_chain_sorted_dict['C'] = self.sorted_option_chain_by_right(option_chain_dict_tmp['C'])
        self._option_chain_sorted_dict['P'] = self.sorted_option_chain_by_right(option_chain_dict_tmp['P'])
        
    # input:  ticker = 'CSCO'; expiry = '20150821'
    # output: option chain data dictionary
    def download(self, expirys=None):
        self._expicys = expirys
        self.connect()
        self.download_price()
        print "underline price: ", self._price
        self.download_contracts()
        #self.debug_contracts()
        self.reduce_contracts()
        #self.debug_contracts()
        
        self.download_option_chain()
        self.disconnect()
        #pprint(self._option_chain_dict)
        self.sort_option_chain()
        #self.debug_sorted_option_chain()
        
    
    def debug_sorted_option_chain(self):
        self.debug_sorted_option_chain_by_right('C')
        self.debug_sorted_option_chain_by_right('P')
        
    def debug_sorted_option_chain_by_right(self, right):
        print ''
        for option_chain in self._option_chain_sorted_dict[right]:
            pprint(option_chain)
        print ''
        
    @staticmethod
    def sorted_option_chain_by_right(option_chain):
        sorted_data_chain = []
        for contract_str in sorted(option_chain.keys()):
            #print contract_str
            sorted_data_chain.append(option_chain[contract_str])
        return sorted_data_chain
    
    def debug_contracts(self):
        for c in self._contracts:
            if c.m_expiry in self._expicys:
                print c.m_expiry + ' ' + str(c.m_strike) + ' ' + c.m_right
    
    
if __name__ == '__main__':
    ticker = 'SPY'
    expiry = '20150918'
    option_chain = OptionChain(ticker)
    option_chain.download([expiry])
    
    #option_chain.debug_contracts()
    
    
        
        
        
        