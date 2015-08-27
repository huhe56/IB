'''
Created on Aug 23, 2015

@author: huhe
'''

from ib.ext.Contract import Contract
from ib.opt import ibConnection
import time
from pprint import pprint

class Stock(object):
    '''
    classdocs
    '''

    def __init__(self, ticker):
        '''
        Constructor
        '''
        self._snapshot = True
        self._market_data = 1
        self._req_id = 999
        
        self._ticker = ticker
        self._con = None
        
        self._close_price = -1
        self._last_price  = -1
        self._price = -1
        
    def  set_snapshot(self, snapshot):
        self._snapshot = snapshot
        
    def watcher(self, msg):
        #print '-> watcher: message type = ' + msg.typeName
        self.process_message(msg)
    
    def tick_price_hander(self, msg):
        #print 'tick_price_hander: ' + msg.typeName
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
        field     = msg_dict['field'] if 'field' in msg_dict.keys() else None
        if msg_type == 'tickPrice':
            price = msg_dict['price']
            if field == 4:
                self._last_price = price
            elif field == 9:
                self._close_price = price
            else:
                pass
                #print "ERROR: unknown field in type TickPrice: " + str(field)
                #self.print_message(msg)
        elif msg_type in ['error', 'managedAccounts', 'nextValidId', 'connectionClosed']:
            pass
            #print "INFO: message type = error"
            #self.print_message(msg)
        else:
            print "INFO: unprocessed type: " + msg_type
            self.print_message(msg)
        
    def convert_message(self, msg):
        msg_dict = {}
        for key, val in msg.items(): 
            msg_dict[key] = val
        return msg_dict
    
    def connect(self):
        self._con = ibConnection()
        self._con.registerAll(self.watcher)
        self._con.unregister(self.watcher, 'ContractDetails', 'ContractDetailsEnd', 'TickPrice', 'TickSize', 'TickString', 'TickGeneric')
        self._con.register(self.tick_price_hander, 'TickPrice')
        self._con.register(self.tick_snapshot_end_handler, 'TickSnapshotEnd')
        self._con.connect()
        
    def disconnect(self):
        self._con.disconnect()
        self._con.close()
            
    def download_price(self):
        contract = Contract()
        contract.m_exchange = "SMART"
        contract.m_secType  = "STK"
        contract.m_currency = "USD"
        contract.m_strike   = 0.0
        contract.m_symbol   = self._ticker
        self._con.reqMktData(self._req_id, contract, None, self._snapshot)
        cnt = 30
        while cnt > 0:
            if self._close_price != -1 or self._last_price != -1:
                if self._last_price != -1:
                    self._price = self._last_price
                elif self._close_price != -1:
                    self._price = self._close_price
                self._con.cancelMktData(self._req_id)  
                return self._price
            cnt -= 1
            time.sleep(1)
            
    # input:  ticker = 'CSCO'; expiry = '20150821'
    # output: option chain data dictionary
    def download(self, expirys=None):
        self.connect()
        self.download_price()
        self.disconnect()
    
    
if __name__ == '__main__':
    ticker = 'SPY'
    stock = Stock(ticker)
    stock.download()
    print stock._price
    
    #option_chain.debug_contracts()
    
    
        
        
        
        