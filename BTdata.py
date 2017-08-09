
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
		self.costrate=costrate
		self.data=dt.sheetData()
		self.realizedVolatility=dt.realizedVolatility()
		self.sheet=self.data.delta_sheet_[self.start:self.end]
		self.BackTestInterval=self.data.delta_sheet_[self.start:self.end].index
		self.underlying=self.realizedVolatility.underlying[self.start:self.end]
		self.OptionPosition()
		self.MarginAccount()
		self.DeltaPortfolio()
		self.OptionETFTrade()
		self.OptionValue()
		self.ShortValue()
		self.OptionValueOptionTrade()
		self.ETFValueETFTrade()
		self.TotalAsset()
		self._CashInHand()
		self.YieldRate()
		self.MaxDrawback()
		self.MaxDrawback_num(30)
	def OptionPosition(self):
		self.deltaPortfolio=[]
		self.WWdeltaSup=[]
		self.WWdeltaInf=[]
		self.WWdeltaHold=[]

		self.gammaPortfolio=[]
		self.vegaPortfolio=[]
		self.thetaPortfolio=[]
		self.OptionPosition={}
		for i in self.data.option_names:
    			self.OptionPosition[i]=[]  
		for date in self.BackTestInterval:
    			self.OptionPool=self.data.delta_sheet_.loc[date].dropna().index
    			deltaPortfolioOneDay=0
			WWdeltaSupOneDay=0
			WWdeltaInfOneDay=0
			WWdeltaHoldOneDay=0

			gammaPortfolioOneDay=0
			vegaPortfolioOneDay=0
			thetaPortfolioOneDay=0
    			SI=self.StrategyImport(date)
    			example=pd.DataFrame(SI)
			
    			num=0
    			for option in self.data.option_names:
        			if option in self.OptionPool:#可交易期权
        		#每天购买期权的种类及份数,并计算期权组合delta
            				if option in example:#选出的期权
                				self.OptionPosition[option].append(example.loc[num,option])
                				num=num+1
                				deltaPortfolioOneDay=deltaPortfolioOneDay+self.data.delta_sheet_.loc[date,option]*self.OptionPosition[option][-1]
						WWdeltaSupOneDay=WWdeltaSupOneDay+self.data.WWBandSup_sheet_.loc[date,option]*self.OptionPosition[option][-1]
						WWdeltaInfOneDay=WWdeltaInfOneDay+self.data.WWBandInf_sheet_.loc[date,option]*self.OptionPosition[option][-1]
						WWdeltaHoldOneDay=WWdeltaHoldOneDay+self.data.WWDeltaHold_sheet_.loc[date,option]*self.OptionPosition[option][-1]

						gammaPortfolioOneDay=gammaPortfolioOneDay+self.data.gamma_sheet_.loc[date,option]*self.OptionPosition[option][-1]
						vagePortfolioOneDay=vegaPortfolioOneDay+self.data.vega_sheet_.loc[date,option]*self.OptionPosition[option][-1]
						thetaPortfolioOneDay=thetaPortfolioOneDay+self.data.theta_sheet_.loc[date,option]*self.OptionPosition[option][-1]
            				else:
                				self.OptionPosition[option].append(0)
                				#deltaPortfolioOneDay=deltaPortfolioOneDay+self.data.delta_sheet_.loc[date,option]*self.OptionPosition[option][-1]
        			else:
        		    		self.OptionPosition[option].append(0)    
    			self.deltaPortfolio.append(deltaPortfolioOneDay)
			self.WWdeltaSup.append(WWdeltaSupOneDay)
			self.WWdeltaInf.append(WWdeltaInfOneDay)
			self.WWdeltaHold.append(WWdeltaHoldOneDay)

			self.gammaPortfolio.append(gammaPortfolioOneDay)
			self.vegaPortfolio.append(vegaPortfolioOneDay)
			self.thetaPortfolio.append(thetaPortfolioOneDay)


	def MarginAccount(self):
		self.Position_=pd.DataFrame(self.OptionPosition,index=self.BackTestInterval,columns=self.data.option_names)
		self.MarginAccountSum=[]
		self.ETFMarginAccountSum=[]
		for i in self.BackTestInterval:
			optionpool=self.data.delta_sheet_.loc[i].dropna().index
			self.MarginAccountForOneday=0
			self.ETFMarginAccountForOneday=0
			for j in self.Position_.columns:
				if j in optionpool:
					if self.Position_.loc[i,j]<0:
						self.MarginAccountForOneday=self.MarginAccountForOneday+self.data.MarginAccount_sheet_.loc[i,j]*self.Position_.loc[i,j]
					else:
						if self.data.delta_sheet_.loc[i,j]>0:		
							self.ETFMarginAccountForOneday=self.ETFMarginAccountForOneday+self.data.delta_sheet_.loc[i,j]*self.Position_.loc[i,j]*self.underlying.loc[i,'spot']*self.data.ContractUnit_sheet_.loc[i,j]*0.4
						else:
							pass
				else:
					pass
			self.MarginAccountSum.append(self.MarginAccountForOneday)
			self.ETFMarginAccountSum.append(self.ETFMarginAccountForOneday)
		self.MarginAccountSum_=pd.DataFrame(self.MarginAccountSum,index=self.BackTestInterval,columns=['MarginAccount'])
		self.ETFMarginAccountSum_=pd.DataFrame(self.ETFMarginAccountSum,index=self.BackTestInterval,columns=['ETFMarginAccount'])

		self.MarginAccount_=self.MarginAccountSum_.diff(1)
		self.MarginAccount_.iloc[0]=self.MarginAccountSum_.iloc[0]
		
		self.ETFMarginAccount_=self.ETFMarginAccountSum_.diff(1)
		self.ETFMarginAccount_.iloc[0]=self.ETFMarginAccountSum_.iloc[0]
