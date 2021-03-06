#encoding=utf-8



import sys
import matplotlib
import pandas as pd
import numpy as np
import re
matplotlib.use("Qt5Agg")
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import seaborn as sns
from QuantLib import *
import BTdata as Bd


class BackTest(QWidget):
	def __init__(self):
		super(BackTest,self).__init__()
		
		self.CreateLabel()
		self.CreateEdit()
		self.CreateCombo()
		self.CreateImage()
		self.CreateButton()
		self.comboBoxAct()
		self.EditChange()
		self.StartDate='20170301'
		self.EndDate='20170418'
		self.Capital=1000000
		self.CostRate=0.0025		
		
		self.initUI()
	def CreateLabel(self):
		self.lblStartDate=QLabel('起始日期',self)
		self.lblEndDate=QLabel('结束日期',self)
		self.lblCapitalAccount=QLabel('资金',self)
		self.lblCostRate=QLabel('佣金费率',self)
		self.lblYieldRate=QLabel('回测收益',self)
		self.lblYieldRateForYear=QLabel('年化收益',self)
		self.lblMaxDrawback=QLabel('最大回撤',self)
		self.lblOptionCost=QLabel('期权交易费用',self)
		self.lblETFCost=QLabel('对冲交易费用',self)
		self.lblOptionETFCost=QLabel('总交易费用',self)
	def CreateButton(self):
		self.btnRun=QPushButton('运行',self)
		
		self.btnRun.clicked.connect(self.run)
		
		self.btnDetails=QPushButton('details',self)
		self.btnDetails.clicked.connect(self.Details)
	def CreateEdit(self):
		self.CapitalAccountEdit=QLineEdit(self)
		self.CostRateEdit=QLineEdit(self)
		self.YieldRateEdit=QLabel('',self)
		self.YieldRateForYearEdit=QLabel('',self)
		self.MaxDrawbackEdit=QLabel('',self)

		self.OptionCostEdit=QLabel('',self)
		self.ETFCostEdit=QLabel('',self)
		self.OptionETFCostEdit=QLabel('',self)

	def CreateCombo(self):
		self.comboStartYear=QComboBox(self)
		self.comboEndYear=QComboBox(self)
		self.comboStartYear.addItem('')
		self.comboEndYear.addItem('')
		for i in range(2015,2018):
			self.comboStartYear.addItem(str(i))
			self.comboEndYear.addItem(str(i))
		
		self.comboStartMonth=QComboBox(self)
		self.comboEndMonth=QComboBox(self)
		self.comboStartMonth.addItem('')
		self.comboEndMonth.addItem('')
		for i in range(1,13):
			if len(str(i))==1:
				self.comboStartMonth.addItem(str(0)+str(i))
				self.comboEndMonth.addItem(str(0)+str(i))
			else:
				self.comboStartMonth.addItem(str(i))
				self.comboEndMonth.addItem(str(i))
		self.comboStartDay=QComboBox(self)
		self.comboEndDay=QComboBox(self)
		self.comboStartDay.addItem('')
		self.comboEndDay.addItem('')
		for i in range(1,32):
			if len(str(i))==1:
				self.comboStartDay.addItem(str(0)+str(i))
				self.comboEndDay.addItem(str(0)+str(i))
			else:
				self.comboStartDay.addItem(str(i))
				self.comboEndDay.addItem(str(i))
	
	def comboBoxAct(self):
		self.comboStartYear.activated[str].connect(self.onActivatedStartYear)
		self.comboStartMonth.activated[str].connect(self.onActivatedStartMonth)
		self.comboStartDay.activated[str].connect(self.onActivatedStartDay)
		
		self.comboEndYear.activated[str].connect(self.onActivatedEndYear)
		self.comboEndMonth.activated[str].connect(self.onActivatedEndMonth)
		self.comboEndDay.activated[str].connect(self.onActivatedEndDay)
	def CreateImage(self):
		self.figureBT=plt.figure()
		self.axesBT=plt.figure()
		plt.xlabel('date')
		plt.ylabel(u'累计收益')
		self.axesBT=self.figureBT.add_subplot(111)
		self.axesBT.hold(False)
		self.canvasBT=FigureCanvas(self.figureBT)
	def EditChange(self):
		self.CapitalAccountEdit.textChanged[str].connect(self.CapitalAccountOnChanged)
		self.CostRateEdit.textChanged[str].connect(self.CostRateOnChanged)
	def initUI(self):
		hboxStartDate=QHBoxLayout()
		hboxStartDate.addWidget(self.comboStartYear)
		hboxStartDate.addWidget(self.comboStartMonth)
		hboxStartDate.addWidget(self.comboStartDay)

		hboxEndDate=QHBoxLayout()
		hboxEndDate.addWidget(self.comboEndYear)
		hboxEndDate.addWidget(self.comboEndMonth)
		hboxEndDate.addWidget(self.comboEndDay)

		grid=QGridLayout()
		grid.addWidget(self.lblStartDate,0,0)
		grid.addLayout(hboxStartDate,0,1)
		grid.addWidget(self.lblEndDate,0,2)
		grid.addLayout(hboxEndDate,0,3)
		grid.addWidget(self.lblCapitalAccount,0,4)
		grid.addWidget(self.CapitalAccountEdit,0,5)
		grid.addWidget(self.lblCostRate,0,6)
		grid.addWidget(self.CostRateEdit,0,7)

		grid.addWidget(self.lblYieldRate,1,0)
		grid.addWidget(self.YieldRateEdit,1,1)
		grid.addWidget(self.lblYieldRateForYear,1,2)
		grid.addWidget(self.YieldRateForYearEdit,1,3)
		grid.addWidget(self.lblMaxDrawback,1,4)
		grid.addWidget(self.MaxDrawbackEdit,1,5)
		grid.addWidget(self.lblOptionCost,2,0)
		grid.addWidget(self.OptionCostEdit,2,1)
		grid.addWidget(self.lblETFCost,2,2)
		grid.addWidget(self.ETFCostEdit,2,3)
		grid.addWidget(self.lblOptionETFCost,2,4)
		grid.addWidget(self.OptionETFCostEdit,2,5)
		grid.addWidget(self.btnRun,1,7)
		
		grid.addWidget(self.btnDetails,2,7)	
		vbox=QVBoxLayout()
		vbox.addLayout(grid)
		vbox.addWidget(self.canvasBT)
		
		self.setLayout(vbox)
		self.show()
		self.setWindowTitle('BackTest')
		self.setGeometry(300,300,900,700)
	def onActivatedStartYear(self,StartYear):
		self.StartYear=StartYear
		self.StartDate=self.StartYear+self.StartDate[-4:]
	def onActivatedStartMonth(self,StartMonth):
		self.StartMonth=StartMonth
		self.StartDate=self.StartDate[:4]+self.StartMonth+self.StartDate[-2:]
	def onActivatedStartDay(self,StartDay):
		self.StartDay=StartDay
		self.StartDate=self.StartDate[:6]+self.StartDay

	def onActivatedEndYear(self,EndYear):
		self.EndYear=EndYear
		self.EndDate=self.EndYear+self.EndDate[-4:]
	def onActivatedEndMonth(self,EndMonth):
		self.EndMonth=EndMonth
		self.EndDate=self.EndDate[:4]+self.EndMonth+self.EndDate[-2:]
	def onActivatedEndDay(self,EndDay):
		self.EndDay=EndDay
		self.EndDate=self.EndDate[:6]+self.EndDay
	
	def CapitalAccountOnChanged(self,capital):
		self.Capital=capital
	def CostRateOnChanged(self,costrate):
		self.CostRate=costrate 

	
	def run(self):
		self.Capital=float(self.Capital)
		self.CostRate=float(self.CostRate)
		self.StartDate=self.StartDate[:4]+'-'+self.StartDate[4:6]+'-'+self.StartDate[6:8]
		self.EndDate=self.EndDate[:4]+'-'+self.EndDate[4:6]+'-'+self.EndDate[6:8]
		self.data=Bd.BackTestData(self.StartDate,self.EndDate,self.Capital,self.CostRate)
		self.Details=Details(self.data)
		self.YieldRatePlot()
		self.setText()
	def Analysis(self):
		#self.optionAnalysis
		self.optionAnalysis.show()
	def Details(self):
		self.Details.show()
		
	def setText(self):
		self.YieldRateEdit.setText(str(round(self.data.yield_rate_.values[-1][0],4)*100)+'%')
		self.YieldRateForYearEdit.setText(str(round(self.data.yield_rate_to_year_.values[-1][0],4)*100)+'%')
		self.MaxDrawbackEdit.setText(str(round(self.data.MaxDrawback[0],4)*100)+'%')
		self.OptionCostEdit.setText(str(round(self.data.GrossCostOption,2)))
		self.ETFCostEdit.setText(str(round(self.data.GrossCost50ETF,2)))
		self.OptionETFCostEdit.setText(str(round(self.data.GrossCost,2)))
	
	def WWsetText(self):
		self.YieldRateEdit.setText(str(round(self.data.WWyield_rate_.values[-1][0],4)*100)+'%')
		self.YieldRateForYearEdit.setText(str(round(self.data.WWyield_rate_to_year_.values[-1][0],4)*100)+'%')
		self.MaxDrawbackEdit.setText(str(round(self.data.WWMaxDrawback[0],4)*100)+'%')
		self.OptionCostEdit.setText(str(round(self.data.GrossCostOption,2)))
		self.ETFCostEdit.setText(str(round(self.data.WWGrossCost50ETF,2)))
		self.OptionETFCostEdit.setText(str(round(self.data.WWGrossCost,2)))
	
		
	#收益率
	def YieldRatePlot(self):
		t=self.data.BackTestInterval
		s=self.data.yield_rate_['yield_rate']
		#s_ww=self.data.WWyield_rate_['yield_rate']
		s_u=self.data.realizedVolatility.underlyingYieldRate[t[0]:t[-1]]['spot']
		self.axesBT.plot(t,s,label=r'yield_rate')
		self.axesBT.hold(True)
		#self.axesBT.plot(t,s_ww,label=r'WWyield_rate')
		self.axesBT.plot(t,s_u,label=r'underlying')
		self.axesBT.legend(loc=2)
		self.axesBT.hold(False)
		self.canvasBT.draw()
	

