#encoding=utf-8

import random
import re
import scipy.stats as sc
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from QuantLib import *
#%matplotlib inline
import seaborn as sns
sns.set(color_codes=True)
import data as dt



class BackTestData:
	def __init__(self,start,end,capital,costrate,fixcostrate,optioncost):		
		self.start=start
		self.end=end
		self.capital=capital
		self.capital_temp=capital
		self.costrate=costrate
		self.fixcostrate=fixcostrate
		self.optioncost_=optioncost[0]+optioncost[1]+optioncost[2]
		self.data=dt.sheetData(costrate)
		self.realizedVolatility=dt.realizedVolatility()
		self.winddata=dt.winddata()
		self.sheet=self.data.delta_sheet_[self.start:self.end]
		self.BackTestInterval=self.data.delta_sheet_[self.start:self.end].index
		self.underlying=pd.DataFrame(self.realizedVolatility.underlying,index=self.BackTestInterval)
		self.sheetData_temp()
		self.OptionPosition()
		self.main()
		self.YieldRate()
		self.MaxDrawback()
		self.MaxDrawback_num(30)
	def sheetData_temp(self):
		self.BT_delta_sheet_=pd.DataFrame(self.data.delta_sheet_,index=self.BackTestInterval).fillna(0)
		self.BT_gamma_sheet_=pd.DataFrame(self.data.gamma_sheet_,index=self.BackTestInterval).fillna(0)
		self.BT_vega_sheet_=pd.DataFrame(self.data.vega_sheet_,index=self.BackTestInterval).fillna(0)
		self.BT_theta_sheet_=pd.DataFrame(self.data.theta_sheet_,index=self.BackTestInterval).fillna(0)
		self.BT_impliedVolatility_sheet_=pd.DataFrame(self.data.impliedVolatility_sheet_,index=self.BackTestInterval).fillna(0)
		self.BT_theoryvalue_sheet_=pd.DataFrame(self.data.theoryvalue_sheet_,index=self.BackTestInterval).fillna(0)
		self.BT_mktprice_sheet_=pd.DataFrame(self.data.mktprice_sheet_,index=self.BackTestInterval).fillna(0)
		self.BT_ptmtradeday_sheet_=pd.DataFrame(self.data.ptmtradeday_sheet_,index=self.BackTestInterval).fillna(0)
		self.BT_MarginAccount_sheet_=pd.DataFrame(self.data.MarginAccount_sheet_,index=self.BackTestInterval).fillna(0)
		self.BT_InitialAccount_sheet_=pd.DataFrame(self.data.InitialAccount_sheet_,index=self.BackTestInterval).fillna(0)
		self.BT_ContractUnit_sheet_=pd.DataFrame(self.data.ContractUnit_sheet_,index=self.BackTestInterval).fillna(0)
		temp=self.realizedVolatility.underlying[self.start:self.end].loc[:,'spot']
		self.bench_=(temp/temp.iloc[0]-1)
		self.bench_=pd.DataFrame(np.matrix(self.bench_),index=['spot'],columns=self.bench_.index).T
	###策略头寸
	def symoption(self,option):
		if option[5]==u'购':
			temp=option[:5]+u'沽'+option[6:]
		else:
			temp=option[:5]+u'购'+option[6:]
		return temp
	def append(self,num,list_,position):
		if num+1>len(list_):
			list_.append(position)
		else:
			list_[-1]=position
		return list_
	
	def HighVol(self,number,date,option):
		if self.realizedVolatility.underlyingYieldRate_5.loc[date,'spot']>=self.realizedVolatility.underlyingYieldRate_10.loc[date,'spot'] and self.realizedVolatility.underlyingYieldRate_5.diff(1).loc[date,'spot']>=0:#call
			if option[5]==u'购':
				self.append(number,self.OptionPosition[option],20)
				#self.optioninhand.append(option)
				
			else:
				self.append(number,self.OptionPosition[option],-20)
				self.optioninhand.append(option)

		elif self.realizedVolatility.underlyingYieldRate_5.loc[date,'spot']>=self.realizedVolatility.underlyingYieldRate_10.loc[date,'spot'] and self.realizedVolatility.underlyingYieldRate_5.diff(1).loc[date,'spot']<0:#put
			if option[5]==u'购':
				self.append(number,self.OptionPosition[option],-20)
				self.optioninhand.append(option)
			else:
				self.append(number,self.OptionPosition[option],20)
				#self.optioninhand.append(option)
				
		elif self.realizedVolatility.underlyingYieldRate_5.loc[date,'spot']<self.realizedVolatility.underlyingYieldRate_10.loc[date,'spot'] and self.realizedVolatility.underlyingYieldRate_5.diff(1).loc[date,'spot']<0:#put
			if option[5]==u'购':
				self.append(number,self.OptionPosition[option],-20)
				self.optioninhand.append(option)
				
			else:
				self.append(number,self.OptionPosition[option],20)
				#self.optioninhand.append(option)
				
		elif self.realizedVolatility.underlyingYieldRate_5.loc[date,'spot']<self.realizedVolatility.underlyingYieldRate_10.loc[date,'spot'] and self.realizedVolatility.underlyingYieldRate_5.diff(1).loc[date,'spot']>=0:#call
			if option[5]==u'购':
				self.append(number,self.OptionPosition[option],20)
				#self.optioninhand.append(option)
				
			else:
				self.append(number,self.OptionPosition[option],-20)
				self.optioninhand.append(option)
	def stableVol(self,number,date,option):
		if self.realizedVolatility.fore_30.loc[:date,'fore']<=np.mean(self.realizedVolatility.underlyingYieldRate_30.loc[:date,'spot'].iloc[-5]):
			if option[5]==u'购':
				self.append(number,self.OptionPosition[option],20)
				#self.optioninhand.append(option)
			else:
				self.append(number,self.OptionPosition[option],-20)
				self.optioninhand.append(option)
		else:
			if option[5]==u'购':
				self.append(number,self.OptionPosition[option],-20)
				self.optioninhand.append(option)
			else:
				self.append(number,self.OptionPosition[option],20)
				#self.optioninhand.append(option)
	def HighVol_2(self,number,date,option):
		if option[5]==u'购':
			self.append(number,self.OptionPosition[option],40)
			self.append(number,self.OptionPosition[self.symoption(option)],20)
		else:
			self.append(number,self.OptionPosition[option],20)
			self.append(number,self.OptionPosition[self.symoption(option)],40)
	def stableVol_2(self,number,date,option):
		if option[5]==u'购':
			self.append(number,self.OptionPosition[option],-40)
			self.append(number,self.OptionPosition[self.symoption(option)],-20)
		else:
			self.append(number,self.OptionPosition[option],-20)
			self.append(number,self.OptionPosition[option],-40)

		
	'''
	def stableVol(self,number,date,option):
		if self.realizedVolatility.underlyingYieldRate_10.loc[date,'spot']>self.realizedVolatility.underlyingYieldRate_30.loc[date,'spot']:
			if option[5]==u'购':
				self.append(number,self.OptionPosition[option],0)
				#self.optioninhand.append(option)
			else:
				self.append(number,self.OptionPosition[option],-30)
				self.optioninhand.append(option)
		else:
			if option[5]==u'购':
				self.append(number,self.OptionPosition[option],-30)
				self.optioninhand.append(option)
			else:
				self.append(number,self.OptionPosition[option],0)
				#self.optioninhand.append(option)
	'''
	'''
	def stableVol(self,number,date,option):
		if self.realizedVolatility.fore.loc[date,'fore']>self.realizedVolatility.underlyingYieldRate_5.loc[date,'spot']:
			if option[5]==u'购':
				self.append(number,self.OptionPosition[option],0)
				#self.optioninhand.append(option)
				#print date,'stable','fore+'
			else:
				self.append(number,self.OptionPosition[option],-20)
				self.optioninhand.append(option)
				print date,'stable','fore+'
		else:
			if option[5]==u'购':
				self.append(number,self.OptionPosition[option],-20)
				self.optioninhand.append(option)
				print date,'stable','fore-'
			else:
				self.append(number,self.OptionPosition[option],0)
				#self.optioninhand.append(option)
				#print date,'stable','fore-'
	'''	
	'''	
	def OptionPosition(self):
		self.OptionPosition={}
		self.temp1_optioninhand=[]
		self.temp2_optioninhand=[]
		self.temp_exitoption=[]
		for i in self.data.option_names:
			self.OptionPosition[i]=[]

		#换仓时间为15个交易日
		period=15
		step=period
		for number,date in enumerate(self.BackTestInterval):
			_date=str(date)[:10]
			#latest_issue_date=self.data.option_startdate[self.data.option_startdate<=_date].iloc[-1]
			optionpool=self.data.delta_sheet_.loc[date].dropna().index
			self.optioninhand=[]
			if step==period:
				for option in self.data.option_names:
					#if option in set(self.data.options_in_startdate[latest_issue_date]+self.temp1_optioninhand+self.temp2_optioninhand)-set(self.temp_exitoption):
					if option in set(optionpool)-set(self.temp_exitoption):
						if abs(self.BT_delta_sheet_.loc[date,option])>0.8:
							self.append(number,self.OptionPosition[option],0)
							self.temp_exitoption.append(option)
						elif self.BT_ptmtradeday_sheet_.loc[date,option]<=1:	
							self.append(number,self.OptionPosition[option],0)	
							self.temp_exitoption.append(option)
					
						else:
							
							
							if self.realizedVolatility.VolForecast.loc[date,'vol_fore']>=self.realizedVolatility.realizedVol_day_10.loc[date,'spot']*1.1 or self.realizedVolatility.realizedVol_day_10.loc[date,'spot']>=0.45:#预测波动率上升 或 波动率处于高位
								self.HighVol(number,date,option)
							else:
								self.stableVol(number,date,option)
							#self.HighVol(number,date,option)
							
							
					else:
						self.append(number,self.OptionPosition[option],0)
				self.temp2_optioninhand=self.temp1_optioninhand
				self.temp1_optioninhand=self.optioninhand
				step=0
				
			else:
				for option in self.data.option_names:
					if option in set(optionpool)-set(self.temp_exitoption):
						if abs(self.BT_delta_sheet_.loc[date,option])>0.8:
							self.append(number,self.OptionPosition[option],0)
							self.temp_exitoption.append(option)
						elif self.BT_ptmtradeday_sheet_.loc[date,option]<=1:
							self.append(number,self.OptionPosition[option],0)	
							self.temp_exitoption.append(option)
						else:
							self.append(number,self.OptionPosition[option],self.OptionPosition[option][-1])
					else:
						self.append(number,self.OptionPosition[option],self.OptionPosition[option][-1])
				step=step+1
		'''
	def OptionPosition(self):
		self.OptionPosition={}
		self.temp_exitoption=[]
		for i in self.data.option_names:
			self.OptionPosition[i]=[]
		
		period=15
		step=period
		iii=0
		print self.realizedVolatility.VolForecast
		print self.realizedVolatility.realizedVol_10
		for number,date in enumerate(self.BackTestInterval):
			optionpool=self.data.delta_sheet_.loc[date].dropna().index
			self.optioninhand=[]
			if step==period:
				for option in self.data.option_names:
					if option in set(optionpool)-set(self.temp_exitoption):
						if abs(self.BT_delta_sheet_.loc[date,option])>0.8:
							self.append(number,self.OptionPosition[option],0)
							self.append(number,self.OptionPosition[self.symoption(option)],0)
							self.temp_exitoption.append(option)
							self.temp_exitoption.append(self.symoption(option))
						elif self.BT_ptmtradeday_sheet_.loc[date,option]<=1:
							self.append(number,self.OptionPosition[option],0)
							self.append(number,self.OptionPosition[self.symoption(option)],0)
							self.temp_exitoption.append(option)
							self.temp_exitoption.append(self.symoption(option))
						else:
							if self.realizedVolatility.VolForecast.loc[date,'vol_fore']>=self.realizedVolatility.realizedVol_10.loc[date,'spot'] or self.realizedVolatility.realizedVol_10.loc[date,'spot']>=0.5:#预测波动率上升 或 波动率处于高位
								self.HighVol_2(number,date,option)
							else:
								self.stableVol_2(number,date,option)
								iii+=1
								
					else:
						self.append(number,self.OptionPosition[option],0)
						self.append(number,self.OptionPosition[self.symoption(option)],0)
				step=0
			else:
				for option in self.data.option_names:
					if option in set(optionpool)-set(self.temp_exitoption):
						if abs(self.BT_delta_sheet_.loc[date,option])>0.8:
							self.append(number,self.OptionPosition[option],0)
							self.append(number,self.OptionPosition[self.symoption(option)],0)
							self.temp_exitoption.append(option)
							self.temp_exitoption.append(option)
						elif self.BT_ptmtradeday_sheet_.loc[date,option]<=1:
							self.append(number,self.OptionPosition[option],0)
							self.append(number,self.OptionPosition[self.symoption(option)],0)
							self.temp_exitoption.append(option)
							self.temp_exitoption.append(option)
						else:
							self.append(number,self.OptionPosition[option],self.OptionPosition[option][-1])
					else:
						self.append(number,self.OptionPosition[option],self.OptionPosition[option][-1])
				step=step+1
		print iii
				
		self.Position_=pd.DataFrame(self.OptionPosition,index=self.BackTestInterval,columns=self.data.option_names)
		self.PositionDiff_=self.Position_.diff(1)
		self.PositionDiff_.iloc[0]=self.Position_.iloc[0]
		self.OptionPosition_={}
		self.OptionPositionDiff_={}
		for j in self.data.option_names:
			self.OptionPosition_[j]=pd.DataFrame(self.OptionPosition[j],index=self.BackTestInterval,columns=[j])
			self.OptionPositionDiff_[j]=self.OptionPosition_[j].diff(1)
			self.OptionPositionDiff_[j].iloc[0]=self.OptionPosition_[j].iloc[0]
	
	def long(self,i,j,num1):
		#多头的期权费及手续费
		self.OptionTradeBuyVolume[j].append(self.OptionPositionDiff_[j].loc[i,j])
		self.OptionTradeSellVolume[j].append(0)
						
		self.premium[j].append(-self.OptionPositionDiff_[j].loc[i,j]*self.BT_mktprice_sheet_.loc[i,j]*self.BT_ContractUnit_sheet_.loc[i,j]-self.OptionPositionDiff_[j].loc[i,j]*(self.optioncost_))
		self.OptionCost[j].append(self.OptionPositionDiff_[j].loc[i,j]*(self.optioncost_))
		#-----------------------期权保证金每日变化------------------------------------
		if num1>=1:
			if self.OptionPosition_[j].iloc[num1-1,0]>=0 and self.OptionPosition_[j].loc[i,j]>0:
				self.OptionMarginAccount[j].append(0)
			elif self.OptionPosition_[j].iloc[num1-1,0]<0 and self.OptionPosition_[j].loc[i,j]>=0:
				self.OptionMarginAccount[j].append(0-self.OptionPosition_[j].iloc[num1-1,0]*abs(self.BT_MarginAccount_sheet_[j].iloc[num1-1]))
			else:
				self.OptionMarginAccount[j].append(self.OptionPosition_[j].loc[i,j]*abs(self.BT_MarginAccount_sheet_.loc[i,j])-self.OptionPosition_[j].iloc[num1-1,0]*abs(self.BT_MarginAccount_sheet_[j].iloc[num1-1]))
		else:
			self.OptionMarginAccount[j].append(0)

		#---------------------------------期权Greeks每日变化---------------------------------------------------
		if num1>=1:
			self.delta[j].append(self.BT_delta_sheet_.loc[i,j]*self.OptionPosition_[j].loc[i,j]*self.BT_ContractUnit_sheet_.loc[i,j]-self.BT_delta_sheet_[j].iloc[num1-1]*self.OptionPosition_[j].iloc[num1-1,0]*self.BT_ContractUnit_sheet_[j].iloc[num1-1])
			self.gamma[j].append(self.BT_gamma_sheet_.loc[i,j]*self.OptionPosition_[j].loc[i,j]*self.BT_ContractUnit_sheet_.loc[i,j]-self.BT_gamma_sheet_[j].iloc[num1-1]*self.OptionPosition_[j].iloc[num1-1,0]*self.BT_ContractUnit_sheet_[j].iloc[num1-1])
			self.vega[j].append(self.BT_vega_sheet_.loc[i,j]*self.OptionPosition_[j].loc[i,j]*self.BT_ContractUnit_sheet_.loc[i,j]-self.BT_vega_sheet_[j].iloc[num1-1]*self.OptionPosition_[j].iloc[num1-1,0]*self.BT_ContractUnit_sheet_[j].iloc[num1-1])
			self.theta[j].append(self.BT_theta_sheet_.loc[i,j]*self.OptionPosition_[j].loc[i,j]*self.BT_ContractUnit_sheet_.loc[i,j]-self.BT_theta_sheet_[j].iloc[num1-1]*self.OptionPosition_[j].iloc[num1-1,0]*self.BT_ContractUnit_sheet_[j].iloc[num1-1])

		else:
		
			self.delta[j].append(self.BT_delta_sheet_.loc[i,j]*self.OptionPosition_[j].loc[i,j]*self.BT_ContractUnit_sheet_.loc[i,j])
			self.gamma[j].append(self.BT_gamma_sheet_.loc[i,j]*self.OptionPosition_[j].loc[i,j]*self.BT_ContractUnit_sheet_.loc[i,j])
			self.vega[j].append(self.BT_vega_sheet_.loc[i,j]*self.OptionPosition_[j].loc[i,j]*self.BT_ContractUnit_sheet_.loc[i,j])
			self.theta[j].append(self.BT_theta_sheet_.loc[i,j]*self.OptionPosition_[j].loc[i,j]*self.BT_ContractUnit_sheet_.loc[i,j])
		self.Trade_delta[j].append(self.BT_delta_sheet_.loc[i,j]*self.OptionPositionDiff_[j].loc[i,j]*self.BT_ContractUnit_sheet_.loc[i,j])
		self.Trade_gamma[j].append(self.BT_gamma_sheet_.loc[i,j]*self.OptionPositionDiff_[j].loc[i,j]*self.BT_ContractUnit_sheet_.loc[i,j])
		self.Trade_vega[j].append(self.BT_vega_sheet_.loc[i,j]*self.OptionPositionDiff_[j].loc[i,j]*self.BT_ContractUnit_sheet_.loc[i,j])
		self.Trade_theta[j].append(self.BT_theta_sheet_.loc[i,j]*self.OptionPositionDiff_[j].loc[i,j]*self.BT_ContractUnit_sheet_.loc[i,j])


	def longcall(self,i,j,num1):
		ETF_temp=self.OptionPositionDiff_[j].loc[i,j]*self.BT_delta_sheet_.loc[i,j]*self.BT_ContractUnit_sheet_.loc[i,j]
		if num1>=1:
			if self.ETFInHand[j][-1]>0 and self.ETFInHand[j][-1]-ETF_temp>0:
				self.ETFInHand[j].append(self.ETFInHand[j][-1]-ETF_temp)
				self.ETFDebt[j].append(0)
									
			elif self.ETFInHand[j][-1]>0 and self.ETFInHand[j][-1]-ETF_temp<0:
				self.ETFInHand[j].append(0)
				self.ETFDebt[j].append(self.ETFInHand[j][-1]-ETF_temp)
									
			else:
				self.ETFInHand[j].append(0)
				self.ETFDebt[j].append(0-ETF_temp)
									
		else:
			self.ETFInHand[j].append(0)
			self.ETFDebt[j].append(0-ETF_temp)
			#-----------------------------------------------------------------------------------------------------
			#--------------------------------所持期权的价值------------------------------------------------
		if j[-1]=='A':
			strike=float(j[-6:-1])
		else:
        		strike=float(j[-4:])
		if num1>=1:
			self.OptionValue[j].append(max(self.underlying.loc[i,'spot']-strike,0)*self.OptionPosition_[j].loc[i,j]*self.BT_ContractUnit_sheet_.loc[i,j]-max(self.underlying.iloc[num1-1,0]-strike,0)*self.OptionPosition_[j].iloc[num1-1,0]*self.BT_ContractUnit_sheet_[j].iloc[num1-1])
		else:
			self.OptionValue[j].append(max(self.underlying.loc[i,'spot']-strike,0)*self.OptionPosition_[j].loc[i,j]*self.BT_ContractUnit_sheet_.loc[i,j])


	def longput(self,i,j,num1):
		ETF_temp=self.OptionPositionDiff_[j].loc[i,j]*self.BT_delta_sheet_.loc[i,j]*self.BT_ContractUnit_sheet_.loc[i,j]
		if num1>=1:
			if self.ETFInHand[j][-1]>0 and self.ETFInHand[j][-1]-ETF_temp>0:
				self.ETFInHand[j].append(self.ETFInHand[j][-1]-ETF_temp)
				self.ETFDebt[j].append(0)
									
			else:
				self.ETFInHand[j].append(self.ETFInHand[j][-1]-ETF_temp)
				self.ETFDebt[j].append(self.ETFDebt[j][-1])
									
		else:
			self.ETFInHand[j].append(0-ETF_temp)
			self.ETFDebt[j].append(0)
		#---------------------------------所持看跌期权价值------------------------------------------------------
		if j[-1]=='A':
			strike=float(j[-6:-1])
		else:
        		strike=float(j[-4:])
		if num1>=1:
			self.OptionValue[j].append(max(strike-self.underlying.loc[i,'spot'],0)*self.OptionPosition_[j].loc[i,j]*self.BT_ContractUnit_sheet_.loc[i,j]-max(strike-self.underlying.iloc[num1-1,0],0)*self.OptionPosition_[j].iloc[num1-1,0]*self.BT_ContractUnit_sheet_[j].iloc[num1-1])
		else:
			self.OptionValue[j].append(max(strike-self.underlying.loc[i,'spot'],0)*self.OptionPosition_[j].loc[i,j]*self.BT_ContractUnit_sheet_.loc[i,j])
	

	def short(self,i,j,num1):
		#空头的期权费及手续费
		self.OptionTradeBuyVolume[j].append(0)
		self.OptionTradeSellVolume[j].append(self.OptionPositionDiff_[j].loc[i,j])
		self.premium[j].append(-self.OptionPositionDiff_[j].loc[i,j]*self.BT_mktprice_sheet_.loc[i,j]*self.BT_ContractUnit_sheet_.loc[i,j]-abs(self.OptionPositionDiff_[j].loc[i,j]*(self.optioncost_)))
		self.OptionCost[j].append(abs(self.OptionPositionDiff_[j].loc[i,j]*(self.optioncost_)))
						#----------------------------------------期权保证金每日变化-------------------------------------
		if num1>=1:
			if self.OptionPosition_[j].iloc[num1-1,0]>0 and self.OptionPosition_[j].loc[i,j]>=0:
				self.OptionMarginAccount[j].append(0)
			elif self.OptionPosition_[j].iloc[num1-1,0]>=0 and self.OptionPosition_[j].loc[i,j]<0:
				self.OptionMarginAccount[j].append(self.OptionPosition_[j].loc[i,j]*abs(self.BT_MarginAccount_sheet_.loc[i,j])-0)
			else:
				self.OptionMarginAccount[j].append(self.OptionPosition_[j].loc[i,j]*abs(self.BT_MarginAccount_sheet_.loc[i,j])-self.OptionPosition_[j].iloc[num1-1,0]*abs(self.BT_MarginAccount_sheet_[j].iloc[num1-1]))
		else:
			self.OptionMarginAccount[j].append(self.OptionPosition_[j].loc[i,j]*abs(self.BT_MarginAccount_sheet_.loc[i,j])-0)


		#---------------------------------期权Greeks每日变化---------------------------------------------------
		if num1>=1:
			self.delta[j].append(self.BT_delta_sheet_.loc[i,j]*self.OptionPosition_[j].loc[i,j]*self.BT_ContractUnit_sheet_.loc[i,j]-self.BT_delta_sheet_[j].iloc[num1-1]*self.OptionPosition_[j].iloc[num1-1,0]*self.BT_ContractUnit_sheet_[j].iloc[num1-1])
			self.gamma[j].append(self.BT_gamma_sheet_.loc[i,j]*self.OptionPosition_[j].loc[i,j]*self.BT_ContractUnit_sheet_.loc[i,j]-self.BT_gamma_sheet_[j].iloc[num1-1]*self.OptionPosition_[j].iloc[num1-1,0]*self.BT_ContractUnit_sheet_[j].iloc[num1-1])
			self.vega[j].append(self.BT_vega_sheet_.loc[i,j]*self.OptionPosition_[j].loc[i,j]*self.BT_ContractUnit_sheet_.loc[i,j]-self.BT_vega_sheet_[j].iloc[num1-1]*self.OptionPosition_[j].iloc[num1-1,0]*self.BT_ContractUnit_sheet_[j].iloc[num1-1])
			self.theta[j].append(self.BT_theta_sheet_.loc[i,j]*self.OptionPosition_[j].loc[i,j]*self.BT_ContractUnit_sheet_.loc[i,j]-self.BT_theta_sheet_[j].iloc[num1-1]*self.OptionPosition_[j].iloc[num1-1,0]*self.BT_ContractUnit_sheet_[j].iloc[num1-1])
				
		else:
			self.delta[j].append(self.BT_delta_sheet_.loc[i,j]*self.OptionPosition_[j].loc[i,j]*self.BT_ContractUnit_sheet_.loc[i,j])
			self.gamma[j].append(self.BT_gamma_sheet_.loc[i,j]*self.OptionPosition_[j].loc[i,j]*self.BT_ContractUnit_sheet_.loc[i,j])
			self.vega[j].append(self.BT_vega_sheet_.loc[i,j]*self.OptionPosition_[j].loc[i,j]*self.BT_ContractUnit_sheet_.loc[i,j])
			self.theta[j].append(self.BT_theta_sheet_.loc[i,j]*self.OptionPosition_[j].loc[i,j]*self.BT_ContractUnit_sheet_.loc[i,j])
		self.Trade_delta[j].append(self.BT_delta_sheet_.loc[i,j]*self.OptionPositionDiff_[j].loc[i,j]*self.BT_ContractUnit_sheet_.loc[i,j])
		self.Trade_gamma[j].append(self.BT_gamma_sheet_.loc[i,j]*self.OptionPositionDiff_[j].loc[i,j]*self.BT_ContractUnit_sheet_.loc[i,j])
		self.Trade_vega[j].append(self.BT_vega_sheet_.loc[i,j]*self.OptionPositionDiff_[j].loc[i,j]*self.BT_ContractUnit_sheet_.loc[i,j])
		self.Trade_theta[j].append(self.BT_theta_sheet_.loc[i,j]*self.OptionPositionDiff_[j].loc[i,j]*self.BT_ContractUnit_sheet_.loc[i,j])


	def shortcall(self,i,j,num1):
		ETF_temp=self.OptionPositionDiff_[j].loc[i,j]*self.BT_delta_sheet_.loc[i,j]*self.BT_ContractUnit_sheet_.loc[i,j]
		if num1>=1:
			if self.ETFInHand[j][-1]>0 and self.ETFInHand[j][-1]-ETF_temp>0:
				self.ETFInHand[j].append(self.ETFInHand[j][-1]-ETF_temp)
				self.ETFDebt[j].append(0)
									
			else:
				self.ETFInHand[j].append(self.ETFInHand[j][-1]-ETF_temp)
				self.ETFDebt[j].append(self.ETFDebt[j][-1])
									
		else:
			self.ETFInHand[j].append(0-ETF_temp)
			self.ETFDebt[j].append(0)
		#-----------------------------------------------------------------------------------------------------
		#------------------------------------所持期权的价值------------------------------------------------
		if j[-1]=='A':
			strike=float(j[-6:-1])
		else:
        		strike=float(j[-4:])
		if num1>=1:
			self.OptionValue[j].append(max(self.underlying.loc[i,'spot']-strike,0)*self.OptionPosition_[j].loc[i,j]*self.BT_ContractUnit_sheet_.loc[i,j]-max(self.underlying.iloc[num1-1,0]-strike,0)*self.OptionPosition_[j].iloc[num1-1,0]*self.BT_ContractUnit_sheet_[j].iloc[num1-1])
		else:
			self.OptionValue[j].append(max(self.underlying.loc[i,'spot']-strike,0)*self.OptionPosition_[j].loc[i,j]*self.BT_ContractUnit_sheet_.loc[i,j])
		
	def shortput(self,i,j,num1):
		ETF_temp=self.OptionPositionDiff_[j].loc[i,j]*self.BT_delta_sheet_.loc[i,j]*self.BT_ContractUnit_sheet_.loc[i,j]
		if num1>=1:
			if self.ETFInHand[j][-1]>0 and self.ETFInHand[j][-1]-ETF_temp>0:
				self.ETFInHand[j].append(self.ETFInHand[j][-1]-ETF_temp)
				self.ETFDebt[j].append(0)
									
			elif self.ETFInHand[j][-1]>0 and self.ETFInHand[j][-1]-ETF_temp<0:
				self.ETFInHand[j].append(0)
				self.ETFDebt[j].append(self.ETFInHand[j][-1]-ETF_temp)
									
			else:
				self.ETFInHand[j].append(0)
				self.ETFDebt[j].append(0-ETF_temp)
									
		else:
			self.ETFInHand[j].append(0)
			self.ETFDebt[j].append(0-ETF_temp)
		#---------------------------------------------------------------------------------------------------
		#所持看跌期权价值
		if j[-1]=='A':
			strike=float(j[-6:-1])
		else:
        		strike=float(j[-4:])
		if num1>=1:
			self.OptionValue[j].append(max(strike-self.underlying.loc[i,'spot'],0)*self.OptionPosition_[j].loc[i,j]*self.BT_ContractUnit_sheet_.loc[i,j]-max(strike-self.underlying.iloc[num1-1,0],0)*self.OptionPosition_[j].iloc[num1-1,0]*self.BT_ContractUnit_sheet_[j].iloc[num1-1])
		else:
			self.OptionValue[j].append(max(strike-self.underlying.loc[i,'spot'],0)*self.OptionPosition_[j].loc[i,j]*self.BT_ContractUnit_sheet_.loc[i,j])
		


	def main(self):
		self.delta_sheet_diff_=self.BT_delta_sheet_.diff(1)
		self.delta_sheet_diff_.iloc[0]=self.BT_delta_sheet_.iloc[0]

		self.OptionMarginAccount={}
		self.OptionValue={}
		
		self.premium={}
		
		self.delta={}
		self.gamma={}
		self.vega={}
		self.theta={}

		self.Trade_delta={}
		self.Trade_gamma={}
		self.Trade_vega={}
		self.Trade_theta={}
		
		self.OptionTradeBuyVolume={}
		self.OptionTradeSellVolume={}
		self.OptionCost={}
		self.ETFInHand={}
		self.ETFDebt={}
		for i in self.data.option_names:
			
			self.OptionMarginAccount[i]=[]
			self.OptionValue[i]=[]
			
			self.premium[i]=[]
			
			self.delta[i]=[]
			self.gamma[i]=[]
			self.vega[i]=[]
			self.theta[i]=[]
			
			self.Trade_delta[i]=[]
			self.Trade_gamma[i]=[]
			self.Trade_vega[i]=[]
			self.Trade_theta[i]=[]
			
			self.OptionTradeBuyVolume[i]=[]
			self.OptionTradeSellVolume[i]=[]
			self.OptionCost[i]=[]
			self.ETFInHand[i]=[]
			self.ETFDebt[i]=[]
		for num1,i in enumerate(self.BackTestInterval):
			optionpool=pd.DataFrame(self.data.delta_sheet_,index=self.BackTestInterval).loc[i].dropna().index
			for j in self.data.option_names:
				if j in optionpool:
#---------------------------------------------------------------------多头--------------------------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
					if self.OptionPositionDiff_[j].loc[i,j]>0:
						self.long(i,j,num1)
						#------------------------------------------------------------------------------
						#多头看涨期权对冲 卖ETF对冲
						if self.BT_delta_sheet_.loc[i,j]>0:#看涨
							self.longcall(i,j,num1)
							#--------------------------------------------------------------------------------------						
						else:#self.BT_delta_sheet_.loc[i,j]<0看跌 
							self.longput(i,j,num1)
						
#---------------------------------------------------------------------空头------------------------------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
					elif self.OptionPositionDiff_[j].loc[i,j]<0:
						self.short(i,j,num1)
						#空头看涨期权对冲 买ETF对冲
						if self.BT_delta_sheet_.loc[i,j]>0:#看涨
							self.shortcall(i,j,num1)
							
							#--------------------------------------------------------------------------------------						
						else:#self.BT_delta_sheet_.loc[i,j]<0看跌 
							self.shortput(i,j,num1)
						
					else:#OptionPositionDiff_[j].loc[i,j]==0
						
						#期权费不变
						self.premium[j].append(0)


						if self.BT_delta_sheet_.loc[i,j]>0:
							#所持期权价值
							if j[-1]=='A':
								strike=float(j[-6:-1])
							else:
        							strike=float(j[-4:])
							if num1>=1:
								self.OptionValue[j].append(max(self.underlying.loc[i,'spot']-strike,0)*self.OptionPosition_[j].loc[i,j]*self.BT_ContractUnit_sheet_.loc[i,j]-max(self.underlying.iloc[num1-1,0]-strike,0)*self.OptionPosition_[j].iloc[num1-1,0]*self.BT_ContractUnit_sheet_[j].iloc[num1-1])
							else:
								self.OptionValue[j].append(max(self.underlying.loc[i,'spot']-strike,0)*self.OptionPosition_[j].loc[i,j]*self.BT_ContractUnit_sheet_.loc[i,j])
							
						else:
							#所持期权价值
							if j[-1]=='A':
								strike=float(j[-6:-1])
							else:
        							strike=float(j[-4:])
							if num1>=1:
								self.OptionValue[j].append(max(strike-self.underlying.loc[i,'spot'],0)*self.OptionPosition_[j].loc[i,j]*self.BT_ContractUnit_sheet_.loc[i,j]-max(strike-self.underlying.iloc[num1-1,0],0)*self.OptionPosition_[j].iloc[num1-1,0]*self.BT_ContractUnit_sheet_[j].iloc[num1-1])
							else:
								self.OptionValue[j].append(max(strike-self.underlying.loc[i,'spot'],0)*self.OptionPosition_[j].loc[i,j]*self.BT_ContractUnit_sheet_.loc[i,j])

						#期权保证金的变化
						if self.OptionPosition_[j].loc[i,j]>=0:
							self.OptionMarginAccount[j].append(0)
						else:
							if num1>=1:
								self.OptionMarginAccount[j].append(self.OptionPosition_[j].loc[i,j]*abs(self.BT_MarginAccount_sheet_.loc[i,j])-self.OptionPosition_[j].iloc[num1-1,0]*abs(self.BT_MarginAccount_sheet_[j].iloc[num1-1]))
							else:
								self.OptionMarginAccount[j].append(0)
						
						#
						if num1>=1:
							self.ETFInHand[j].append(self.ETFInHand[j][-1])
							self.ETFDebt[j].append(self.ETFDebt[j][-1])
						else:
							self.ETFInHand[j].append(0)
							self.ETFDebt[j].append(0)
							
						#---------------------------------期权Greeks每日变化---------------------------------------------------
						if num1>=1:
							self.delta[j].append(self.BT_delta_sheet_.loc[i,j]*self.OptionPosition_[j].loc[i,j]*self.BT_ContractUnit_sheet_.loc[i,j]-self.BT_delta_sheet_[j].iloc[num1-1]*self.OptionPosition_[j].iloc[num1-1,0]*self.BT_ContractUnit_sheet_[j].iloc[num1-1])
							self.gamma[j].append(self.BT_gamma_sheet_.loc[i,j]*self.OptionPosition_[j].loc[i,j]*self.BT_ContractUnit_sheet_.loc[i,j]-self.BT_gamma_sheet_[j].iloc[num1-1]*self.OptionPosition_[j].iloc[num1-1,0]*self.BT_ContractUnit_sheet_[j].iloc[num1-1])
							self.vega[j].append(self.BT_vega_sheet_.loc[i,j]*self.OptionPosition_[j].loc[i,j]*self.BT_ContractUnit_sheet_.loc[i,j]-self.BT_vega_sheet_[j].iloc[num1-1]*self.OptionPosition_[j].iloc[num1-1,0]*self.BT_ContractUnit_sheet_[j].iloc[num1-1])
							self.theta[j].append(self.BT_theta_sheet_.loc[i,j]*self.OptionPosition_[j].loc[i,j]*self.BT_ContractUnit_sheet_.loc[i,j]-self.BT_theta_sheet_[j].iloc[num1-1]*self.OptionPosition_[j].iloc[num1-1,0]*self.BT_ContractUnit_sheet_[j].iloc[num1-1])

						else:
							self.delta[j].append(self.BT_delta_sheet_.loc[i,j]*self.OptionPosition_[j].loc[i,j]*self.BT_ContractUnit_sheet_.loc[i,j])
							self.gamma[j].append(self.BT_gamma_sheet_.loc[i,j]*self.OptionPosition_[j].loc[i,j]*self.BT_ContractUnit_sheet_.loc[i,j])
							self.vega[j].append(self.BT_vega_sheet_.loc[i,j]*self.OptionPosition_[j].loc[i,j]*self.BT_ContractUnit_sheet_.loc[i,j])
							self.theta[j].append(self.BT_theta_sheet_.loc[i,j]*self.OptionPosition_[j].loc[i,j]*self.BT_ContractUnit_sheet_.loc[i,j])

						self.Trade_delta[j].append(self.BT_delta_sheet_.loc[i,j]*self.OptionPositionDiff_[j].loc[i,j]*self.BT_ContractUnit_sheet_.loc[i,j])
						self.Trade_gamma[j].append(self.BT_gamma_sheet_.loc[i,j]*self.OptionPositionDiff_[j].loc[i,j]*self.BT_ContractUnit_sheet_.loc[i,j])
						self.Trade_vega[j].append(self.BT_vega_sheet_.loc[i,j]*self.OptionPositionDiff_[j].loc[i,j]*self.BT_ContractUnit_sheet_.loc[i,j])
						self.Trade_theta[j].append(self.BT_theta_sheet_.loc[i,j]*self.OptionPositionDiff_[j].loc[i,j]*self.BT_ContractUnit_sheet_.loc[i,j])
		

						self.OptionTradeBuyVolume[j].append(0)
						self.OptionTradeSellVolume[j].append(0)
						self.OptionCost[j].append(0)	
						
							
				else:# j not in optionpool
					
					self.OptionMarginAccount[j].append(0)
					self.OptionValue[j].append(0)
					self.premium[j].append(0)
					

					self.delta[j].append(0)
					self.gamma[j].append(0)
					self.vega[j].append(0)
					self.theta[j].append(0)
		
					self.Trade_delta[j].append(0)
					self.Trade_gamma[j].append(0)
					self.Trade_vega[j].append(0)
					self.Trade_theta[j].append(0)
					
					self.OptionTradeBuyVolume[j].append(0)
					self.OptionTradeSellVolume[j].append(0)
					self.OptionCost[j].append(0)
	
					if num1>=1:					
						self.ETFInHand[j].append(self.ETFInHand[j][-1])
						self.ETFDebt[j].append(self.ETFDebt[j][-1])
					else:
						self.ETFInHand[j].append(0)
						self.ETFDebt[j].append(0)
	
		#每只期权每日盈亏
		
		
		self.OptionMarginAccount_sheet_=pd.DataFrame(self.OptionMarginAccount,index=self.BackTestInterval)
		self.OptionValue_sheet_=pd.DataFrame(self.OptionValue,index=self.BackTestInterval)
		
		self.premium_sheet_=pd.DataFrame(self.premium,index=self.BackTestInterval)
		
		

		self.OptionTradeBuyVolume_sheet_=pd.DataFrame(self.OptionTradeBuyVolume,index=self.BackTestInterval)
		self.OptionTradeSellVolume_sheet_=pd.DataFrame(self.OptionTradeSellVolume,index=self.BackTestInterval)
		self.OptionCost_sheet_=pd.DataFrame(self.OptionCost,index=self.BackTestInterval)
		
		#每只期权每日Greeks变化
		self.Delta_sheet_=pd.DataFrame(self.delta,index=self.BackTestInterval)
		self.Gamma_sheet_=pd.DataFrame(self.gamma,index=self.BackTestInterval)
		self.Vega_sheet_=pd.DataFrame(self.vega,index=self.BackTestInterval)
		self.Theta_sheet_=pd.DataFrame(self.theta,index=self.BackTestInterval)
	
		self.Trade_Delta_sheet_=pd.DataFrame(self.Trade_delta,index=self.BackTestInterval)
		self.Trade_Gamma_sheet_=pd.DataFrame(self.Trade_gamma,index=self.BackTestInterval)
		self.Trade_Vega_sheet_=pd.DataFrame(self.Trade_vega,index=self.BackTestInterval)
		self.Trade_Theta_sheet_=pd.DataFrame(self.Trade_theta,index=self.BackTestInterval)
		
		#每只期权每日盈亏累计
		
		
		self.OptionMarginAccountSum_sheet_=self.OptionMarginAccount_sheet_.cumsum()
		self.OptionValueSum_sheet_=self.OptionValue_sheet_.cumsum()
		#print self.OptionValueSum_sheet_.loc['2016-11-01':'2017-02-01',[u'50ETF购2016年12月2.348A',u'50ETF购2016年12月2.397A',u'50ETF购2017年3月2.348A',u'50ETF购2017年3月2.397A',u'50ETF购2016年11月2.35']]
		self.premiumSum_sheet_=self.premium_sheet_.cumsum()

		self.ETFInHandSum_sheet_=pd.DataFrame(self.ETFInHand,index=self.BackTestInterval)#持有的ETF
		self.ETFDebtSum_sheet_=pd.DataFrame(self.ETFDebt,index=self.BackTestInterval)
		#ETF净头寸
		netETFPositionSum=[a+b for a,b in zip(self.ETFInHandSum_sheet_.sum(axis=1),self.ETFDebtSum_sheet_.sum(axis=1))]
		self.netETFPositionSum_=pd.DataFrame(netETFPositionSum,index=self.BackTestInterval,columns=['netETF'])

		self.netETFPosition_=self.netETFPositionSum_.diff(1)
		self.netETFPosition_.iloc[0]=self.netETFPositionSum_.iloc[0]

		self.ETFMargin=[]
		self.ETFTrade=[]
		for i in self.BackTestInterval:
			self.ETFTrade.append(-self.underlying.loc[i,'spot']*self.netETFPosition_.loc[i,'netETF'])
			if self.netETFPosition_.loc[i,'netETF']>=0:
				self.ETFMargin.append(0)
			else:
				self.ETFMargin.append(self.underlying.loc[i,'spot']*self.netETFPosition_.loc[i,'netETF']*0.4)
		self.ETFTrade_=pd.DataFrame(self.ETFTrade,index=self.BackTestInterval,columns=['ETFTrade'])	
		self.ETFMargin_=pd.DataFrame(self.ETFMargin,index=self.BackTestInterval,columns=['ETFMargin'])

		self.ETFTradeSum_=self.ETFTrade_.cumsum()
		self.ETFMarginSum_=self.ETFMargin_.cumsum()
		

		self.ETFInHand_sheet_=self.ETFInHandSum_sheet_.diff(1)
		self.ETFInHand_sheet_.iloc[0]=self.ETFInHandSum_sheet_.iloc[0]
		
		self.ETFDebt_sheet_=self.ETFDebtSum_sheet_.diff(1)
		self.ETFDebt_sheet_.iloc[0]=self.ETFDebtSum_sheet_.iloc[0]
		

		self.OptionTradeBuyVolumeSum_sheet_=self.OptionTradeBuyVolume_sheet_.cumsum()
		self.OptionTradeSellVolumeSum_sheet_=self.OptionTradeSellVolume_sheet_.cumsum()
		self.OptionCostSum_sheet_=self.OptionCost_sheet_.cumsum()
		
		#每只期权每日Greeks累计
		self.DeltaSum_sheet_=self.Delta_sheet_.cumsum()
		self.GammaSum_sheet_=self.Gamma_sheet_.cumsum()
		self.VegaSum_sheet_=self.Vega_sheet_.cumsum()
		self.ThetaSum_sheet_=self.Theta_sheet_.cumsum()

		self.Trade_DeltaSum_sheet_=self.Trade_Delta_sheet_.cumsum()
		self.Trade_GammaSum_sheet_=self.Trade_Gamma_sheet_.cumsum()
		self.Trade_VegaSum_sheet_=self.Trade_Vega_sheet_.cumsum()
		self.Trade_ThetaSum_sheet_=self.Trade_Theta_sheet_.cumsum()
		
		#每日盈亏
		
		
		self.OptionMarginAccount_=pd.DataFrame(self.OptionMarginAccount_sheet_.sum(axis=1),columns=['OptionMarginAccount'])
		self.OptionValue_=pd.DataFrame(self.OptionValue_sheet_.sum(axis=1),columns=['OptionValue'])
		
		self.premium_=pd.DataFrame(self.premium_sheet_.sum(axis=1),columns=['premium'])

		self.OptionTradeBuyVolume_=pd.DataFrame(self.OptionTradeBuyVolume_sheet_.sum(axis=1),columns=['TradeVolume'])
		self.OptionTradeSellVolume_=pd.DataFrame(self.OptionTradeSellVolume_sheet_.sum(axis=1),columns=['TradeVolume'])
		self.OptionCost_=pd.DataFrame(self.OptionCost_sheet_.sum(axis=1),columns=['OptionCost'])
		
		#每日Greeks
		self.Delta_=pd.DataFrame(self.Delta_sheet_.sum(axis=1),columns=['delta'])
		self.Gamma_=pd.DataFrame(self.Gamma_sheet_.sum(axis=1),columns=['gamma'])
		self.Vega_=pd.DataFrame(self.Vega_sheet_.sum(axis=1),columns=['vega'])
		self.Theta_=pd.DataFrame(self.Theta_sheet_.sum(axis=1),columns=['theta'])

		self.Trade_Delta_=pd.DataFrame(self.Trade_Delta_sheet_.sum(axis=1),columns=['delta'])
		self.Trade_Gamma_=pd.DataFrame(self.Trade_Gamma_sheet_.sum(axis=1),columns=['gamma'])
		self.Trade_Vega_=pd.DataFrame(self.Trade_Vega_sheet_.sum(axis=1),columns=['vega'])
		self.Trade_Theta_=pd.DataFrame(self.Trade_Theta_sheet_.sum(axis=1),columns=['theta'])
		
		#每日盈亏累计
		
		
		self.OptionMarginAccountSum_=self.OptionMarginAccount_.cumsum()
		self.OptionValueSum_=self.OptionValue_.cumsum()
	
		self.premiumSum_=self.premium_.cumsum()
		self.OptionTradeBuyVolumeSum_=self.OptionTradeBuyVolume_.cumsum()
		self.OptionTradeSellVolumeSum_=self.OptionTradeSellVolume_.cumsum()
		self.OptionCostSum_=self.OptionCost_.cumsum()

		self.ETFInHandSum_=pd.DataFrame(self.ETFInHandSum_sheet_.sum(axis=1),columns=['ETFInHand'])
		self.ETFDebtSum_=pd.DataFrame(self.ETFDebtSum_sheet_.sum(axis=1),columns=['ETFDebt'])

		self.ETFInHand_=self.ETFInHandSum_.diff(1)
		self.ETFInHand_.iloc[0]=self.ETFInHandSum_.iloc[0]
		self.ETFDebt_=self.ETFDebtSum_.diff(1)
		self.ETFDebt_.iloc[0]=self.ETFDebtSum_.iloc[0]

		ETFValueSum=[]
		ETFDebtValueSum=[]
		netETFValueSum=[]
		for num,i in enumerate(self.BackTestInterval):
			ETFValueSum.append(self.underlying.loc[i,'spot']*self.ETFInHandSum_.loc[i,'ETFInHand'])
			ETFDebtValueSum.append(self.underlying.loc[i,'spot']*self.ETFDebtSum_.loc[i,'ETFDebt'])
			netETFValueSum.append(self.underlying.loc[i,'spot']*self.netETFPositionSum_.loc[i,'netETF'])
		self.ETFValueSum_=pd.DataFrame(ETFValueSum,index=self.BackTestInterval,columns=['ETFValue'])
		self.ETFDebtValueSum_=pd.DataFrame(ETFDebtValueSum,index=self.BackTestInterval,columns=['ETFDebt'])
		self.netETFValueSum_=pd.DataFrame(netETFValueSum,index=self.BackTestInterval,columns=['netETF'])
		
		self.netETFValue_=self.netETFValueSum_.diff(1)
		self.netETFValue_.iloc[0]=self.netETFValueSum_.iloc[0]
		
	
		self.ETFValue_=self.ETFValueSum_.diff(1)
		self.ETFValue_.iloc[0]=self.ETFValueSum_.iloc[0]
		self.ETFDebtValue_=self.ETFDebtValueSum_.diff(1)
		self.ETFDebtValue_.iloc[0]=self.ETFDebtValueSum_.iloc[0]
			

		#每日Greeks累计
		self.DeltaSum_=self.Delta_.cumsum()
		self.GammaSum_=self.Gamma_.cumsum()
		self.VegaSum_=self.Vega_.cumsum()
		self.ThetaSum_=self.Theta_.cumsum()
			
		self.Trade_DeltaSum_=self.Trade_Delta_.cumsum()
		self.Trade_GammaSum_=self.Trade_Gamma_.cumsum()
		self.Trade_VegaSum_=self.Trade_Vega_.cumsum()
		self.Trade_ThetaSum_=self.Trade_Theta_.cumsum()
		
		#ETF 期权每日盈亏
		self.option_value_trade=[a+b for a,b in zip(self.premium_['premium'],self.OptionValue_['OptionValue'])]
		self.option_value_trade_=pd.DataFrame(self.option_value_trade,index=self.BackTestInterval,columns=['option_value_trade'])
		self.ETF_value_trade=[a+b for a,b in zip(self.ETFTrade_['ETFTrade'],self.netETFValue_['netETF'])]
		self.ETF_value_trade_=pd.DataFrame(self.ETF_value_trade,index=self.BackTestInterval,columns=['ETF_value_trade'])
		
		#ETF 期权每日盈亏累计
		self.option_value_trade_sum_=self.option_value_trade_.cumsum()
		self.ETF_value_trade_sum_=self.ETF_value_trade_.cumsum()

		#ETF交易每天的手续费
		self.ETFCost=[]
		for i in self.ETFTrade_['ETFTrade']:
			if i!=0:
				if abs(i*self.costrate)<self.fixcostrate:
					self.ETFCost.append(self.fixcostrate)
				else:
					self.ETFCost.append(abs(i*self.costrate))
			else:
				self.ETFCost.append(0)
			
				
		self.ETFCost_=pd.DataFrame(self.ETFCost,index=self.BackTestInterval,columns=['ETFCost'])
		self.ETFCostSum_=self.ETFCost_.cumsum()
		
		#cash
		self.cashinhand=[a+b+c+d-e for a,b,c,d,e in zip(self.ETFTrade_['ETFTrade'],self.premium_['premium'],self.ETFMargin_['ETFMargin'],self.OptionMarginAccount_['OptionMarginAccount'],self.ETFCost_['ETFCost'])]
		self.CashInHand_=pd.DataFrame(self.cashinhand,index=self.BackTestInterval,columns=['cashinhand'])
		self.CashInHandSum_=self.CashInHand_.cumsum()+self.capital_temp	

		self.additionFund=[]
		for i in self.CashInHandSum_['cashinhand']:
			if i>=0:
				self.additionFund.append(0)	
			else:
				self.additionFund.append(abs(i))
		self.additionFund_=pd.DataFrame(self.additionFund,index=self.BackTestInterval,columns=['additionFund'])

		#总权益
		self.Asset=[a+b+c+d-e for a,b,c,d,e in zip(self.ETFTrade_['ETFTrade'],self.premium_['premium'],self.OptionValue_['OptionValue'],self.netETFValue_['netETF'],self.ETFCost_['ETFCost'])]
		self.Asset_=pd.DataFrame(self.Asset,index=self.BackTestInterval,columns=['Asset'])
		self.AssetSum_=self.Asset_.cumsum()+self.capital_temp

	def YieldRate(self):
		#累计收益率
		self.yield_rate=[a/(self.capital_temp+b)-1 for a,b in zip(self.AssetSum_['Asset'],self.additionFund_['additionFund'])]
		self.yield_rate_=pd.DataFrame(self.yield_rate,index=self.BackTestInterval,columns=['yield_rate'])
		#年化收益率
		self.yield_rate_to_year=[(a[0]/(self.capital_temp+a[1])-1)/(i+1)*252 for i,a in enumerate(zip(self.AssetSum_['Asset'],self.additionFund_['additionFund']))]
		self.yield_rate_to_year_=pd.DataFrame(self.yield_rate_to_year,index=self.BackTestInterval,columns=['yield_rate'])
		
		
			
	def MaxDrawback(self):
		self.maxdrawback=[]
		for i,d in enumerate(self.AssetSum_['Asset']):
    			temp=self.AssetSum_[:i+1].rolling(window=i+1,center=False).max().iloc[-1].values
    			self.maxdrawback.append((d-temp)/temp)
		self.maxdrawback_=pd.DataFrame(self.maxdrawback,index=self.BackTestInterval,columns=['drawback'])
		self.MaxDrawback=np.min(self.maxdrawback_).values

	def MaxDrawback_num(self,num):
		self.maxdrawback_num=[]
		for i,d in enumerate(self.AssetSum_['Asset']):
    			if i<=num-1:
        			temp=self.AssetSum_[:i+1].rolling(window=i+1,center=False).max().iloc[-1].values
        			self.maxdrawback_num.append((d-temp)/temp)
    			else:
        			temp=self.AssetSum_[i-num+1:i+1].rolling(window=num,center=False).max().iloc[-1].values
        			self.maxdrawback_num.append((d-temp)/temp)
		self.maxdrawback_num_=pd.DataFrame(self.maxdrawback_num,index=self.BackTestInterval,columns=['drawback'])
		self.MaxDrawback_num=np.min(self.maxdrawback_num_).values
		#

	
			











