#卖买标的		

	def DeltaPortfolio(self):        
		self.deltaPortfolio_=pd.DataFrame(self.deltaPortfolio,index=self.BackTestInterval,columns=['delta'])
		self.WWdeltaSup_=pd.DataFrame(self.WWdeltaSup,index=self.BackTestInterval,columns=['delta'])
		self.WWdeltaInf_=pd.DataFrame(self.WWdeltaInf,index=self.BackTestInterval,columns=['delta'])
		self.WWdeltaHold_=pd.DataFrame(self.WWdeltaHold,index=self.BackTestInterval,columns=['delta'])
		
		self.gammaPortfolio_=pd.DataFrame(self.gammaPortfolio,index=self.BackTestInterval,columns=['gamma'])
		self.vegaPortfolio_=pd.DataFrame(self.vegaPortfolio,index=self.BackTestInterval,columns=['vega'])
		self.thetaPortfolio_=pd.DataFrame(self.thetaPortfolio,index=self.BackTestInterval,columns=['theta'])
		self.deltaPortfolioDiff_=self.deltaPortfolio_.diff(1)
		self.deltaPortfolioDiff_.iloc[0]=self.deltaPortfolio_.iloc[0]

		self.gammaPortfolioDiff_=self.gammaPortfolio_.diff(1)
		self.gammaPortfolioDiff_.iloc[0]=self.gammaPortfolio_.iloc[0]
	
		self.vegaPortfolioDiff_=self.vegaPortfolio_.diff(1)
		self.vegaPortfolioDiff_.iloc[0]=self.vegaPortfolio_.iloc[0]
	
		self.thetaPortfolioDiff_=self.thetaPortfolio_.diff(1)
		self.thetaPortfolioDiff_.iloc[0]=self.thetaPortfolio_.iloc[0]
		
		self.WWdeltaSupDiff_=self.WWdeltaSup_.diff(1)
		self.WWdeltaSupDiff_.iloc[0]=self.WWdeltaSup_.iloc[0]
		
		self.WWdeltaInfDiff_=self.WWdeltaInf_.diff(1)
		self.WWdeltaInfDiff_.iloc[0]=self.WWdeltaInf_.iloc[0]

		self.WWdeltaHoldDiff_=self.WWdeltaHold_.diff(1)
		self.WWdeltaHoldDiff_.iloc[0]=self.WWdeltaHold_.iloc[0]

		#标的每日盈亏情况 (不算手续费)
		self.PositionDiff_=self.Position_.diff(1)
		self.PositionDiff_.iloc[0]=self.Position_.iloc[0]#########
		self.ProfitLoss50ETF=[]
		for i in self.Position_.index:
			optionpool=self.data.delta_sheet_.loc[i].dropna().index
			profit50ETFForOneday=0
			for j in self.Position_.columns:
				if j in optionpool:
					profit50ETFForOneday+=self.PositionDiff_.loc[i,j]*self.underlying.loc[i,'spot']*self.data.ContractUnit_sheet_.loc[i,j]
				else:
					pass
			self.ProfitLoss50ETF.append(profit50ETFForOneday)
		
		self.WWProfitLoss50ETF=[a*b*10000 for a,b in zip(self.WWdeltaHoldDiff_['delta'],self.underlying['spot'])]

		self.WWProfitLoss50ETFCost=[]
		self.ProfitLoss50ETFCost=[]
		for i in self.ProfitLoss50ETF:
    			if i>0:
				if i*self.costrate<5:
					temp=i-5
				else:
        				temp=i*(1-self.costrate)
    			else:	
				if abs(i*self.costrate)<5:
					temp=i-5
				else:
        				temp=i*(1+self.costrate)
    			self.ProfitLoss50ETFCost.append(temp)

		for i in self.WWProfitLoss50ETF:
    			if i>0:
				if i*self.costrate<5:
					temp=i-5
				else:
        				temp=i*(1-self.costrate)
    			else:	
				if abs(i*self.costrate)<5:
					temp=i-5
				else:
        				temp=i*(1+self.costrate)
    			self.WWProfitLoss50ETFCost.append(temp)
		
		self.ProfitLoss50ETF_=pd.DataFrame(self.ProfitLoss50ETF,index=self.BackTestInterval,columns=['P/L_Cost'])
		self.WWProfitLoss50ETF_=pd.DataFrame(self.WWProfitLoss50ETF,index=self.BackTestInterval,columns=['P/L_Cost'])
		#标的每日盈亏(加上手续费)
		self.ProfitLoss50ETFCost_=pd.DataFrame(self.ProfitLoss50ETFCost,index=self.BackTestInterval,columns=['P/L_Cost'])
		self.WWProfitLoss50ETFCost_=pd.DataFrame(self.WWProfitLoss50ETFCost,index=self.BackTestInterval,columns=['P/L_Cost'])
		
		#标的整个回测区间的盈亏(包含手续费)
		self.ProfitLoss50ETFCostSum_=self.ProfitLoss50ETFCost_.cumsum()
		self.WWProfitLoss50ETFCostSum_=self.WWProfitLoss50ETFCost_.cumsum()
	
		#标的每日的手续费
		Cost50ETFDaily=[a-b for a,b in zip(self.ProfitLoss50ETF_['P/L_Cost'],self.ProfitLoss50ETFCost_['P/L_Cost'])]
		self.Cost50ETFDaily_=pd.DataFrame(Cost50ETFDaily,index=self.BackTestInterval,columns=['P/L_Cost'])
		WWCost50ETFDaily=[a-b for a,b in zip(self.WWProfitLoss50ETF_['P/L_Cost'],self.WWProfitLoss50ETFCost_['P/L_Cost'])]
		self.WWCost50ETFDaily_=pd.DataFrame(WWCost50ETFDaily,index=self.BackTestInterval,columns=['P/L_Cost'])
		#标的累计的手续费
		self.Cost50ETFDailyCum_=self.Cost50ETFDaily_.cumsum()
		self.WWCost50ETFDailyCum_=self.WWCost50ETFDaily_.cumsum()
		#整个回测区间标的总的手续费=self.Cost50ETFDailyCum_['P/L_Cost'][-1]
		self.GrossCost50ETF=self.ProfitLoss50ETF_.sum().values-self.ProfitLoss50ETFCost_.sum().values
		self.WWGrossCost50ETF=self.WWProfitLoss50ETF_.sum().values-self.WWProfitLoss50ETFCost_.sum().values
	#买卖期权
	def OptionETFTrade(self):
		#期权每日变化的头寸
		self.PositionDiff_=self.Position_.diff(1)
		self.PositionDiff_.iloc[0]=self.Position_.iloc[0]
		
		#期权每日交易的净盈亏
		self.ProfitLossOption=[]
		self.ProfitLossOptionCost=[]
		
		#期权每日交易量的头寸
		self.OptionTradeBuyVolume=[]
		self.OptionTradeSellVolume=[]

		for i in self.PositionDiff_.index:
			optionpool=self.data.delta_sheet_.loc[i].dropna().index
    			ProfitLossOptionForOneday=0
    			ProfitLossOptionForOnedayCost=0
			OptionTradeVolumeBuyForOneday=0
			OptionTradeVolumeSellForOneday=0
    			for j in self.PositionDiff_.columns:
				if j in optionpool:
        				ProfitLossOptionForOneday=ProfitLossOptionForOneday+(-self.PositionDiff_.loc[i,j]*self.data.mktprice_sheet_.fillna(0).loc[i,j]*self.data.ContractUnit_sheet_.loc[i,j])
            				temp=-self.PositionDiff_.loc[i,j]*self.data.mktprice_sheet_.fillna(0).loc[i,j]*self.data.ContractUnit_sheet_.loc[i,j]-self.PositionDiff_.loc[i,j]*(1.3+0.3+10)
        				ProfitLossOptionForOnedayCost=ProfitLossOptionForOnedayCost+temp
					#期权每日的交易量(+买-卖)
					if self.PositionDiff_.loc[i,j]>0:
						OptionTradeVolumeBuyForOneday+=(self.PositionDiff_.loc[i,j])
					else:
						OptionTradeVolumeSellForOneday+=self.PositionDiff_.loc[i,j]
				else:
					pass
    			self.ProfitLossOption.append(ProfitLossOptionForOneday)
    			self.ProfitLossOptionCost.append(ProfitLossOptionForOnedayCost)

			self.OptionTradeBuyVolume.append(OptionTradeVolumeBuyForOneday)
			self.OptionTradeSellVolume.append(OptionTradeVolumeSellForOneday)
		#净盈亏(无手续费)
		self.ProfitLossOption_=pd.DataFrame(self.ProfitLossOption,index=self.BackTestInterval,columns=['P/L_Cost'])
		self.OptionTradeBuyVolume_=pd.DataFrame(self.OptionTradeBuyVolume,index=self.BackTestInterval,columns=['TradeVolume'])

		self.OptionTradeSellVolume_=pd.DataFrame(self.OptionTradeSellVolume,index=self.BackTestInterval,columns=['TradeVolume'])

		#净盈亏(包含手续费)
		self.ProfitLossOptionCost_=pd.DataFrame(self.ProfitLossOptionCost,index=self.BackTestInterval,columns=['P/L_Cost'])

		#整个回测区间期权交易总的净盈亏(包含手续费)
		self.ProfitLossOptionCostSum_=self.ProfitLossOptionCost_.cumsum()
		
		#期权交易每日的手续费
		CostOptionDaily=[a-b for a,b in zip(self.ProfitLossOption_['P/L_Cost'],self.ProfitLossOptionCost_['P/L_Cost'])]
		self.CostOptionDaily_=abs(pd.DataFrame(CostOptionDaily,index=self.BackTestInterval,columns=['P/L_Cost']))
		#期权累积的手续费
		self.CostOptionDailyCum_=self.CostOptionDaily_.cumsum()
		#整个回测区间期权交易总的手续费
		self.GrossCostOption=self.CostOptionDailyCum_['P/L_Cost'][-1]
		
		#整个回测区间总的手续费(option+ETF)
		self.GrossCost=self.GrossCost50ETF+self.GrossCostOption
		self.WWGrossCost=self.WWGrossCost50ETF+self.GrossCostOption


	#持有期权每日的内在价值
	def OptionValue(self):
		self.OptionValueSum=[]
		for i in self.Position_.index:
			optionpool=self.data.delta_sheet_.loc[i].dropna().index
    			OptionValueOneday=0
    			for j in self.Position_.columns:
				if j in optionpool:
					if j[-1]=='A':
						strike=float(j[-6:-1])
						contractUnit=10220
					else:
        					strike=float(j[-4:])
						contractUnit=10000
        				if j[5]==u'购':
            					temp=max(self.underlying.loc[i,'spot']-strike,0)*self.Position_.loc[i,j]*self.data.ContractUnit_sheet_.loc[i,j]
        				else:
            					temp=max(strike-self.underlying.loc[i,'spot'],0)*self.Position_.loc[i,j]*self.data.ContractUnit_sheet_.loc[i,j]
        				OptionValueOneday+=temp
				else:
					pass
    			self.OptionValueSum.append(OptionValueOneday)
		self.OptionValueSum_=pd.DataFrame(self.OptionValueSum,index=self.BackTestInterval,columns=['optionvalue'])
		#持有期权价值每日的变化量
		self.OptionValue_=self.OptionValueSum_.diff(1)
		self.OptionValue_.iloc[0]=self.OptionValueSum_.iloc[0]
	
	#卖出标的的价值(所借标的 的价值)
	def ShortValue(self):
		self.shortPositionValueSum=[]
		for i in self.Position_.index:
			optionpool=self.data.delta_sheet_.loc[i].dropna().index
			shortPositionForOneday=0
			for j in self.Position_.columns:
				if j in optionpool:
					shortPositionForOneday+=-self.underlying.loc[i,'spot']*self.data.delta_sheet_.loc[i,j]*self.data.ContractUnit_sheet_.loc[i,j]
				else:
					pass
			self.shortPositionValueSum.append(shortPositionForOneday)
		#self.shortPositionValueSum=[-a*b*10000 for a,b in zip(self.underlying['spot'],self.deltaPortfolio_['delta'])]
		self.shortPositionValueSum_=pd.DataFrame(self.shortPositionValueSum,index=self.BackTestInterval,columns=['shortPosition'])

		self.WWshortPositionValueSum=[-a*b*10000 for a,b in zip(self.underlying['spot'],self.WWdeltaHold_['delta'])]
		self.WWshortPositionValueSum_=pd.DataFrame(self.WWshortPositionValueSum,index=self.BackTestInterval,columns=['shortPosition'])
		#卖出标的价值每日的变化量
		self.shortPositionValue_=self.shortPositionValueSum_.diff(1)
		self.shortPositionValue_.iloc[0]=self.shortPositionValueSum_.iloc[0]

		self.WWshortPositionValue_=self.WWshortPositionValueSum_.diff(1)
		self.WWshortPositionValue_.iloc[0]=self.WWshortPositionValueSum_.iloc[0]
	def OptionValueOptionTrade(self):
		option_value_trade=[a+b for a,b in zip(self.OptionValue_['optionvalue'],self.ProfitLossOptionCost_['P/L_Cost'])]
		self.option_value_trade_=pd.DataFrame(option_value_trade,index=self.BackTestInterval,columns=['P/L_Cost'])
		self.option_value_trade_sum_=self.option_value_trade_.cumsum()	

	def ETFValueETFTrade(self):
		ETF_value_trade=[a+b for a,b in zip(self.shortPositionValue_['shortPosition'],self.ProfitLoss50ETFCost_['P/L_Cost'])]
		self.ETF_value_trade_=pd.DataFrame(ETF_value_trade,index=self.BackTestInterval,columns=['P/L_Cost'])
		self.ETF_value_trade_sum_=self.ETF_value_trade_.cumsum()
	#总资产
	def TotalAsset(self):
		self.AssetSum=[a+b+c+d+self.capital for a,b,c,d in zip(self.ProfitLossOptionCostSum_['P/L_Cost'],self.ProfitLoss50ETFCostSum_['P/L_Cost'],self.OptionValueSum_['optionvalue'],self.shortPositionValueSum_['shortPosition'])]
		self.WWAssetSum=[a+b+c+d+self.capital for a,b,c,d in zip(self.ProfitLossOptionCostSum_['P/L_Cost'],self.WWProfitLoss50ETFCostSum_['P/L_Cost'],self.OptionValueSum_['optionvalue'],self.shortPositionValueSum_['shortPosition'])]

		#期权,标的交易  期权实值  借标的需还的 
		self.AssetSum_=pd.DataFrame(self.AssetSum,index=self.BackTestInterval,columns=['Asset'])
		self.WWAssetSum_=pd.DataFrame(self.WWAssetSum,index=self.BackTestInterval,columns=['Asset'])
		#总资产每日的变化量
		
		
		self.Asset_=self.AssetSum_.diff(1)
		self.Asset_.iloc[0]=self.AssetSum_.iloc[0]
	#持有流动现金 
	def _CashInHand(self):
		self.CashInHandSum=[]
		self.WWCashInHandSum=[]
		for k,i in enumerate(self.Position_.index):
			optionpool=self.data.delta_sheet_.loc[i].dropna().index
			cashinhand=0
			WWcashinhand=0
			for j in self.Position_.columns:
				if j in optionpool:
					#期权费+手续费  对冲成本+手续费  保证金
					premium=-self.Position_.loc[i,j]*self.data.mktprice_sheet_.fillna(0).loc[i,j]*self.data.ContractUnit_sheet_.loc[i,j]-self.CostOptionDailyCum_['P/L_Cost'][k]
					temp1=self.data.delta_sheet_.loc[i,j]*self.Position_.loc[i,j]*self.underlying.loc[i,'spot']*self.data.ContractUnit_sheet_.loc[i,j]
					temp2=self.data.WWDeltaHold_sheet_.loc[i,j]*self.Position_.loc[i,j]*self.underlying.loc[i,'spot']*self.data.ContractUnit_sheet_.loc[i,j]
					ETFTrade=temp1-self.Cost50ETFDailyCum_['P/L_Cost'][k]
					WWETFTrade=temp2-self.WWCost50ETFDailyCum_['P/L_Cost'][k]
					#当买看涨期权或卖看跌期权进行对冲时,需借入标的卖出,因此要交ETF保证金.
					#卖期权时,都要交期权的保证金
					if self.Position_.loc[i,j]>0:
						if self.data.delta_sheet_.loc[i,j]>0:
							ETFMarginAccount=-self.data.delta_sheet_.loc[i,j]*self.Position_.loc[i,j]*self.underlying.loc[i,'spot']*self.data.ContractUnit_sheet_.loc[i,j]*0.4###卖空保证金为当时ETF市场价值的40%
						else:
							ETFMarginAccount=0
						MarginAccount=0
					else:
						if self.data.delta_sheet_.loc[i,j]<0:
							ETFMarginAccount=-self.data.delta_sheet_.loc[i,j]*self.Position_.loc[i,j]*self.underlying.loc[i,'spot']*self.data.ContractUnit_sheet_.loc[i,j]*0.4
						else:
							ETFMarginAccount=0
						MarginAccount=self.data.MarginAccount_sheet_.loc[i,j]*self.Position_.loc[i,j]
					cashinhand=cashinhand+premium+ETFTrade+ETFMarginAccount+MarginAccount
					WWcashinhand=WWcashinhand+premium+WWETFTrade+MarginAccount
				else:
					pass
			self.CashInHandSum.append(cashinhand)
			self.WWCashInHandSum.append(WWcashinhand)
		
		self.CashInHandSum_=pd.DataFrame(self.CashInHandSum,index=self.BackTestInterval,columns=['cashinhand'])+self.capital
		self.WWCashInHandSum_=pd.DataFrame(self.WWCashInHandSum,index=self.BackTestInterval,columns=['cashinhand'])+self.capital
		
		self.CashInHand_=self.CashInHandSum_.diff(1)
		self.CashInHand_.iloc[0]=self.CashInHandSum_.iloc[0]
	
		self.WWCashInHand_=self.WWCashInHandSum_.diff(1)
		self.WWCashInHand_.iloc[0]=self.WWCashInHandSum_.iloc[0]		
		
	
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
		self.yield_rate=[a/self.capital-1 for a in self.AssetSum_['Asset']]
		self.WWyield_rate=[a/self.capital-1 for a in self.WWAssetSum_['Asset']]	
	
		self.yield_rate_=pd.DataFrame(self.yield_rate,index=self.BackTestInterval,columns=['yield_rate'])
		self.WWyield_rate_=pd.DataFrame(self.WWyield_rate,index=self.BackTestInterval,columns=['yield_rate'])
		#年化收益率
		self.yield_rate_to_year=[(a/self.capital-1)/(i+1)*252 for i,a in enumerate(self.AssetSum_['Asset'])]
		self.WWyield_rate_to_year=[(a/self.capital-1)/(i+1)*252 for i,a in enumerate(self.WWAssetSum_['Asset'])]

		self.yield_rate_to_year_=pd.DataFrame(self.yield_rate_to_year,index=self.BackTestInterval,columns=['yield_rate'])
		self.WWyield_rate_to_year_=pd.DataFrame(self.WWyield_rate_to_year,index=self.BackTestInterval,columns=['yield_rate'])
		
	def MaxDrawback(self):
		self.maxdrawback=[]
		self.AssetSum_.iloc[0]=self.capital
		for i,d in enumerate(self.AssetSum_['Asset']):
    			temp=self.AssetSum_[:i+1].rolling(window=i+1,center=False).max().iloc[-1].values
    			self.maxdrawback.append((d-temp)/temp)
		self.maxdrawback_=pd.DataFrame(self.maxdrawback,index=self.BackTestInterval,columns=['drawback'])
		self.MaxDrawback=np.min(self.maxdrawback_).values


		self.WWmaxdrawback=[]
		self.WWAssetSum_.iloc[0]=self.capital
		for i,d in enumerate(self.WWAssetSum_['Asset']):
    			temp=self.WWAssetSum_[:i+1].rolling(window=i+1,center=False).max().iloc[-1].values
    			self.WWmaxdrawback.append((d-temp)/temp)
		self.WWmaxdrawback_=pd.DataFrame(self.WWmaxdrawback,index=self.BackTestInterval,columns=['drawback'])
		self.WWMaxDrawback=np.min(self.WWmaxdrawback_).values


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



		self.WWmaxdrawback_num=[]
		for i,d in enumerate(self.WWAssetSum_['Asset']):
    			if i<=num-1:
        			temp=self.WWAssetSum_[:i+1].rolling(window=i+1,center=False).max().iloc[-1].values
        			self.WWmaxdrawback_num.append((d-temp)/temp)
    			else:
        			temp=self.WWAssetSum_[i-num+1:i+1].rolling(window=num,center=False).max().iloc[-1].values
        			self.WWmaxdrawback_num.append((d-temp)/temp)
		self.WWmaxdrawback_num_=pd.DataFrame(self.WWmaxdrawback_num,index=self.BackTestInterval,columns=['drawback'])
		self.WWMaxDrawback_num=np.min(self.WWmaxdrawback_num_).values


	def StrategyImport(self,date):
		SI=[]
		
		for option in self.data.option_names:
			if self.data.impliedVolatility_sheet_.loc[date,option]>self.realizedVolatility.realizedVol.loc[date,'realizedVol_10']:
				temp=0.99*self.capital/80/(self.data.mktprice_sheet_.loc[date,option]*self.data.ContractUnit_sheet_.loc[date,option])
				temp=int(temp)
				SI.append(self.order_target(option,temp))
		
		#SI.append(self.order_target(self.data.option_names[4],1))
		return SI



