class optionAnalysis(QWidget):
	def __init__(self,data):
		super(optionAnalysis,self).__init__()
		self.data=data
		self.CreateImage()
		self.CreateComboBox()
		self.CreateCheckBox()
		self.comboBoxAct()
		self.initUI()
		self.Transit='day'

	def CreateImage(self):
		self.figure1=plt.figure()
		self.axesShortValue=self.figure1.add_subplot(322)
		self.axesOptionValue=self.figure1.add_subplot(321)
		self.axesOptionTrade=self.figure1.add_subplot(323)
		self.axesETFTrade=self.figure1.add_subplot(324)
		self.axesOption=self.figure1.add_subplot(325)
		self.axesETF=self.figure1.add_subplot(326)
		self.canvas1=FigureCanvas(self.figure1)
		self.axesShortValue.hold(False)
		self.axesOptionValue.hold(False)
		self.axesOptionTrade.hold(False)
		self.axesETFTrade.hold(False)
		self.axesOption.hold(False)
		self.axesETF.hold(False)

		self.figure2=plt.figure()	
		
		self.axesMarginAccount=self.figure2.add_subplot(211)
		self.axesCash=self.figure2.add_subplot(212)
		self.canvas2=FigureCanvas(self.figure2)
		
		self.axesMarginAccount.hold(False)
		self.axesCash.hold(False)
		self.canvas2.hide()	
			
		self.figure3=plt.figure()
		self.axesdelta=self.figure3.add_subplot(221)
		self.axesgamma=self.figure3.add_subplot(222)
		self.axesvega=self.figure3.add_subplot(223)
		self.axestheta=self.figure3.add_subplot(224)
		self.axesdelta.hold(False)
		self.axesgamma.hold(False)
		self.axesvega.hold(False)
		self.axestheta.hold(False)
		self.canvas3=FigureCanvas(self.figure3)
		self.canvas3.hide()
	def CreateCheckBox(self):
		self.cb=QCheckBox()
		self.cb.stateChanged.connect(self.changeAxes)
	def CreateComboBox(self):
		self.combofigure=QComboBox()
		self.combofigure.addItem('')
		self.combofigure.addItem('&figure1')
		self.combofigure.addItem('&figure2')
		self.combofigure.addItem('&figure3')
		
		self.comboyield=QComboBox()
		self.comboyield.addItem('')
		self.comboyield.addItem('每日')
		self.comboyield.addItem('累计')
	
	def initUI(self):
				
		hbox=QHBoxLayout()
		hbox.addWidget(self.combofigure)
		hbox.addWidget(self.comboyield)
		hbox.addWidget(self.cb)
		hbox.addStretch()
		vbox=QVBoxLayout()
		vbox.addLayout(hbox)
		vbox.addWidget(self.canvas1)
		vbox.addWidget(self.canvas2)
		vbox.addWidget(self.canvas3)
		self.setLayout(vbox)
		
		self.setGeometry(300,300,900,700)
		self.setWindowTitle('Analysis')
	def comboBoxAct(self):
		self.combofigure.activated[str].connect(self.onActivatedfigure)
		self.comboyield.activated[str].connect(self.onActivatedyield)
	def changeAxes(self,state):
		if state==Qt.Checked:
			self.axesShortValue.hold(True)
			self.axesOptionValue.hold(True)
			self.axesOptionTrade.hold(True)
			self.axesETFTrade.hold(True)
			self.axesOption.hold(True)
			self.axesETF.hold(True)
			
			self.axesMarginAccount.hold(True)
			self.axesCash.hold(True)
			self.axesdelta.hold(True)
			self.axesgamma.hold(True)
			self.axesvega.hold(True)
			self.axestheta.hold(True)
		else:
			
			self.axesShortValue.hold(False)
			self.axesOptionValue.hold(False)
			self.axesOptionTrade.hold(False)
			self.axesETFTrade.hold(False)
			self.axesOption.hold(False)
			self.axesETF.hold(False)			

			self.axesMarginAccount.hold(False)
			self.axesCash.hold(False)
			self.axesdelta.hold(False)
			self.axesgamma.hold(False)
			self.axesvega.hold(False)
			self.axestheta.hold(False)
	def onActivatedfigure(self,txt):
		if txt=='&figure1':
			self.ShortValuePlot()
			self.OptionValuePlot()
			self.OptionTradePlot()
			self.ETFTradePlot()
			self.OptionPlot()
			self.ETFPlot()
			self.canvas1.show()
			self.canvas2.hide()
			self.canvas3.hide()
		elif txt=='&figure2':
			self.MarginAccountPlot()
			self.CashInHandPlot()
			self.canvas2.show()
			self.canvas1.hide()
			self.canvas3.hide()
		elif txt=='&figure3':
			self.deltaPlot()
			self.gammaPlot()
			self.vegaPlot()
			self.thetaPlot()
			self.canvas3.show()
			self.canvas1.hide()
			self.canvas2.hide()
		else:
			pass
		self.figureTransit=txt
	def onActivatedyield(self,txt):
		if txt==u'每日':
			self.Transit='day'
		elif txt==u'累计':
			self.Transit='sum'
		else:
			pass
		
		self.onActivatedfigure(self.figureTransit)

	#标的价值

	def ShortValuePlot(self):
		if self.Transit=='day':
			t=self.data.BackTestInterval
			s=self.data.shortPositionValue_['shortPosition']
			s_ww=self.data.WWshortPositionValue_['shortPosition']
			self.axesShortValue.plot(t,s,label=r'underlyingvalue')
			self.axesShortValue.hold(True)
			self.axesShortValue.plot(t,s_ww,label=r'WWunderlying')
			self.axesShortValue.legend(loc=2)
			self.axesShortValue.hold(False)
			self.canvas1.draw()
		else:
			t=self.data.BackTestInterval
			s=self.data.shortPositionValueSum_['shortPosition']
			s_ww=self.data.WWshortPositionValueSum_['shortPosition']
			self.axesShortValue.plot(t,s,label=r'underlyingvaluesum')
			self.axesShortValue.hold(True)
			self.axesShortValue.plot(t,s_ww,label=r'WWunderlyingsum')
			self.axesShortValue.legend(loc=2)
			self.axesShortValue.hold(False)
			self.canvas1.draw()
	#期权价值
	def OptionValuePlot(self):
		if self.Transit=='day':
			t=self.data.BackTestInterval
			s=self.data.OptionValue_['optionvalue']
			self.axesOptionValue.plot(t,s,label=r'optionvalue')
			self.axesOptionValue.legend(loc=2)
			self.canvas1.draw()
		else:
			t=self.data.BackTestInterval
			s=self.data.OptionValueSum_['optionvalue']
			self.axesOptionValue.plot(t,s,label=r'optionvaluesum')
			self.axesOptionValue.legend(loc=2)
			self.canvas1.draw()
			
	def OptionTradePlot(self):
		if self.Transit=='day':
			t=self.data.BackTestInterval
			s=self.data.ProfitLossOptionCost_['P/L_Cost']
			self.axesOptionTrade.plot(t,s,label=r'optiontrade')
			self.axesOptionTrade.legend(loc=2)
			self.canvas1.draw()
		else:	
			t=self.data.BackTestInterval
			s=self.data.ProfitLossOptionCostSum_['P/L_Cost']
			self.axesOptionTrade.plot(t,s,label=r'optiontradesum')
			self.axesOptionTrade.legend(loc=2)
			self.canvas1.draw()
			
	def ETFTradePlot(self):
		if self.Transit=='day':
			t=self.data.BackTestInterval
			s=self.data.ProfitLoss50ETFCost_['P/L_Cost']
			s_ww=self.data.WWProfitLoss50ETFCost_['P/L_Cost']
			self.axesETFTrade.plot(t,s,label=r'ETFtrade')
			self.axesETFTrade.hold(True)
			self.axesETFTrade.plot(t,s_ww,label=r'WWETFTrade')
			self.axesETFTrade.legend(loc=2)
			self.axesETFTrade.hold(False)
			self.canvas1.draw()
		else:
			t=self.data.BackTestInterval
			s=self.data.ProfitLoss50ETFCostSum_['P/L_Cost']
			s_ww=self.data.WWProfitLoss50ETFCostSum_['P/L_Cost']
			self.axesETFTrade.plot(t,s,label=r'ETFtradesum')
			self.axesETFTrade.hold(True)
			self.axesETFTrade.plot(t,s_ww,label=r'WWETFTradesum')
			self.axesETFTrade.legend(loc=2)
			self.axesETFTrade.hold(False)
			self.canvas1.draw()
	def OptionPlot(self):
		if self.Transit=='day':
			t=self.data.BackTestInterval
			s=self.data.option_value_trade_['P/L_Cost']
			self.axesOption.plot(t,s,label=r'option')
			self.axesOption.legend(loc=2)
			self.canvas1.draw()
		else:
			t=self.data.BackTestInterval
			s=self.data.option_value_trade_sum_['P/L_Cost']
			self.axesOption.plot(t,s,label=r'optionsum')
			self.axesOption.legend(loc=2)
			self.canvas1.draw()
	def ETFPlot(self):
		if self.Transit=='day':
			t=self.data.BackTestInterval
			s=self.data.ETF_value_trade_['P/L_Cost']
			self.axesETF.plot(t,s,label=r'ETF')
			self.axesETF.legend(loc=2)
			self.canvas1.draw()
		else:
			t=self.data.BackTestInterval
			s=self.data.ETF_value_trade_sum_['P/L_Cost']
			self.axesETF.plot(t,s,label=r'ETFsum')
			self.axesETF.legend(loc=2)
			self.canvas1.draw()
	

	def MarginAccountPlot(self):
		if self.Transit=='day':
			t=self.data.BackTestInterval	
			s=self.data.MarginAccount_['MarginAccount']
			self.axesMarginAccount.plot(t,s,label=r'MarginAccount')
			self.axesMarginAccount.legend(loc=2)
			self.canvas2.draw()
		else:
			t=self.data.BackTestInterval
			s=self.data.MarginAccountSum_['MarginAccount']
			self.axesMarginAccount.plot(t,s,label=r'MarginAccountsum')
			self.axesMarginAccount.legend(loc=2)
			self.canvas2.draw()
	def CashInHandPlot(self):
		if self.Transit=='day':
			t=self.data.BackTestInterval
			s=self.data.CashInHand_['cashinhand']
			s_ww=self.data.WWCashInHand_['cashinhand']
			self.axesCash.plot(t,s,label=r'cashinhand')
			self.axesCash.hold(True)
			self.axesCash.plot(t,s_ww,label=r'WWcashinhand')
			self.axesCash.legend(loc=2)
			self.axesCash.hold(False)
			self.canvas2.draw()
		else:
			t=self.data.BackTestInterval
			s=self.data.CashInHandSum_['cashinhand']
			s_ww=self.data.WWCashInHandSum_['cashinhand']
			self.axesCash.plot(t,s,label=r'cashinhandsum')
			self.axesCash.hold(True)
			self.axesCash.plot(t,s_ww,label=r'WWcashinhandsum')
			self.axesCash.legend(loc=2)
			self.axesCash.hold(False)
			self.canvas2.draw()
	


	def deltaPlot(self):
		if self.Transit=='day':
			t=self.data.BackTestInterval
			s=self.data.deltaPortfolioDiff_['delta']
			s_sup=self.data.WWdeltaSupDiff_['delta']
			s_inf=self.data.WWdeltaInfDiff_['delta']
			s_hold=self.data.WWdeltaHoldDiff_['delta']
			self.axesdelta.plot(t,s,label=r'delta')
			self.axesdelta.hold(True)
			self.axesdelta.plot(t,s_inf,label=r'delta_inf')
			self.axesdelta.plot(t,s_sup,label=r'delta_sup')
			self.axesdelta.plot(t,s_hold,label=r'delta_hold')
			self.axesdelta.legend(loc=2)
			self.axesdelta.hold(False)
			self.canvas3.draw()
		else:
			t=self.data.BackTestInterval
			s=self.data.deltaPortfolio_['delta']
			s_sup=self.data.WWdeltaSup_['delta']
			s_inf=self.data.WWdeltaInf_['delta']
			s_hold=self.data.WWdeltaHold_['delta']
			self.axesdelta.plot(t,s,label=r'deltasum')
			self.axesdelta.hold(True)
			self.axesdelta.plot(t,s_inf,label=r'delta_infsum')
			self.axesdelta.plot(t,s_sup,label=r'delta_supsum')
			self.axesdelta.plot(t,s_hold,label=r'delta_holdsum')
			self.axesdelta.legend(loc=2)
			self.axesdelta.hold(False)
			self.canvas3.draw()
			
	def gammaPlot(self):
		if self.Transit=='day':
			t=self.data.BackTestInterval
			s=self.data.gammaPortfolioDiff_['gamma']
			self.axesgamma.plot(t,s)
			self.axesgamma.legend(loc=2)
			self.canvas3.draw()
		else:
			t=self.data.BackTestInterval
			s=self.data.gammaPortfolio_['gamma']
			self.axesgamma.plot(t,s)
			self.axesgamma.legend(loc=2)
			self.canvas3.draw()
	def vegaPlot(self):
		if self.Transit=='day':
			t=self.data.BackTestInterval
			s=self.data.vegaPortfolioDiff_['vega']
			self.axesvega.plot(t,s)
			self.axesvega.legend(loc=2)
			self.canvas3.draw()
		else:
			t=self.data.BackTestInterval
			s=self.data.vegaPortfolio_['vega']
			self.axesvega.plot(t,s)
			self.axesvega.legend(loc=2)
			self.canvas3.draw()
	def thetaPlot(self):
		if self.Transit=='day':
			t=self.data.BackTestInterval
			s=self.data.thetaPortfolioDiff_['theta']
			self.axestheta.plot(t,s)
			self.axestheta.legend(loc=2)
			self.canvas3.draw()
		else:
			t=self.data.BackTestInterval
			s=self.data.thetaPortfolio_['theta']
			self.axestheta.plot(t,s)
			self.axestheta.legend(loc=2)
			self.canvas3.draw()

