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
	def __init__(self,start,end,capital,costrate):		
		self.start=start
		self.end=end
		self.capital=capital
		self.capital_temp=capital
		self.costrate=costrate
		self.data=dt.sheetData()
		self.realizedVolatility=dt.realizedVolatility()
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
		
	def OptionPosition(self):
		self.OptionPosition={}
		for i in self.data.option_names:
			self.OptionPosition[i]=[]
		for number,date in enumerate(self.BackTestInterval):
			OptionPool=self.BT_delta_sheet_.loc[date].dropna().index
			deltaPortsfolioOneday=0
			SI=self.StrategyImport(date)
			example=pd.DataFrame(SI)
			num=0
			for option in self.data.option_names:
				if option in OptionPool:
					if option in example:
						self.OptionPosition[option].append(example.loc[num,option])
						num=num+1
					else:
						self.OptionPosition[option].append(0)
				else:
					self.OptionPosition[option].append(0)
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
		
		self.CashInHandSum=[]

		self.ETFTrade={}
		self.ETFMarginAccount={}
		self.OptionMarginAccount={}
		self.OptionValue={}
		self.ShortValue={}
		self.premium={}
		
		self.delta={}
		self.gamma={}
		self.vega={}
		self.theta={}
		
		self.OptionTradeBuyVolume={}
		self.OptionTradeSellVolume={}
		self.OptionCost={}
		self.ETFCost={}
		for i in self.data.option_names:
			self.ETFTrade[i]=[]
			self.ETFMarginAccount[i]=[]
			self.OptionMarginAccount[i]=[]
			self.OptionValue[i]=[]
			self.ShortValue[i]=[]
			self.premium[i]=[]
			
			self.delta[i]=[]
			self.gamma[i]=[]
			self.vega[i]=[]
			self.theta[i]=[]
			
			self.OptionTradeBuyVolume[i]=[]
			self.OptionTradeSellVolume[i]=[]
			self.OptionCost[i]=[]
			self.ETFCost[i]=[]
		for num1,i in enumerate(self.BackTestInterval):
			optionpool=self.BT_delta_sheet_.loc[i].dropna().index
			if len(self.CashInHandSum)==0:
				cashinhand=self.capital
			else:
				cashinhand=self.CashInHandSum[-1]
			for j in self.data.option_names:
				if j in optionpool:
