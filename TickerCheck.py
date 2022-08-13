# -*- coding: utf-8 -*-
"""
Created on Wed Sep  9 00:10:58 2020

@author: dougi
"""

import yfinance as yf
import os
import pygame as pg
from datetime import datetime
from yahoo_fin import stock_info as si

class MacroTrendTracker():   
    def __init__(self):
        pg.init()
        # Sampling constraints
        self.dwell = 5
        self.window = 12
        # self.open = "00:58"
        # self.close = "00:59"
        self.open = "07:00"
        self.close = "19:30"
        self.outputdir = os.path.join(os.getcwd(),'STK_INFO')
        
        # Main Functions
        # self.twilio_init()
        self.buildportfolio()
        self.metaloop()
    
    # def compareIndices(self):
    #     for sec in si.tickers_nasdaq():
    #         try: 
    #             p = 
    #             print('%s : %f' % (sec,si.get_live_price(sec)))
    #         except:
    #             print('Skipping %s' %sec)

    def checkopen(self):
        week = ('Mon','Tue','Wed','Thu','Fri')
        curr = datetime.now().strftime("%H:%M_%a").split('_')
        if curr[0] in self.open and (curr[1] in week):
            return True
        else: return False
    def checkclose(self):
        curr = datetime.now().strftime("%H:%M")
        if curr in self.close:
            return True
        else: return False       

    # def twilio_init(self):
    #     from twilio.rest import Client
    #     # Your Account Sid and Auth Token from twilio.com/console
    #     # DANGER! This is insecure. See http://twil.io/secure
    #     account_sid = 'AC3ba8411a8d4be94b8e55546de8fc5e39'
    #     auth_token = 'a6da1e645fdb17de3fca76413d400568'
    #     self.numbers = {'from': '+12674811584',
    #                     'to': '+18509903227'}
    #     self.client = Client(account_sid, auth_token)
    
    def generate_SMS(self):
        message = self.client.messages \
                        .create(
                         body="This message was sent from Doug in the basement using TWILIO on python.",
                         from_=self.numbers['from'],
                         to=self.numbers['to'],
                         )
        print(message.sid)
        
    def buildportfolio(self):
        ## Setup individual stock datastructure
        self.portfolio = {'HOLDING' : ['ICD','NIO','TSLA','GOOG','AMZN','KLR','SPG','HT','ICAGY','NNOX'],
                          'WATCHING' : ['LMCO','AAPL','TCY','BIDU'],
                          'INDICES': ['SPY','DIA','QQQ','VOO','VTI','IWM','IWL','IWC','SPGM','NDAQ']}
        self.resetportfolio()
        
    def resetportfolio(self):
        # {STOCKNAME:  ({summary statistics}, [prices], [price changes]}  
        self.fullday = {}
        for regime in ['HOLDING','INDICES']:
            for key in self.portfolio[regime]:
                self.fullday[key] = ({},[],[])
        # self.fullday = {key: ({},[],[]) for key in self.portfolio['HOLDING']}
        # self.fullday = {key: ({},[],[]) for key in self.portfolio['INDICES']}
        
    # def buildHistoricalData(self):
    #     ## Current set to run manually only
    #     import yfinance as yf
    #     for key in self.portfolio.keys():
    #             for security in self.portfolio[key]:                   
    #                 stock = yf.ticker.Ticker(security)
    #                 options = stock.options
    #                 hist = stock.history(period = 'max')
    #                 hist.to_csv('%s_info.csv' % security)
                    
    def windowing(self,data,new,movingSpan=30):
        #data.pop(0)
        data=data[movingSpan:]
        data.append(new)
        return data
    
    def scoring(self,summary,security):
        # Determine a score value for eventual training
        ## Need to determine, can this be a continuous variable?  Does it need to be binary?        
        score = (summary['%chng']*3  - (summary['Skew2']*4 + summary['Close']*3))/10
        if score > 1.25:
            outcome = 'GOOD'
        elif score > -0.25:
            outcome = 'NEUTRAL'
        else: outcome = 'BAD'
        return score, outcome
    
    def dailyEval(self,security):
        def median(data):
            LEN = len(data)
            temp = sorted(data)
            if LEN % 2:
                return temp[int((LEN+1)/2)]
            else: return sum(temp[int(LEN/2-1):int(LEN/2+1)])/2
        def mean(data):
            return sum(data)/len(data)
        def stdev(data,mu):
            variance = sum([(val-mu)**2 for val in data]) / len(data) # Using full population , no Bessel's correction
            return variance**0.5
        def datrange(data):
            return max(data)-min(data)
        def percChange(data):
            return 100*((data[-1]-data[0]) / data[0])
        def kurt(data,mu,std):
            N = len(data)
            if N > 3:
                partial = sum([(val-mu)**4 for val in data])/(std**4)
                return (N*(N+1)/((N-1)*(N-2)*(N-3))*partial) - (3*(N-1)**2)/((N-2)*(N-3))
            else: 
                return 0
        def mode(data):
            instanceLib = {}
            for val in data:
                if val in instanceLib.keys():
                    instanceLib[val] += 1
                else: instanceLib[val] = 1
            keys = list(instanceLib.keys())
            vals = list(instanceLib.values())
            return keys[vals.index(max(vals))]                
        def close_rat(data,RANGE):
            if RANGE:
                return (data[-1] - min(data))/RANGE
            else: return 0
            
        def Sk1(data,mu,std): #Person's skewness, mode formulation
            if std:
                return (mu - mode(data)) / std # + tiny constant to avoid infinities
            else: return 0
        def Sk2(data,mu,std,med):  # Pearson's skewness, median formlation
            if std:
                return 3*(mu - med) / std
            else: return 0    
        data = self.fullday[security][1][:] #Faster than list.copy()
        mu = mean(data)
        std = stdev(data,mu)
        med = median(data)
        RANGE = datrange(data)
        summary = {'mean':                    mu,
                   'median':                 med,
                   'stdev':                  std,
                   'max':               max(data),
                   'min':               min(data),
                   'range':                 RANGE,
                   'kurt':     kurt(data,mu,std),
                   'Skew1':     Sk1(data,mu,std),
                   'Skew2':     Sk2(data,mu,std,med),
                   'Close':     close_rat(data,RANGE),
                   '%chng':     percChange(data),}
        summary['score'],outcome =  self.scoring(summary,security)                
        return summary,outcome
   
    def report_out(self):
        today = datetime.now().strftime("%m-%d-%y")
        for regime in ['HOLDING','INDICES']:
            print('\n'+regime) 
            for security in self.portfolio[regime]:
                t=9.0
                evalDATA,outcome= self.dailyEval(security)
                scoring = [(key,evalDATA[key]) for key in evalDATA.keys()]
                print("Generating %s report - **%s** trading day " % (security,outcome))
                basestr = ''
                tick = 9/len(self.fullday[security][1]) # number of hours elapsed per data point
                for elem in scoring:
                    basestr += '%s: %f  ' %(elem[0],elem[1])
                print(basestr)
                if not os.path.exists(os.path.join(self.outputdir,regime,security)):
                    os.mkdir(os.path.join(self.outputdir,regime,security))
                with open(os.path.join(self.outputdir,regime,security,'%s_%s.csv' % (security,today)), 'w') as f:
                    f.write('%s - %s, %r\n' % (security,today,evalDATA))
                    ind = 0
                    for val in self.fullday[security][1]:
                        f.write('%f, %f, %f\n' % (t,val,self.fullday[security][2][ind]))
                        t+=tick;ind+=1                  
                        
    def metaloop(self):
        while 1:
            pg.time.wait(self.dwell*1000)  # Sets dwell in milliseconds
            t = datetime.now().strftime("%H:%M")
            #if t == self.open:
            isopen = self.checkopen()
            if isopen:                                                          
                print("Market Opened")
                self.mainloop()

    def getprice(self, regime):
        for security in self.portfolio[regime]:
            ticker_yahoo = yf.Ticker(security)
            data = ticker_yahoo.history()
            current = data['Close'].iloc[-1]
            self.fullday[security][1].append(current)
            try:
                self.fullday[security][2].append(self.fullday[security][1][-1] - self.fullday[security][1][-2]) 
            except: # For first entry of the day where no initial value exists
                self.fullday[security][2].append(0)
                #print('%s @ $%s, prices: %r' % (security,current,self.fullday[security][1]))
        
    def mainloop(self):
        loop=True
        count = 0 
        movingSpan = 30
        while loop:  
            os.chdir(os.path.join('C:\\Users\dougi','Documents'))
            pg.time.wait(self.dwell*1000)  # Sets dwell in milliseconds
            #for key in self.portfolio.keys():
            count += 1
            #if datetime.now().strftime("%H:%M") == self.close:
            if self.checkclose():                          
                loop = False
                self.report_out()
                self.resetportfolio()
                print("Market Closed")
            self.getprice('HOLDING')
            self.getprice('INDICES')
                
            # USe for periodic checking, will be useful after pattern analysis is refined
            # if count % self.window == 0:
            #     # print('Running %s check...' % self.window)
            #     # print(self.fullday[security][1])
            #     count = 0

example = MacroTrendTracker()



