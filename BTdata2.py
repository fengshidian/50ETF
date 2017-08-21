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
		temp=self.realizedVolatility.underlying[self.start:self.end]
		self.bench_=(temp/temp.iloc[0]-1)
	###策略头寸
	def ichange(self,i,n):
		if i[-1]<0:
			i.append(i[-1]-n)
		else:
			i.append(i[-1]+n)
	
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
	def OptionPosition(self):
		self.OptionPosition={}
		self.temp_optioninhand=[]
		self.temp_exitoption=[]
		for i in self.data.option_names:
			self.OptionPosition[i]=[]
		for number,date in enumerate(self.BackTestInterval):
			_date=str(date)[:10]
			latest_issue_date=self.data.option_startdate[self.data.option_startdate<=_date].iloc[-1]
			optioninhand=[]
			temp={}
			for option in self.data.option_names:
				if option in set(self.data.options_in_startdate[latest_issue_date]+self.temp_optioninhand)-set(self.temp_exitoption):
					if abs(self.BT_delta_sheet_.loc[date,option])>0.7:
						self.append(number,self.OptionPosition[option],0)
						self.temp_exitoption.append(option)
						self.temp_exitoption.append(self.symoption(option))
						self.append(number,self.OptionPosition[self.symoption(option)],0)
					elif self.data.ptmtradeday_sheet_.loc[date,option]<=15:
						self.append(number,self.OptionPosition[option],0)
						self.temp_exitoption.append(option)
						self.temp_exitoption.append(self.symoption(option))
						self.append(number,self.OptionPosition[self.symoption(option)],0)
							
					else:
						if self.realizedVolatility.VolForecast.loc[date,'vol_fore']-self.realizedVolatility.realizedVol_day_10.loc[date,'spot']>=0.01 or self.realizedVolatility.realizedVol_day_10.loc[date,'spot']>=0.025:#预测波动率上升 或 波动率处于高位
							if self.realizedVolatility.underlyingYieldRate.loc[date,'spot']>=0.05:
								if option[5]==u'购':
									self.append(number,self.OptionPosition[option],0)
									#optioninhand.append(option)
								else:
									self.append(number,self.OptionPosition[option],-30)
									optioninhand.append(option)
							elif self.realizedVolatility.underlyingYieldRate.loc[date,'spot']>=0.02:
								if option[5]==u'购':
									self.append(number,self.OptionPosition[option],0)
									#optioninhand.append(option)
								else:
									self.append(number,self.OptionPosition[option],-20)
									optioninhand.append(option)
							elif self.realizedVolatility.underlyingYieldRate.loc[date,'spot']<=-0.05:
								if option[5]==u'购':
									self.append(number,self.OptionPosition[option],-30)
									optioninhand.append(option)
								else:
									self.append(number,self.OptionPosition[option],0)
									#optioninhand.append(option)
							elif self.realizedVolatility.underlyingYieldRate.loc[date,'spot']<=-0.02:
								if option[5]==u'购':
									self.append(number,self.OptionPosition[option],-20)
									optioninhand.append(option)
								else:
									self.append(number,self.OptionPosition[option],0)
									#optioninhand.append(option)
							else:
								
								for k,option1 in enumerate(self.data.options_in_startdate[latest_issue_date]):
									if option==option1:
										for option2 in self.data.options_in_startdate[latest_issue_date]:
											
											if option1[:5]==option2[:5] and option1[5]!=option2[5] and option1[6:]==option2[6:]:
												if option2 in self.temp_exitoption:
													pass
												else:
													if option1[5]==u'购':
														self.append(number,self.OptionPosition[option1],0)
														self.append(number,self.OptionPosition[option2],0)
														#optioninhand.append(option1)
														#optioninhand.append(option2)
													else:
														self.append(number,self.OptionPosition[option1],0)
														self.append(number,self.OptionPosition[option2],0)
						else:
							for k,option1 in enumerate(self.data.options_in_startdate[latest_issue_date]):
								if option==option1:
									for option2 in self.data.options_in_startdate[latest_issue_date]:
										
										if option1[:5]==option2[:5] and option1[5]!=option2[5] and option1[6:]==option2[6:]:
											if option2 in self.temp_exitoption:
												pass
											else:
												if option1[5]==u'购':
													self.append(number,self.OptionPosition[option1],-10)
													self.append(number,self.OptionPosition[option2],-20)
													optioninhand.append(option1)
													optioninhand.append(option2)
												else:	
													self.append(number,self.OptionPosition[option1],-20)
													self.append(number,self.OptionPosition[option2],-10)
			
				else:
					self.append(number,self.OptionPosition[option],0)

			self.temp_option=optioninhand
				

			'''
			for option in self.data.option_names:
				i=[0]
				if option in set(self.data.options_in_startdate[latest_issue_date]+self.temp_optioninhand)-set(self.temp_exitoption):
					
					if self.realizedVolatility.VolForecast.loc[date,'vol_fore']-self.realizedVolatility.realizedVol_day_10.loc[date,'spot']>=0.01 or self.realizedVolatility.realizedVol_day_10.loc[date,'spot']>=0.025:#预测波动率上升 或 波动率处于高位				
						if self.realizedVolatility.underlyingYieldRate.loc[date,'spot']>=0.05:
							self.opn='call'
							self.ichange(i,5)
						elif self.realizedVolatility.underlyingYieldRate.loc[date,'spot']>=0.02:
							self.opn='call'
							self.ichange(i,3)
						elif self.realizedVolatility.underlyingYieldRate.loc[date,'spot']<=-0.05:
							self.opn='put'
							self.ichange(i,5)
						elif self.realizedVolatility.underlyingYieldRate.loc[date,'spot']<=-0.02:
							self.opn='put'
							self.ichange(i,3)
						else:
							self.opn='vol'
							self.ichange(i,1)
					else:
						self.opn='stable'
						
					


					if self.BT_impliedVolatility_sheet_.loc[date,option]<=self.realizedVolatility.realizedVol_day_10.loc[date,'spot']:
						self.ichange(i,1)
					else:
						
						self.ichange(i,-1)
											


					#delta过大或到期期限过短都不进行交易
					if abs(self.BT_delta_sheet_.loc[date,option])<0.8:
						self.ichange(i,0)
					else:
						self.opn='NoTrade'
					if self.data.ptmtradeday_sheet_.loc[date,option]>15:
						self.ichange(i,0)
					else:
						self.opn='NoTrade'


					#
					if self.opn=='call':
						if option[5]==u'购':
							if number==0:
								self.OptionPosition[option].append(i[-1]*10)
							else:
								self.OptionPosition[option].append(i[-1]*10)
							optioninhand.append(option)
						else:
							self.OptionPosition[option].append(-i[-1]*10)
							optioninhand.append(option)
					
					elif self.opn=='put':
						if option[5]==u'购':
							self.OptionPosition[option].append(-i[-1]*10)
							optioninhand.append(option)
						else:
							if number==0:
								self.OptionPosition[option].append(i[-1]*10)
							else:
								self.OptionPosition[option].append(i[-1]*10)
							optioninhand.append(option)
							
					elif self.opn=='vol':
						self.OptionPosition[option].append(-i[-1]*10)
						optioninhand.append(option)
					elif self.opn=='stable':
						



						
						optioninhand.append(option)
					elif self.opn=='NoTrade':
						self.OptionPosition[option].append(0)
					else:
						pass
					
				else:
			
					self.OptionPosition[option].append(0)
					
			self.temp_optioninhand=optioninhand
			'''	
				
		self.Position_=pd.DataFrame(self.OptionPosition,index=self.BackTestInterval,columns=self.data.option_names)
		self.PositionDiff_=self.Position_.diff(1)
		self.PositionDiff_.iloc[0]=self.Position_.iloc[0]
		self.OptionPosition_={}
		self.OptionPositionDiff_={}
		for j in self.data.option_names:
			self.OptionPosition_[j]=pd.DataFrame(self.OptionPosition[j],index=self.BackTestInterval,columns=[j])
			self.OptionPositionDiff_[j]=self.OptionPosition_[j].diff(1)
			self.OptionPositionDiff_[j].iloc[0]=self.OptionPosition_[j].iloc[0]
			
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
						#------------------------------------------------------------------------------
						#多头看涨期权对冲 卖ETF对冲
						if self.BT_delta_sheet_.loc[i,j]>0:#看涨
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
							#--------------------------------------------------------------------------------------						
						else:#self.BT_delta_sheet_.loc[i,j]<0看跌 买ETF对冲
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
#-------------------------------------------------------------------------------------------------------空头------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
					elif self.OptionPositionDiff_[j].loc[i,j]<0:
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
						#-----------------------------------------------------------------------------------------------

						#空头看涨期权对冲 买ETF对冲
						if self.BT_delta_sheet_.loc[i,j]>0:#看涨
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
							#--------------------------------------------------------------------------------------						
						else:#self.BT_delta_sheet_.loc[i,j]<0看跌 买ETF对冲
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
		
		self.premiumSum_sheet_=self.premium_sheet_.cumsum()

		self.ETFInHandSum_sheet_=pd.DataFrame(self.ETFInHand,index=self.BackTestInterval)#持有的ETF
		self.ETFDebtSum_sheet_=pd.DataFrame(self.ETFDebt,index=self.BackTestInterval)
		#ETF净头寸
		netETFPosition=[a+b for a,b in zip(self.ETFInHandSum_sheet_.sum(axis=1),self.ETFDebtSum_sheet_.sum(axis=1))]
		self.netETFPosition_=pd.DataFrame(netETFPosition,index=self.BackTestInterval,columns=['netETF'])

		self.ETFMarginSum=[]
		self.ETFTradeSum=[]
		for i in self.BackTestInterval:
			self.ETFTradeSum.append(-self.underlying.loc[i,'spot']*self.netETFPosition_.loc[i,'netETF'])
			if self.netETFPosition_.loc[i,'netETF']>=0:
				self.ETFMarginSum.append(0)
			else:
				self.ETFMarginSum.append(self.underlying.loc[i,'spot']*self.netETFPosition_.loc[i,'netETF']*0.4)
		self.ETFTradeSum_=pd.DataFrame(self.ETFTradeSum,index=self.BackTestInterval,columns=['ETFTrade'])	
		self.ETFMarginSum_=pd.DataFrame(self.ETFMarginSum,index=self.BackTestInterval,columns=['ETFMargin'])

		self.ETFTrade_=self.ETFTradeSum_.diff(1)
		self.ETFTrade_.iloc[0]=self.ETFTradeSum_.iloc[0]

		self.ETFMargin_=self.ETFMarginSum_.diff(1)
		self.ETFMargin_.iloc[0]=self.ETFMarginSum_.iloc[0]
		

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
			netETFValueSum.append(self.underlying.loc[i,'spot']*self.netETFPosition_.loc[i,'netETF'])
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
		
		#总权益
		self.Asset=[a+b+c+d-e for a,b,c,d,e in zip(self.ETFTrade_['ETFTrade'],self.premium_['premium'],self.OptionValue_['OptionValue'],self.netETFValue_['netETF'],self.ETFCost_['ETFCost'])]
		self.Asset_=pd.DataFrame(self.Asset,index=self.BackTestInterval,columns=['Asset'])
		self.AssetSum_=self.Asset_.cumsum()+self.capital_temp
		

	def YieldRate(self):
		#累计收益率
		self.yield_rate=[a/self.capital_temp-1 for a in self.AssetSum_['Asset']]
		self.yield_rate_=pd.DataFrame(self.yield_rate,index=self.BackTestInterval,columns=['yield_rate'])
		#年化收益率
		self.yield_rate_to_year=[(a/self.capital_temp-1)/(i+1)*252 for i,a in enumerate(self.AssetSum_['Asset'])]
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

	
			











