#---------------------------------------------------------------------多头--------------------------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
					if self.OptionPositionDiff_[j].loc[i,j]>0:
						#多头的期权费及手续费
						self.OptionTradeBuyVolume[j].append(self.OptionPositionDiff_[j].loc[i,j])
						self.OptionTradeSellVolume[j].append(0)
						if num1>=1:
							self.premium[j].append(-(self.OptionPosition_[j].loc[i,j]*self.BT_mktprice_sheet_.loc[i,j]*self.BT_ContractUnit_sheet_.loc[i,j]-self.OptionPosition_[j].iloc[num1-1,0]*self.BT_mktprice_sheet_[j].iloc[num1-1]*self.BT_ContractUnit_sheet_[j].iloc[num1-1])-self.OptionPositionDiff_[j].loc[i,j]*(1.3+0.3+10))
						else:
							self.premium[j].append(-self.OptionPosition_[j].loc[i,j]*self.BT_mktprice_sheet_.loc[i,j]*self.BT_ContractUnit_sheet_.loc[i,j]-self.OptionPositionDiff_[j].loc[i,j]*(1.3+0.3+10))
						self.OptionCost[j].append(self.OptionPositionDiff_[j].loc[i,j]*(1.3+0.3+10))
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
							if num1>=1:
								#ETFTrade变化量
								temp1=self.underlying.loc[i,'spot']*self.BT_delta_sheet_.loc[i,j]*self.BT_ContractUnit_sheet_.loc[i,j]*self.OptionPosition_[j].loc[i,j]-self.underlying.iloc[num1-1,0]*self.BT_delta_sheet_[j].iloc[num1-1]*self.BT_ContractUnit_sheet_[j].iloc[num1-1]*self.OptionPosition_[j].iloc[num1-1,0]
								#ETFtrade交易额
								temp2=self.underlying.loc[i,'spot']*self.BT_delta_sheet_.loc[i,j]*self.BT_ContractUnit_sheet_.loc[i,j]*self.OptionPositionDiff_[j].loc[i,j]
							else:
								temp1=self.underlying.loc[i,'spot']*self.BT_delta_sheet_.loc[i,j]*self.BT_ContractUnit_sheet_.loc[i,j]*self.OptionPositionDiff_[j].loc[i,j]
								temp2=temp1
							if abs(temp2*self.costrate)<5:
								self.ETFTrade[j].append(temp1-5)
								self.ETFCost[j].append(5)
							else:
								self.ETFTrade[j].append(temp1-abs(temp2*self.costrate))
								self.ETFCost[j].append(abs(temp2*self.costrate))
							self.ShortValue[j].append(-temp1)
		
							#-------------------------------ETF保证金每日变化-----------------------------------------------
							if num1>=1:
								if self.OptionPosition_[j].iloc[num1-1,0]>=0 and self.OptionPosition_[j].loc[i,j]>0:
									temp=self.underlying.loc[i,'spot']*self.BT_delta_sheet_.loc[i,j]*self.BT_ContractUnit_sheet_.loc[i,j]*self.OptionPosition_[j].loc[i,j]-self.underlying.iloc[num1-1,0]*self.BT_delta_sheet_[j].iloc[num1-1]*self.BT_ContractUnit_sheet_[j].iloc[num1-1]*self.OptionPosition_[j].iloc[num1-1,0]
									self.ETFMarginAccount[j].append(-temp*0.4)
								elif self.OptionPosition_[j].iloc[num1-1,0]<0 and self.OptionPosition_[j].loc[i,j]>=0:
									temp=self.OptionPosition_[j].loc[i,j]*self.underlying.loc[i,'spot']*self.BT_delta_sheet_.loc[i,j]*self.BT_ContractUnit_sheet_.loc[i,j]
									self.ETFMarginAccount[j].append(-temp*0.4)
								else:
									self.ETFMarginAccount[j].append(0)
							else:
								temp=self.OptionPosition_[j].loc[i,j]*self.underlying.loc[i,'spot']*self.BT_delta_sheet_.loc[i,j]*self.BT_ContractUnit_sheet_.loc[i,j]
								self.ETFMarginAccount[j].append(-temp*0.4)
							#0.6*temp新增可用资金
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
							if num1>=1:
								temp1=self.underlying.loc[i,'spot']*self.BT_delta_sheet_.loc[i,j]*self.BT_ContractUnit_sheet_.loc[i,j]*self.OptionPosition_[j].loc[i,j]-self.underlying.iloc[num1-1,0]*self.BT_delta_sheet_[j].iloc[num1-1]*self.BT_ContractUnit_sheet_[j].iloc[num1-1]*self.OptionPosition_[j].iloc[num1-1,0]
								temp2=self.underlying.loc[i,'spot']*self.BT_delta_sheet_.loc[i,j]*self.BT_ContractUnit_sheet_.loc[i,j]*self.OptionPositionDiff_[j].loc[i,j]
							else:
								temp1=self.underlying.loc[i,'spot']*self.BT_delta_sheet_.loc[i,j]*self.BT_ContractUnit_sheet_.loc[i,j]*self.OptionPositionDiff_[j].loc[i,j]
								temp2=temp1

							if abs(temp2*self.costrate)<5:
								self.ETFTrade[j].append(temp1-5)
								self.ETFCost[j].append(5)
							else:
								self.ETFTrade[j].append(temp1-abs(temp2*self.costrate))
								self.ETFCost[j].append(abs(temp2*self.costrate))
							self.ShortValue[j].append(-temp1)
							#-------------------------------ETF保证金每日变化---------------------------------------------------
							if num1>=1:
								if self.OptionPosition_[j].iloc[num1-1,0]>=0 and self.OptionPosition_[j].loc[i,j]>0:
									self.ETFMarginAccount[j].append(0)
								elif self.OptionPosition_[j].iloc[num1-1,0]<0 and self.OptionPosition_[j].loc[i,j]>=0:
									temp=(0-self.OptionPosition_[j].iloc[num1-1,0]*self.underlying.iloc[num1-1,0]*self.BT_delta_sheet_[j].iloc[num1-1]*self.BT_ContractUnit_sheet_[j].iloc[num1-1])
									self.ETFMarginAccount[j].append(-temp*0.4)
								else:
									temp=self.underlying.loc[i,'spot']*self.BT_delta_sheet_.loc[i,j]*self.BT_ContractUnit_sheet_.loc[i,j]*self.OptionPosition_[j].loc[i,j]-self.underlying.iloc[num1-1,0]*self.BT_delta_sheet_[j].iloc[num1-1]*self.BT_ContractUnit_sheet_[j].iloc[num1-1]*self.OptionPosition_[j].iloc[num1-1,0]
									self.ETFMarginAccount[j].append(-temp*0.4)
							else:
								self.ETFMarginAccount[j].append(0)
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

						temp_capital=self.premium[j][-1]+self.ETFTrade[j][-1]+self.ETFMarginAccount[j][-1]+self.OptionMarginAccount[j][-1]
						cashinhand=cashinhand+temp_capital