class Details(QWidget):
	def __init__(self,BTdata):
		super(Details,self).__init__()
		self.BTdata=BTdata
		self.sheetdata=BTdata.data
		self.CreateTablist()
		self.TradeDetail()
		self.DailyPosition()
		self.Account()
		self.Yield()
		self.CreateButton()
		self.ButtonAct()
		
		self.initUI()
	def CreateButton(self):
		self.btnYield=QPushButton('收益概况',self)
		self.btnTradeDetail=QPushButton('交易详情',self)
		self.btnDailyPosition=QPushButton('每日持仓',self)
		self.btnAccount=QPushButton('账户信息',self)
		self.btnAnalysis=QPushButton('进阶分析',self)
	

	def ButtonAct(self):
		self.btnYield.clicked.connect(self.Yield_)
		self.btnTradeDetail.clicked.connect(self.TradeDetail_)
		self.btnDailyPosition.clicked.connect(self.DailyPosition_)
		self.btnAccount.clicked.connect(self.Account_)
		self.btnAnalysis.clicked.connect(self.Analysis_)
	def CreateTablist(self):
		self.TradeDetail_tablist=QTabWidget()
		#self.TradeDetail_tablist.hide()
		self.TradeDetail_tablist.setSizePolicy(QSizePolicy.Preferred,QSizePolicy.Ignored)
		self.TradeDetail_tablist.hide()
		self.DailyPosition_tablist=QTabWidget()
		self.DailyPosition_tablist.hide()
		self.DailyPosition_tablist.setSizePolicy(QSizePolicy.Preferred,QSizePolicy.Ignored)
	
	def Yield(self):
		self.figure=plt.figure()
		self.axes1=self.figure.add_subplot(311)
		plt.ylabel(u'收益率')
		self.axes2=self.figure.add_subplot(312)
		plt.ylabel(u'交易量')
		self.axes3=self.figure.add_subplot(313)
		plt.ylabel(u'每日盈亏')

		self.axes1.hold(False)
		self.axes2.hold(True)
		self.axes3.hold(True)
		self.canvas=FigureCanvas(self.figure)
		t=self.BTdata.BackTestInterval
		s1=self.BTdata.yield_rate_['yield_rate']
		
		#self.BTdata.OptionTradeBuyVolume_['TradeVolume'][0]=0
		#self.BTdata.OptionTradeSellVolume_['TradeVolume'][0]=0
		s2_1=self.BTdata.OptionTradeBuyVolume_['TradeVolume']
		s2_2=self.BTdata.OptionTradeSellVolume_['TradeVolume']
		
		self.BTdata.Asset_['Asset'][0]=0
		s3=self.BTdata.Asset_['Asset']
		s3_1=s3[s3>0].dropna()
		t3_1=s3_1.index
		s3_2=s3[s3<0].dropna()
		t3_2=s3_2.index
		self.axes1.plot(t,s1,label=r'yield_rate')
		self.axes1.set_ylabel(u'收益率')
		self.axes2.bar(t,s2_1,align='center',yerr=0.01,color='red')
		self.axes2.bar(t,s2_2,align='center',yerr=0.01,color='green')
		self.axes2.set_ylabel(u'交易量')
		self.axes3.bar(t3_1,s3_1,align='center',yerr=0.01,color='red')
		self.axes3.bar(t3_2,s3_2,align='center',yerr=0.01,color='green')
		self.axes3.set_ylabel(u'每日盈亏')
		self.axes1.legend(loc=2)
		self.axes2.legend(loc=2)
		self.axes3.legend(loc=2)
		self.canvas.draw()	

	#交易详情
	def TradeDetail(self):
		self.PositionDiff_=self.BTdata.PositionDiff_
		self.PositionDiff_[self.PositionDiff_==0]=np.nan
		tab={}
		for i in self.BTdata.BackTestInterval:
			tab[i]=QWidget()

			TradeOptionProduct_=self.PositionDiff_.loc[i].dropna().index
			PositionDiff_=self.PositionDiff_.loc[i].dropna()
			mktprice_=self.sheetdata.mktprice_sheet_.loc[i,TradeOptionProduct_]
			num=len(TradeOptionProduct_)
			tableWidget=QTableWidget(num+1,8)
			tableWidget.setHorizontalHeaderLabels(['期权品种','头寸','标的价格(元)','成交价格(元)','期权价值','成交量(张)','费用(元)','手续费(元)'])
			tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
				
			TradeOptionProduct={}
			for j,product in enumerate(TradeOptionProduct_):
					TradeOptionProduct[j]=QTableWidgetItem(product)
					TradeOptionProduct[j].setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)			
					tableWidget.setItem(j,0,TradeOptionProduct[j])
			item_total=QTableWidgetItem('总计')
			item_total.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)			
			tableWidget.setItem(len(TradeOptionProduct),0,item_total)

			buy_sell={}
			for j,position in enumerate(PositionDiff_):
				if position>0:
					buy_sell[TradeOptionProduct[j]]=QTableWidgetItem('买进')
				else:
					buy_sell[TradeOptionProduct[j]]=QTableWidgetItem('卖出')
				buy_sell[TradeOptionProduct[j]].setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
				tableWidget.setItem(j,1,buy_sell[TradeOptionProduct[j]])
			
			ETFPrice={}
			for j,position in enumerate(PositionDiff_):
				ETFPrice[TradeOptionProduct[j]]=QTableWidgetItem(str(self.BTdata.underlying.loc[i,'spot']))
				ETFPrice[TradeOptionProduct[j]].setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)		
				tableWidget.setItem(j,2,ETFPrice[TradeOptionProduct[j]])
				
			
			TradePrice={}
			for j,price in enumerate(mktprice_):
				TradePrice[TradeOptionProduct[j]]=QTableWidgetItem(str(price))
				TradePrice[TradeOptionProduct[j]].setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
				tableWidget.setItem(j,3,TradePrice[TradeOptionProduct[j]])
			
			
			OptionValue={}
			sum=0
			for j,num in enumerate(PositionDiff_):
				if TradeOptionProduct[j].text()[-1]=='A':
					strike=float(TradeOptionProduct[j].text()[-6:-1])
				else:
					strike=float(TradeOptionProduct[j].text()[-4:])
				if TradeOptionProduct[j].text()[5]==u'购':
					temp=max(self.BTdata.underlying.loc[i,'spot']-strike,0)*num*self.sheetdata.ContractUnit_sheet_.loc[i,TradeOptionProduct[j].text()]
					OptionValue[TradeOptionProduct[j]]=QTableWidgetItem(str(temp))
				else:
					temp=max(strike-self.BTdata.underlying.loc[i,'spot'],0)*num*self.sheetdata.ContractUnit_sheet_.loc[i,TradeOptionProduct[j].text()]
					OptionValue[TradeOptionProduct[j]]=QTableWidgetItem(str(temp))
				sum=sum+temp
				OptionValue[TradeOptionProduct[j]].setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
				tableWidget.setItem(j,4,OptionValue[TradeOptionProduct[j]])
			OptionValue_sum=QTableWidgetItem(str(sum))
			OptionValue_sum.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
			tableWidget.setItem(len(OptionValue),4,OptionValue_sum)
					

			TradeVolume={}
			sum=0
			for j,num in enumerate(PositionDiff_):
				TradeVolume[TradeOptionProduct[j]]=QTableWidgetItem(str(abs(num)))
				sum=sum+abs(num)
				TradeVolume[TradeOptionProduct[j]].setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
				tableWidget.setItem(j,5,TradeVolume[TradeOptionProduct[j]])
			TradeVolume_sum=QTableWidgetItem(str(sum))	
			TradeVolume_sum.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
			tableWidget.setItem(len(TradeVolume),5,TradeVolume_sum)
			
	
			TradeCost={}
			sum=0
			for j,Position_price in enumerate(zip(PositionDiff_,mktprice_)):
				TradeCost[TradeOptionProduct[j]]=QTableWidgetItem(str(-Position_price[0]*Position_price[1]*self.sheetdata.ContractUnit_sheet_.loc[i,TradeOptionProduct[j].text()]))
				sum=sum+(-Position_price[0]*Position_price[1]*self.sheetdata.ContractUnit_sheet_.loc[i,TradeOptionProduct[j].text()])
				TradeCost[TradeOptionProduct[j]].setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
				tableWidget.setItem(j,6,TradeCost[TradeOptionProduct[j]])
			TradeCost_sum=QTableWidgetItem(str(sum))
			TradeCost_sum.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
			tableWidget.setItem(len(TradeCost),6,TradeCost_sum)
	
			TradeServiceCost={}
			sum=0
			for j,num in enumerate(PositionDiff_):
				TradeServiceCost[TradeOptionProduct[j]]=QTableWidgetItem(str(abs(num*(1.3+0.3+10))))
				sum=sum+abs(num*(1.3+0.3+10))
				TradeServiceCost[TradeOptionProduct[j]].setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
				tableWidget.setItem(j,7,TradeServiceCost[TradeOptionProduct[j]])
			TradeServiceCost_sum=QTableWidgetItem(str(sum))
			TradeServiceCost_sum.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
			tableWidget.setItem(len(TradeServiceCost),7,TradeServiceCost_sum)
		
			hbox=QHBoxLayout()
			hbox.addWidget(tableWidget)
			tab[i].setLayout(hbox)
			self.TradeDetail_tablist.addTab(tab[i],str(i)[:10])
			
		
	
	#计算有问题
	def DailyPosition(self):
		self.Position_=self.BTdata.Position_
		self.Position_[self.Position_==0]=np.nan
		tab={}
		for i in self.BTdata.BackTestInterval:
			tab[i]=QWidget()
			OptionProduct_=self.Position_.loc[i].dropna().index
			Position_=self.Position_.loc[i].dropna()
			mktprice_=self.sheetdata.mktprice_sheet_.loc[i,OptionProduct_]
			num=len(OptionProduct_)
			tableWidget=QTableWidget(num+1,6)
			tableWidget.setHorizontalHeaderLabels(['期权品种','买/卖','标的价格(元)','最新成交价格(元)','期权价值','持仓量(张)'])
			tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

			OptionProduct={}
			for j,product in enumerate(OptionProduct_):
					OptionProduct[j]=QTableWidgetItem(product)
					OptionProduct[j].setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)			
					tableWidget.setItem(j,0,OptionProduct[j])
			item_total=QTableWidgetItem('总计')
			item_total.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)			
			tableWidget.setItem(len(OptionProduct),0,item_total)

			buy_sell={}
			for j,position in enumerate(Position_):
				if position>0:
					buy_sell[OptionProduct[j]]=QTableWidgetItem('多头')
				else:
					buy_sell[OptionProduct[j]]=QTableWidgetItem('空头')
				buy_sell[OptionProduct[j]].setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
				tableWidget.setItem(j,1,buy_sell[OptionProduct[j]])

			
			ETFPrice={}
			for j,position in enumerate(Position_):
				ETFPrice[OptionProduct[j]]=QTableWidgetItem(str(self.BTdata.underlying.loc[i,'spot']))
				ETFPrice[OptionProduct[j]].setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)		
				tableWidget.setItem(j,2,ETFPrice[OptionProduct[j]])
				
			
			TradePrice={}
			for j,price in enumerate(mktprice_):
				TradePrice[OptionProduct[j]]=QTableWidgetItem(str(price))
				TradePrice[OptionProduct[j]].setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
				tableWidget.setItem(j,3,TradePrice[OptionProduct[j]])
			
			
			OptionValue={}
			sum=0
			for j,num in enumerate(Position_):
				if OptionProduct[j].text()[-1]=='A':
					strike=float(OptionProduct[j].text()[-6:-1])
				else:
					strike=float(OptionProduct[j].text()[-4:])

				if OptionProduct[j].text()[5]==u'购':
					temp=max(self.BTdata.underlying.loc[i,'spot']-strike,0)*num*self.sheetdata.ContractUnit_sheet_.loc[i,OptionProduct[j].text()]
					OptionValue[OptionProduct[j]]=QTableWidgetItem(str(temp))
				else:
					temp=max(strike-self.BTdata.underlying.loc[i,'spot'],0)*num*self.sheetdata.ContractUnit_sheet_.loc[i,OptionProduct[j].text()]
					OptionValue[OptionProduct[j]]=QTableWidgetItem(str(temp))
				sum=sum+temp
				OptionValue[OptionProduct[j]].setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
				tableWidget.setItem(j,4,OptionValue[OptionProduct[j]])
			OptionValue_sum=QTableWidgetItem(str(sum))
			OptionValue_sum.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
			tableWidget.setItem(len(OptionValue),4,OptionValue_sum)
					

			TradeVolume={}
			sum=0
			for j,num in enumerate(Position_):
				TradeVolume[OptionProduct[j]]=QTableWidgetItem(str(abs(num)))
				sum=sum+abs(num)
				TradeVolume[OptionProduct[j]].setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
				tableWidget.setItem(j,5,TradeVolume[OptionProduct[j]])
			TradeVolume_sum=QTableWidgetItem(str(sum))	
			TradeVolume_sum.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
			tableWidget.setItem(len(TradeVolume),5,TradeVolume_sum)

			hbox=QHBoxLayout()
			hbox.addWidget(tableWidget)
			tab[i].setLayout(hbox)

			self.DailyPosition_tablist.addTab(tab[i],str(i)[:10])
			
			
	def Account(self):
		num=len(self.BTdata.BackTestInterval)
		self.AccountTableWidget=QTableWidget(num+1,11)
		self.AccountTableWidget.setHorizontalHeaderLabels(['日期','可用资金','总权益','期权累计盈亏','50ETF累计盈亏','ETF保证金账户','期权保证金账户','期权手续费','期权累计的手续费','50ETF手续费','50ETF累计的手续费'])
		self.AccountTableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
		self.AccountTableWidget.hide()
		date={}
		for j,d in enumerate(self.BTdata.BackTestInterval):
			date[j]=QTableWidgetItem(str(d)[:10])
			date[j].setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
			self.AccountTableWidget.setItem(j,0,date[j])
		CashInHand={}
		for j,d in enumerate(self.BTdata.BackTestInterval):
			CashInHand[j]=QTableWidgetItem(str(round(self.BTdata.CashInHandSum_.loc[d,'cashinhand'],4)))
			CashInHand[j].setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
			self.AccountTableWidget.setItem(j,1,CashInHand[j])
		Asset={}
		for j,d in enumerate(self.BTdata.BackTestInterval):
			Asset[j]=QTableWidgetItem(str(round(self.BTdata.AssetSum_.loc[d,'Asset'],4)))
			Asset[j].setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
			self.AccountTableWidget.setItem(j,2,Asset[j])
		OptionValue={}
		for j,d in enumerate(self.BTdata.BackTestInterval):
			OptionValue[j]=QTableWidgetItem(str(round(self.BTdata.OptionValueSum_.loc[d,'optionvalue'],4)))
			OptionValue[j].setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
			self.AccountTableWidget.setItem(j,3,OptionValue[j])
		ETFValue={}
		for j,d in enumerate(self.BTdata.BackTestInterval):
			ETFValue[j]=QTableWidgetItem(str(round(self.BTdata.ProfitLoss50ETFCostSum_.loc[d,'P/L_Cost'],4)))
			ETFValue[j].setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
			self.AccountTableWidget.setItem(j,4,ETFValue[j])
		ETFMargin={}
		for j,d in enumerate(self.BTdata.BackTestInterval):
			ETFMargin[j]=QTableWidgetItem(str(round(self.BTdata.ETFMarginAccountSum_.loc[d,'ETFMarginAccount'],4)))
			ETFMargin[j].setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
			self.AccountTableWidget.setItem(j,5,ETFMargin[j])

		OptionMargin={}
		for j,d in enumerate(self.BTdata.BackTestInterval):
			OptionMargin[j]=QTableWidgetItem(str(round(self.BTdata.MarginAccountSum_.loc[d,'MarginAccount'],4)))
			OptionMargin[j].setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
			self.AccountTableWidget.setItem(j,6,OptionMargin[j])

		OptionCost={}
		for j,d in enumerate(self.BTdata.BackTestInterval):
			OptionCost[j]=QTableWidgetItem(str(round(self.BTdata.CostOptionDaily_.loc[d,'P/L_Cost'],4)))
			OptionCost[j].setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
			self.AccountTableWidget.setItem(j,7,OptionCost[j])
		OptionCostCum={}
		for j,d in enumerate(self.BTdata.BackTestInterval):
			OptionCostCum[j]=QTableWidgetItem(str(round(self.BTdata.CostOptionDailyCum_.loc[d,'P/L_Cost'],4)))
			OptionCostCum[j].setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
			self.AccountTableWidget.setItem(j,8,OptionCostCum[j])
		ETFCostDaily={}
		for j,d in enumerate(self.BTdata.BackTestInterval):
			ETFCostDaily[j]=QTableWidgetItem(str(round(self.BTdata.Cost50ETFDaily_.loc[d,'P/L_Cost'],4)))
			ETFCostDaily[j].setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
			self.AccountTableWidget.setItem(j,9,ETFCostDaily[j])
		ETFCostDailyCum={}
		for j,d in enumerate(self.BTdata.BackTestInterval):
			ETFCostDailyCum[j]=QTableWidgetItem(str(round(self.BTdata.Cost50ETFDailyCum_.loc[d,'P/L_Cost'],4)))
			ETFCostDailyCum[j].setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
			self.AccountTableWidget.setItem(j,10,ETFCostDailyCum[j])

		

	def initUI(self):
		self.setGeometry(300,300,900,700)
		self.setWindowTitle('Details')
		grid=QGridLayout()
		grid.addWidget(self.btnYield,0,0)
		grid.addWidget(self.btnTradeDetail,1,0)
		grid.addWidget(self.btnDailyPosition,2,0)
		grid.addWidget(self.btnAccount,3,0)
		grid.addWidget(self.btnAnalysis,4,0)
		grid.addWidget(self.canvas,0,1,7,7)
		grid.addWidget(self.TradeDetail_tablist,0,1,7,7)
		grid.addWidget(self.DailyPosition_tablist,0,1,7,7)
		grid.addWidget(self.AccountTableWidget,0,1,7,7)
		self.setLayout(grid)
	def Yield_(self):
		self.canvas.show()
		self.DailyPosition_tablist.hide()
		self.TradeDetail_tablist.hide()
		self.AccountTableWidget.hide()
		self.btnYield.setFlat(True)
		self.btnTradeDetail.setFlat(False)
		self.btnDailyPosition.setFlat(False)
		self.btnAccount.setFlat(False)	
		self.btnAnalysis.setFlat(False)
	
	def TradeDetail_(self):
		self.canvas.hide()
		self.DailyPosition_tablist.hide()
		self.TradeDetail_tablist.show()
		self.AccountTableWidget.hide()
		self.btnYield.setFlat(False)
		self.btnTradeDetail.setFlat(True)
		self.btnDailyPosition.setFlat(False)
		self.btnAccount.setFlat(False)
		self.btnAnalysis.setFlat(False)
	def DailyPosition_(self):
		self.canvas.hide()
		self.DailyPosition_tablist.show()
		self.TradeDetail_tablist.hide()
		self.AccountTableWidget.hide()
		self.btnYield.setFlat(False)
		self.btnTradeDetail.setFlat(False)
		self.btnDailyPosition.setFlat(True)
		self.btnAccount.setFlat(False)
		self.btnAnalysis.setFlat(False)
	
	def Account_(self):
		self.canvas.hide()
		self.DailyPosition_tablist.hide()
		self.TradeDetail_tablist.hide()
		self.AccountTableWidget.show()
		self.btnYield.setFlat(False)
		self.btnTradeDetail.setFlat(False)
		self.btnDailyPosition.setFlat(False)
		self.btnAccount.setFlat(True)
		self.btnAnalysis.setFlat(False)

	def Analysis_(self):
		self.optionAnalysis=optionAnalysis(self.BTdata)
		self.optionAnalysis.show()
		self.btnYield.setFlat(False)
		self.btnTradeDetail.setFlat(False)
		self.btnDailyPosition.setFlat(False)
		self.btnAccount.setFlat(False)
		self.btnAnalysis.setFlat(True)	
	

if __name__=='__main__':
	sns.set(color_codes=True)
	app=QApplication(sys.argv)
	BT=BackTest()
	sys.exit(app.exec_())

		



























































	
		