#-------------------------------------------------------------------------------------------------------空头------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
					elif self.OptionPositionDiff_[j].loc[i,j]<0:
						#空头的期权费及手续费
						self.OptionTradeBuyVolume[j].append(0)
						self.OptionTradeSellVolume[j].append(self.OptionPositionDiff_[j].loc[i,j])
						if num1>=1:
							self.premium[j].append(-(self.OptionPosition_[j].loc[i,j]*self.BT_mktprice_sheet_.loc[i,j]*self.BT_ContractUnit_sheet_.loc[i,j]-self.OptionPosition_[j].iloc[num1-1,0]*self.BT_mktprice_sheet_[j].iloc[num1-1]*self.BT_ContractUnit_sheet_[j].iloc[num1-1])-abs(self.OptionPositionDiff_[j].loc[i,j]*(1.3+0.3+10)))
						else:
							self.premium[j].append(-self.OptionPosition_[j].loc[i,j]*self.BT_mktprice_sheet_.loc[i,j]*self.BT_ContractUnit_sheet_.loc[i,j]-abs(self.OptionPositionDiff_[j].loc[i,j]*(1.3+0.3+10)))
						self.OptionCost[j].append(abs(self.OptionPositionDiff_[j].loc[i,j]*(1.3+0.3+10)))
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
							if num1>=1:
								#ETFTrade变化量
								temp1=self.underlying.loc[i,'spot']*self.BT_delta_sheet_.loc[i,j]*self.BT_ContractUnit_sheet_.loc[i,j]*self.OptionPosition_[j].loc[i,j]-self.underlying.iloc[num1-1,0]*self.BT_delta_sheet_[j].iloc[num1-1]*self.BT_ContractUnit_sheet_[j].iloc[num1-1]*self.OptionPosition_[j].iloc[num1-1,0]
								#ETFtrade交易额
								temp2=self.underlying.loc[i,'spot']*self.BT_delta_sheet_.loc[i,j]*self.BT_ContractUnit_sheet_.loc[i,j]*self.OptionPositionDiff_[j].loc[i,j]
							else:
								temp1=self.underlying.loc[i,'spot']*self.BT_delta_sheet_.loc[i,j]*self.BT_ContractUnit_sheet_.loc[i,j]*self.OptionPositionDiff_[j].loc[i,j]
								temp2=temp1
							if abs(temp2*self.costrate)<5:
								self.ETFTrade[j].append(temp1-5)
								self.ETFCost[j].append(5)
							else:
								self.ETFTrade[j].append(temp1-abs(temp2*self.costrate))
								self.ETFCost[j].append(abs(temp2*self.costrate))
							self.ShortValue[j].append(-temp1)
							#-------------------------------------ETF保证金每日变化-----------------------------------------------
							if num1>=1:
								if self.OptionPosition_[j].iloc[num1-1,0]>0 and self.OptionPosition_[j].loc[i,j]>=0:
									temp=self.underlying.loc[i,'spot']*self.BT_delta_sheet_.loc[i,j]*self.BT_ContractUnit_sheet_.loc[i,j]*self.OptionPosition_[j].loc[i,j]-self.underlying.iloc[num1-1,0]*self.BT_delta_sheet_[j].iloc[num1-1]*self.BT_ContractUnit_sheet_[j].iloc[num1-1]*self.OptionPosition_[j].iloc[num1-1,0]
									self.ETFMarginAccount[j].append(-temp*0.4)
								elif self.OptionPosition_[j].iloc[num1-1,0]>=0 and self.OptionPosition_[j].loc[i,j]<0:
									temp=self.OptionPosition_[j].iloc[num1-1,0]*self.underlying.iloc[num1-1,0]*self.BT_delta_sheet_[j].iloc[num1-1]*self.BT_ContractUnit_sheet_[j].iloc[num1-1]
									self.ETFMarginAccount[j].append(-temp*0.4)
								else:
									self.ETFMarginAccount[j].append(0)
							else:
								self.ETFMarginAccount[j].append(0)
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
							if num1>=1:
								temp1=self.underlying.loc[i,'spot']*self.BT_delta_sheet_.loc[i,j]*self.BT_ContractUnit_sheet_.loc[i,j]*self.OptionPosition_[j].loc[i,j]-self.underlying.iloc[num1-1,0]*self.BT_delta_sheet_[j].iloc[num1-1]*self.BT_ContractUnit_sheet_[j].iloc[num1-1]*self.OptionPosition_[j].iloc[num1-1,0]
								temp2=self.underlying.loc[i,'spot']*self.BT_delta_sheet_.loc[i,j]*self.BT_ContractUnit_sheet_.loc[i,j]*self.OptionPositionDiff_[j].loc[i,j]
							else:
								temp1=self.underlying.loc[i,'spot']*self.BT_delta_sheet_.loc[i,j]*self.BT_ContractUnit_sheet_.loc[i,j]*self.OptionPositionDiff_[j].loc[i,j]
								temp2=temp1

							if abs(temp2*self.costrate)<5:
								self.ETFTrade[j].append(temp1-5)
								self.ETFCost[j].append(5)
							else:
								self.ETFTrade[j].append(temp1-abs(temp2*self.costrate))
								self.ETFCost[j].append(abs(temp2*self.costrate))
							self.ShortValue[j].append(-temp1)
							#-------------------------------ETF保证金每日变化---------------------------------------------------###???
							if num1>=1:
								if self.OptionPosition_[j].iloc[num1-1,0]>0 and self.OptionPosition_[j].loc[i,j]>0:
									self.ETFMarginAccount[j].append(0)
								elif self.OptionPosition_[j].iloc[num1-1,0]>0 and self.OptionPosition_[j].loc[i,j]<0:
									temp=self.OptionPosition_[j].loc[i,j]*self.underlying.loc[i,'spot']*self.BT_delta_sheet_.loc[i,j]*self.BT_ContractUnit_sheet_.loc[i,j]
									self.ETFMarginAccount[j].append(-temp*0.4)
								else:
									temp=self.underlying.loc[i,'spot']*self.BT_delta_sheet_.loc[i,j]*self.BT_ContractUnit_sheet_.loc[i,j]*self.OptionPosition_[j].loc[i,j]-self.underlying.iloc[num1-1,0]*self.BT_delta_sheet_[j].iloc[num1-1]*self.BT_ContractUnit_sheet_[j].iloc[num1-1]*self.OptionPosition_[j].iloc[num1-1,0]
									self.ETFMarginAccount[j].append(-temp*0.4)
							else:
								temp=self.OptionPosition_[j].loc[i,j]*self.underlying.loc[i,'spot']*self.BT_delta_sheet_.loc[i,j]*self.BT_ContractUnit_sheet_.loc[i,j]
								self.ETFMarginAccount[j].append(-temp*0.4)
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

							#--------------------------------------------------------------------------------------------------
						temp_capital=self.premium[j][-1]+self.ETFTrade[j][-1]+self.ETFMarginAccount[j][-1]+self.OptionMarginAccount[j][-1]
						cashinhand=cashinhand+temp_capital
						
					else:#OptionPositionDiff_[j].loc[i,j]==0
						#ETF交易不变
						self.ETFTrade[j].append(0)
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
							#ETF保证金变化
							if self.OptionPosition_[j].loc[i,j]>0:
								if num1>=1:
									temp=self.underlying.loc[i,'spot']*self.BT_delta_sheet_.loc[i,j]*self.BT_ContractUnit_sheet_.loc[i,j]*self.OptionPosition_[j].loc[i,j]-self.underlying.iloc[num1-1,0]*self.BT_delta_sheet_[j].iloc[num1-1]*self.BT_ContractUnit_sheet_[j].iloc[num1-1]*self.OptionPosition_[j].iloc[num1-1,0]
									self.ETFMarginAccount[j].append(-temp*0.4)
								else:
									self.ETFMarginAccount[j].append(0)
							else:	
								self.ETFMarginAccount[j].append(0)
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
							#ETF保证金变化
							if self.OptionPosition_[j].loc[i,j]>0:
								if num1>=1:
									self.ETFMarginAccount[j].append(0)
								else:
									temp=self.underlying.loc[i,'spot']*self.BT_delta_sheet_.loc[i,j]*self.BT_ContractUnit_sheet_.loc[i,j]*self.OptionPosition_[j].loc[i,j]-self.underlying.iloc[num1-1,0]*self.BT_delta_sheet_[j].iloc[num1-1]*self.BT_ContractUnit_sheet_[j].iloc[num1-1]*self.OptionPosition_[j].iloc[num1-1,0]
									self.ETFMarginAccount[j].append(-temp*0.4)
							elif self.OptionPosition_[j].loc[i,j]<0:	
								temp=self.underlying.loc[i,'spot']*self.BT_delta_sheet_.loc[i,j]*self.BT_ContractUnit_sheet_.loc[i,j]*self.OptionPosition_[j].loc[i,j]-self.underlying.iloc[num1-1,0]*self.BT_delta_sheet_[j].iloc[num1-1]*self.BT_ContractUnit_sheet_[j].iloc[num1-1]*self.OptionPosition_[j].iloc[num1-1,0]
								self.ETFMarginAccount[j].append(-temp*0.4)
							else:
								self.ETFMarginAccount[j].append(0)


						#期权保证金的变化
						if self.OptionPosition_[j].loc[i,j]>=0:
							self.OptionMarginAccount[j].append(0)
						else:
							if num1>=1:
								self.OptionMarginAccount[j].append(self.OptionPosition_[j].loc[i,j]*abs(self.BT_MarginAccount_sheet_.loc[i,j])-self.OptionPosition_[j].iloc[num1-1,0]*abs(self.BT_MarginAccount_sheet_[j].iloc[num1-1]))
							else:
								self.OptionMarginAccount[j].append(0)
						#shortvalue变化
						if num1>=1:
							temp1=self.underlying.loc[i,'spot']*self.BT_delta_sheet_.loc[i,j]*self.BT_ContractUnit_sheet_.loc[i,j]*self.OptionPosition_[j].loc[i,j]-self.underlying.iloc[num1-1,0]*self.BT_delta_sheet_[j].iloc[num1-1]*self.BT_ContractUnit_sheet_[j].iloc[num1-1]*self.OptionPosition_[j].iloc[num1-1,0]
												
						else:
							temp1=self.underlying.loc[i,'spot']*self.BT_delta_sheet_.loc[i,j]*self.BT_ContractUnit_sheet_.loc[i,j]*self.OptionPositionDiff_[j].loc[i,j]
						self.ShortValue[j].append(-temp1)

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

						self.OptionTradeBuyVolume[j].append(0)
						self.OptionTradeSellVolume[j].append(0)
						self.OptionCost[j].append(0)	
						self.ETFCost[j].append(0)
							
				else:# j not in optionpool
					self.ETFTrade[j].append(0)
					self.ETFMarginAccount[j].append(0)
					self.OptionMarginAccount[j].append(0)
					self.OptionValue[j].append(0)
					self.premium[j].append(0)
					self.ShortValue[j].append(0)

					self.delta[j].append(0)
					self.gamma[j].append(0)
					self.vega[j].append(0)
					self.theta[j].append(0)
					
					self.OptionTradeBuyVolume[j].append(0)
					self.OptionTradeSellVolume[j].append(0)
					self.OptionCost[j].append(0)	
					self.ETFCost[j].append(0)
			self.CashInHandSum.append(cashinhand)
	
		self.CashInHandSum_=pd.DataFrame(self.CashInHandSum,index=self.BackTestInterval,columns=['cashinhand'])
		self.CashInHand_=self.CashInHandSum_.diff(1)
		self.CashInHand_.iloc[0]=self.CashInHandSum_.iloc[0]
		
		#每只期权每日盈亏
		self.ETFTrade_sheet_=pd.DataFrame(self.ETFTrade,index=self.BackTestInterval)
		self.ETFMarginAccount_sheet_=pd.DataFrame(self.ETFMarginAccount,index=self.BackTestInterval)
		self.OptionMarginAccount_sheet_=pd.DataFrame(self.OptionMarginAccount,index=self.BackTestInterval)
		self.OptionValue_sheet_=pd.DataFrame(self.OptionValue,index=self.BackTestInterval)
		self.ShortValue_sheet_=pd.DataFrame(self.ShortValue,index=self.BackTestInterval)
		self.premium_sheet_=pd.DataFrame(self.premium,index=self.BackTestInterval)

		self.OptionTradeBuyVolume_sheet_=pd.DataFrame(self.OptionTradeBuyVolume,index=self.BackTestInterval)
		self.OptionTradeSellVolume_sheet_=pd.DataFrame(self.OptionTradeSellVolume,index=self.BackTestInterval)
		self.OptionCost_sheet_=pd.DataFrame(self.OptionCost,index=self.BackTestInterval)
		self.ETFCost_sheet_=pd.DataFrame(self.ETFCost,index=self.BackTestInterval)
		#每只期权每日Greeks变化
		self.Delta_sheet_=pd.DataFrame(self.delta,index=self.BackTestInterval)
		self.Gamma_sheet_=pd.DataFrame(self.gamma,index=self.BackTestInterval)
		self.Vega_sheet_=pd.DataFrame(self.vega,index=self.BackTestInterval)
		self.Theta_sheet_=pd.DataFrame(self.theta,index=self.BackTestInterval)
		
		#总权益
		self.Asset=[a+b+c+d for a,b,c,d in zip(self.ETFTrade_sheet_.sum(axis=1),self.premium_sheet_.sum(axis=1),self.OptionValue_sheet_.sum(axis=1),self.ShortValue_sheet_.sum(axis=1))]
		self.Asset_=pd.DataFrame(self.Asset,index=self.BackTestInterval,columns=['Asset'])
		self.AssetSum_=self.Asset_.cumsum()+self.capital_temp
		#每只期权每日盈亏累计
		self.ETFTradeSum_sheet_=self.ETFTrade_sheet_.cumsum()
		self.ETFMarginAccountSum_sheet_=self.ETFMarginAccount_sheet_.cumsum()
		self.OptionMarginAccountSum_sheet_=self.OptionMarginAccount_sheet_.cumsum()
		self.OptionValueSum_sheet_=self.OptionValue_sheet_.cumsum()
		self.ShortValueSum_sheet_=self.ShortValue_sheet_.cumsum()
		self.premiumSum_sheet_=self.premium_sheet_.cumsum()
		
		self.OptionTradeBuyVolumeSum_sheet_=self.OptionTradeBuyVolume_sheet_.cumsum()
		self.OptionTradeSellVolumeSum_sheet_=self.OptionTradeSellVolume_sheet_.cumsum()
		self.OptionCostSum_sheet_=self.OptionCost_sheet_.cumsum()
		self.ETFCostSum_sheet_=self.ETFCost_sheet_.cumsum()
		#每只期权每日Greeks累计
		self.DeltaSum_sheet_=self.Delta_sheet_.cumsum()
		self.GammaSum_sheet_=self.Gamma_sheet_.cumsum()
		self.VegaSum_sheet_=self.Vega_sheet_.cumsum()
		self.ThetaSum_sheet_=self.Theta_sheet_.cumsum()
		
		#每日盈亏
		self.ETFTrade_=pd.DataFrame(self.ETFTrade_sheet_.sum(axis=1),columns=['ETFTrade'])
		self.ETFMarginAccount_=pd.DataFrame(self.ETFMarginAccount_sheet_.sum(axis=1),columns=['ETFMarginAccount'])
		self.OptionMarginAccount_=pd.DataFrame(self.OptionMarginAccount_sheet_.sum(axis=1),columns=['OptionMarginAccount'])
		self.OptionValue_=pd.DataFrame(self.OptionValue_sheet_.sum(axis=1),columns=['OptionValue'])
		self.ShortValue_=pd.DataFrame(self.ShortValue_sheet_.sum(axis=1),columns=['ShortValue'])
		self.premium_=pd.DataFrame(self.premium_sheet_.sum(axis=1),columns=['premium'])

		self.OptionTradeBuyVolume_=pd.DataFrame(self.OptionTradeBuyVolume_sheet_.sum(axis=1),columns=['TradeVolume'])
		self.OptionTradeSellVolume_=pd.DataFrame(self.OptionTradeSellVolume_sheet_.sum(axis=1),columns=['TradeVolume'])
		self.OptionCost_=pd.DataFrame(self.OptionCost_sheet_.sum(axis=1),columns=['OptionCost'])
		self.ETFCost_=pd.DataFrame(self.ETFCost_sheet_.sum(axis=1),columns=['ETFCost'])
		#每日Greeks
		self.Delta_=pd.DataFrame(self.Delta_sheet_.sum(axis=1),columns=['delta'])
		self.Gamma_=pd.DataFrame(self.Gamma_sheet_.sum(axis=1),columns=['gamma'])
		self.Vega_=pd.DataFrame(self.Vega_sheet_.sum(axis=1),columns=['vega'])
		self.Theta_=pd.DataFrame(self.Theta_sheet_.sum(axis=1),columns=['theta'])
		
		#每日盈亏累计
		self.ETFTradeSum_=self.ETFTrade_.cumsum()
		self.ETFMarginAccountSum_=self.ETFMarginAccount_.cumsum()
		self.OptionMarginAccountSum_=self.OptionMarginAccount_.cumsum()
		self.OptionValueSum_=self.OptionValue_.cumsum()
		self.ShortValueSum_=self.ShortValue_.cumsum()
		self.premiumSum_=self.premium_.cumsum()
		self.OptionTradeBuyVolumeSum_=self.OptionTradeBuyVolume_.cumsum()
		self.OptionTradeSellVolumeSum_=self.OptionTradeSellVolume_.cumsum()
		self.OptionCostSum_=self.OptionCost_.cumsum()
		self.ETFCostSum_=self.ETFCost_.cumsum()
		#每日Greeks累计
		self.DeltaSum_=self.Delta_.cumsum()
		self.GammaSum_=self.Gamma_.cumsum()
		self.VegaSum_=self.Vega_.cumsum()
		self.ThetaSum_=self.Theta_.cumsum()
		
		#ETF 期权每日盈亏
		self.option_value_trade=[a+b for a,b in zip(self.premium_['premium'],self.OptionValue_['OptionValue'])]
		self.option_value_trade_=pd.DataFrame(self.option_value_trade,index=self.BackTestInterval,columns=['option_value_trade'])
		self.ETF_value_trade=[a+b for a,b in zip(self.ETFTrade_['ETFTrade'],self.ShortValue_['ShortValue'])]
		self.ETF_value_trade_=pd.DataFrame(self.ETF_value_trade,index=self.BackTestInterval,columns=['ETF_value_trade'])
		
		#ETF 期权每日盈亏累计
		self.option_value_trade_sum_=self.option_value_trade_.cumsum()
		self.ETF_value_trade_sum_=self.ETF_value_trade_.cumsum()

		

	def order_target(self,option,num):
    		temp={}
    		temp[option]=num
    		return temp
	def sell_target(self,option,num):
		temp={}
		temp[option]=-num
		return temp
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

	def StrategyImport(self,date):
		SI=[]
		optionpool=pd.DataFrame(self.data.delta_sheet_,index=self.BackTestInterval).loc[date].dropna().index

		
		for option in self.data.option_names:
			if option in optionpool:
				if self.BT_impliedVolatility_sheet_.loc[date,option]>self.realizedVolatility.realizedVol.loc[date,'realizedVol_10']:
					temp=0.99*self.capital/80/(self.BT_mktprice_sheet_.loc[date,option]*self.BT_ContractUnit_sheet_.loc[date,option])
					temp=int(temp)
					SI.append(self.order_target(option,temp))
		'''
		if self.data.option_names[50] in optionpool:
			SI.append(self.sell_target(self.data.option_names[50],1))
		'''
		return SI 
			











































