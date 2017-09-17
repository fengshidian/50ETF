#encoding=utf-8

import sys
import matplotlib
import data as dt
import pandas as pd
import re
matplotlib.use("Qt5Agg")
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import seaborn as sns
from QuantLib import *
import time

class option(QWidget):
	def __init__(self,sheetData):
		super(option,self).__init__()
		
		self.sheetData=sheetData
		self.costrate=self.sheetData.costrate
		self.originalData=self.sheetData.dataprocess
		self.sheet=self.originalData.sheet
		self.sheet_names=self.originalData.sheet_names
		self.prespot=self.originalData.spot_
		self.realizedVolatility=dt.realizedVolatility()
		self.optionAnalysis=optionAnalysis(self.sheetData)
		self.winddata=self.optionAnalysis.winddata
		self.CreateLabel()
		self.CreateEdit()
		self.CreateComboBox()
		#self.CreateCheckBox()
		#self.CreateImage()
		self.CreateButton()
		self.ComboBoxAct()
		#self.CheckBoxChanged()
		self.initUI()
		self.date=str(time.strftime('%Y-%m-%d',time.localtime(time.time())))
		self.HistoryDaysTransit=None
	def CreateLabel(self):
		self.lblOptionType=QLabel('期权类型',self)
		self.lblUnderlyingProduct=QLabel('期权标的',self)
		self.lblOptionStartDate=QLabel('期权起始日期',self)
		self.lblOptionEndDate=QLabel('期权到期日期',self)
		self.lblOptionCode=QLabel('期权代码',self)
		self.lblHistoryDays=QLabel('历史数据天数',self)
		self.lblUnderlyingPrice=QLabel('标的价格',self)
		self.lblOptionPrice=QLabel('期权价格',self)
		self.lblStrike=QLabel('执行价格',self)
		self.lblNoRiskRate=QLabel('无风险利率',self)
		self.lblRealizedVolatility=QLabel('历史波动率',self)
		self.lblDelta=QLabel('Delta值',self)
		self.lblGamma=QLabel('Gamma值',self)
		self.lblVega=QLabel('Vega值',self)
		self.lblImpliedVolatility=QLabel('隐含波动率',self)
		self.lblTheoryValue=QLabel('理论价格',self)
		#self.lblHedgeType=QLabel('对冲类型',self)
		self.lblCurrentDate=QLabel('当前时刻',self)
		self.lblOptionProduct=QLabel('期权品种',self)

	def CreateEdit(self):
		self.OptionTypeEdit=QLineEdit(self)
		self.UnderlyingProductEdit=QLineEdit(self)
		self.OptionStartDateEdit=QLineEdit(self)	
		self.OptionEndDateEdit=QLineEdit(self)
		self.OptionCodeEdit=QLineEdit(self)
		#self.HistoryDaysEdit=QLineEdit(self)
		self.UnderlyingPriceEdit=QLineEdit(self)
		self.OptionPriceEdit=QLineEdit(self)
		self.StrikeEdit=QLineEdit(self)
		self.NoRiskRateEdit=QLineEdit(self)
		self.RealizedVolatilityEdit=QLineEdit(self)
		self.DeltaEdit=QLineEdit(self)
		self.GammaEdit=QLineEdit(self)
		self.VegaEdit=QLineEdit(self)
		self.ImpliedVolatilityEdit=QLineEdit(self)
		self.TheoryValueEdit=QLineEdit(self)


	def CreateComboBox(self):
		self.comboOptionProduct=QComboBox(self)
		self.comboOptionProduct.addItem('')
		for i in self.sheet_names:
			self.comboOptionProduct.addItem(i)

		self.comboYears=QComboBox(self)
		self.comboYears.addItem('')
		for i in range(2015,2018):
			self.comboYears.addItem(str(i))

		self.comboMonths=QComboBox(self)
		self.comboMonths.addItem('')
		for i in range(1,13):
			if len(str(i))==1:
				self.comboMonths.addItem(str(0)+str(i))	
			else:
				self.comboMonths.addItem(str(i))
		
		self.comboDays=QComboBox(self)
		self.comboDays.addItem('')
		for i in range(1,32):
			if len(str(i))==1:
				self.comboDays.addItem(str(0)+str(i))
			else:
				self.comboDays.addItem(str(i))
		
		self.comboHistoryDays=QComboBox(self)
		self.comboHistoryDays.addItem('')
		self.comboHistoryDays.addItem('90天')
		self.comboHistoryDays.addItem('60天')
		self.comboHistoryDays.addItem('30天')
		self.comboHistoryDays.addItem('20天')
		self.comboHistoryDays.addItem('10天')

	def ComboBoxAct(self):
		self.comboYears.activated[str].connect(self.onActivatedYears)
		self.comboMonths.activated[str].connect(self.onActivatedMonths)
		self.comboDays.activated[str].connect(self.onActivatedDays)
		self.comboOptionProduct.activated[str].connect(self.onActivatedOptionProduct)
		#self.comboHedgeType.activated[str].connect(self.onActivatedHedgeType)
		self.comboHistoryDays.activated[str].connect(self.onActivatedHistoryDays)
	def CreateButton(self):
		self.btn=QPushButton('Analysis',self)
		self.btn.clicked.connect(self.buttonclicked)
	def buttonclicked(self):
		self.optionAnalysis
		self.optionAnalysis.show()
	def initUI(self):
		#---------------------------------------------------
		grid=QGridLayout()
		grid.addWidget(self.lblOptionType,2,0)
		grid.addWidget(self.OptionTypeEdit,2,1)

		grid.addWidget(self.lblUnderlyingProduct,3,0)
		grid.addWidget(self.UnderlyingProductEdit,3,1)

		grid.addWidget(self.lblOptionStartDate,4,0)
		grid.addWidget(self.OptionStartDateEdit,4,1)

		grid.addWidget(self.lblOptionEndDate,5,0)
		grid.addWidget(self.OptionEndDateEdit,5,1)

		grid.addWidget(self.lblHistoryDays,6,0)
		grid.addWidget(self.comboHistoryDays,6,1)

		grid.addWidget(self.lblUnderlyingPrice,2,2)
		grid.addWidget(self.UnderlyingPriceEdit,2,3)


		grid.addWidget(self.lblOptionPrice,3,2)
		grid.addWidget(self.OptionPriceEdit,3,3)

		grid.addWidget(self.lblStrike,4,2)
		grid.addWidget(self.StrikeEdit,4,3)

		grid.addWidget(self.lblNoRiskRate,5,2)	
		grid.addWidget(self.NoRiskRateEdit,5,3)


		grid.addWidget(self.lblRealizedVolatility,6,2)
		grid.addWidget(self.RealizedVolatilityEdit,6,3)

		grid.addWidget(self.lblDelta,2,5)
		grid.addWidget(self.DeltaEdit,2,6)

		grid.addWidget(self.lblGamma,3,5)
		grid.addWidget(self.GammaEdit,3,6)

		grid.addWidget(self.lblVega,4,5)
		grid.addWidget(self.VegaEdit,4,6)

		grid.addWidget(self.lblImpliedVolatility,5,5)
		grid.addWidget(self.ImpliedVolatilityEdit,5,6)

		grid.addWidget(self.lblTheoryValue,6,5)
		grid.addWidget(self.TheoryValueEdit,6,6)

		#------------------------------------------------
		grid.addWidget(self.lblOptionProduct,0,0)
		grid.addWidget(self.comboOptionProduct,0,1)
		grid.addWidget(self.lblOptionCode,0,2)
		grid.addWidget(self.OptionCodeEdit,0,3)
		grid.addWidget(self.btn,0,6)
		
		grid.addWidget(self.lblCurrentDate,1,0)
		hboxDate=QHBoxLayout()
		hboxDate.addWidget(self.comboYears)
		hboxDate.addWidget(self.comboMonths)
		hboxDate.addWidget(self.comboDays)
		grid.addLayout(hboxDate,1,1)

		self.OptionTable=QTableWidget(150,9)
		self.OptionTable.setHorizontalHeaderLabels(['期权产品','期权代码','期权类型','delta','gamma','vega','theta','impliedVolatility','theoryvalue'])
		self.OptionTable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
		grid.addWidget(self.OptionTable,12,0,15,9)
		vbox=QVBoxLayout()
		vbox.addLayout(grid)
	
		self.setGeometry(300,300,900,700)
		self.setWindowTitle('OptionHedge')
		self.show()
		self.setLayout(vbox)
	def onActivatedOptionProduct(self,OptionProduct):
		j=0
		for i in self.sheet_names:
			if OptionProduct==self.sheet_names[j]:
				self.OptionProduct=OptionProduct
				if self.sheet_names[j][-1]=='A':
					strike=self.sheet_names[j][-6:-1]
					contractUnit=10220
				else:
					strike=self.sheet_names[j][-4:]
					contractUnit=10000
				strike=float(strike)
				if self.sheet_names[j][5]==u'购':
					optionType=1
				else:
					optionType=0
				self.dataCreate=dt.simulation(self.sheet[j],strike,optionType,self.prespot,contractUnit,self.costrate)
				self.OptionTypeEdit.setText(u'认'+self.OptionProduct[5])
				self.UnderlyingProductEdit.setText('50ETF')
				self.OptionStartDateEdit.setText(str(self.dataCreate.data.index[0])[:10])
				self.OptionCodeEdit.setText(str(self.originalData.code_index[OptionProduct]))				
				self.index=[]
				k=0
				for h in self.dataCreate.data.index:
					temp=re.sub(r'\D','',str(h)[:10])
					self.index.append(temp)
					k=k+1
				self.IndexSeries=pd.Series(self.dataCreate.data.index,index=self.index)

				self.OptionEndDateEdit.setText(self.Exerciseday(self.index[0]))	
	
				if self.date not in self.index:
					print 'select the trading day'
				else:
					self.setText(self.dataCreate,self.date)
					self.setOptionTable(self.date)
				break
			else:
				j=j+1
	def Exerciseday(self,date):
		year=int(date[:4])
		month=int(date[4:6])
		day=int(date[6:])
		today=Date(day,month,year)
		china_calendar=China()
		period=Period(self.dataCreate.ptmtradeday[0]-1,Days)
		exerciseday=china_calendar.advance(today,period)
		year_ =str(exerciseday.year())
		month_=str(exerciseday.month())
		day_=str(exerciseday.dayOfMonth())
		if len(month_)==1:
			month_=str(0)+month_
		else:
			pass
		if len(day_)==1:
			day_=str(0)+day_
		else:
			pass
		return year_+'-'+month_+'-'+day_
			

	def onActivatedHistoryDays(self,txt):
		if txt==u'90天':
			self.RealizedVolatilityEdit.setText(str(round(self.realizedVolatility.realizedVol_90.loc[self.date]['spot'],4))+'/'+str(round(self.winddata.wind_realizedVol_90.loc[self.IndexSeries[self.date],'wind_realizedVol_90'],4)))
		if txt==u'60天':
			self.RealizedVolatilityEdit.setText(str(round(self.realizedVolatility.realizedVol_60.loc[self.date]['spot'],4))+'/'+str(round(self.winddata.wind_realizedVol_60.loc[self.IndexSeries[self.date],'wind_realizedVol_60'],4)))
		elif txt==u'30天':
			self.RealizedVolatilityEdit.setText(str(round(self.realizedVolatility.realizedVol_30.loc[self.date]['spot'],4))+'/'+str(round(self.winddata.wind_realizedVol_30.loc[self.IndexSeries[self.date],'wind_realizedVol_30'],4)))
		elif txt==u'20天':
			self.RealizedVolatilityEdit.setText(str(round(self.realizedVolatility.realizedVol_20.loc[self.date]['spot'],4)))
		elif txt==u'10天':
			self.RealizedVolatilityEdit.setText(str(round(self.realizedVolatility.realizedVol_10.loc[self.date]['spot'],4)))
		else:
			pass
		self.HistoryDaysTransit=txt

	def onActivatedYears(self,year):
		self.year=year
		self.date=self.year+self.date[-4:]
		self.onActivatedHistoryDays(self.HistoryDaysTransit)
		if self.date not in self.index:
			print 'select the trading day'
		else:
			self.setText(self.dataCreate,self.date)
			#self.setTable(self.dataCreate,self.date)
			self.setOptionTable(self.date)
	def onActivatedMonths(self,month):
		self.month=month
		self.date=self.date[:4]+self.month+self.date[-2:]
		self.onActivatedHistoryDays(self.HistoryDaysTransit)
		if self.date not in self.index:
			QMessageBox.information(self,'warning','Please select the trading day')
		else:
			self.setText(self.dataCreate,self.date)
			#self.setTable(self.dataCreate,self.date)
			self.setOptionTable(self.date)
			
	def onActivatedDays(self,day):
		self.day=day
		self.date=self.date[:6]+self.day
		self.onActivatedHistoryDays(self.HistoryDaysTransit)
		if self.date not in self.index:
			QMessageBox.information(self,'warning','Please select the trading day')
		else:
			self.setText(self.dataCreate,self.date)
			#self.setTable(self.dataCreate,self.date)
			self.setOptionTable(self.date)
	
	def setText(self,data,date):
		self.UnderlyingPriceEdit.setText(str(round(data.spot_.loc[date]['spot'],4)))
		self.OptionPriceEdit.setText(str(round(data.mktprice_.loc[date]['mktprice'],4)))
		self.StrikeEdit.setText(str(data.strike))
		self.NoRiskRateEdit.setText(str(0.03))
		#self.HistoryVolatilityEdit.setText()

		self.DeltaEdit.setText(str(round(data.delta_.loc[date]['delta'],4))+'/'+str(round(self.winddata.wind_delta_sheet_.loc[self.IndexSeries[date],self.OptionProduct],4)))
		self.GammaEdit.setText(str(round(data.gamma_.loc[date]['gamma'],4))+'/'+str(round(self.winddata.wind_gamma_sheet_.loc[self.IndexSeries[date],self.OptionProduct],4)))
		self.VegaEdit.setText(str(round(data.vega_.loc[date]['vega'],4))+'/'+str(round(self.winddata.wind_vega_sheet_.loc[self.IndexSeries[date],self.OptionProduct],4)))
		self.ImpliedVolatilityEdit.setText(str(round(data.implied_.loc[date]['implied'],4))+'/'+str(round(self.winddata.wind_impliedVolatility_sheet_.loc[self.IndexSeries[date],self.OptionProduct],4)))
		self.TheoryValueEdit.setText(str(round(data.theoryvalue_.loc[date]['theoryvalue'],4))+'/'+str(round(self.winddata.wind_theoryValue_sheet_.loc[self.IndexSeries[date],self.OptionProduct],4)))
	
	def setOptionTable(self,date):
		dateSelect=self.IndexSeries[date]
		OptionProduct_=self.sheetData.delta_sheet_.loc[dateSelect].dropna().index
		
		OptionDelta_=self.sheetData.delta_sheet_.loc[dateSelect].dropna().values
		OptionGamma_=self.sheetData.gamma_sheet_.loc[dateSelect].dropna().values
		OptionVega_=self.sheetData.vega_sheet_.loc[dateSelect].dropna().values
		OptionTheta_=self.sheetData.theta_sheet_.loc[dateSelect].dropna().values
		OptionImpliedVolatility_=self.sheetData.impliedVolatility_sheet_.loc[dateSelect].dropna().values
		OptionTheoryValue_=self.sheetData.theoryvalue_sheet_.loc[dateSelect].dropna().values
		print len(OptionProduct_),len(OptionDelta_),len(OptionImpliedVolatility_)
		
		#期权产品		
		j=0
		OptionProduct={}
		for product in OptionProduct_:
			OptionProduct[j]=QTableWidgetItem(product)
			OptionProduct[j].setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)		
			self.OptionTable.setItem(j,0,OptionProduct[j])
			j=j+1

		#期权代码
		j=0
		OptionCode={}
		for product in OptionProduct_:
			OptionCode[j]=QTableWidgetItem(str(self.originalData.code_index[product]))
			OptionCode[j].setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
			self.OptionTable.setItem(j,1,OptionCode[j])
			j=j+1

		#期权类型 认购或认沽
		j=0
		OptionType={}
		for type_ in OptionProduct_:
			OptionType[j]=QTableWidgetItem(u'认'+type_[5])
			OptionType[j].setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)		
			self.OptionTable.setItem(j,2,OptionType[j])
			j=j+1		
		
		j=0
		OptionDelta={}
		for delta in OptionDelta_:
			OptionDelta[j]=QTableWidgetItem(str(round(delta,4))+'/'+str(round(self.winddata.wind_delta_sheet_.loc[dateSelect,OptionProduct_[j]],4)))
			OptionDelta[j].setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
			self.OptionTable.setItem(j,3,OptionDelta[j])
			j=j+1

		j=0
		OptionGamma={}
		for gamma in OptionGamma_:
			OptionGamma[j]=QTableWidgetItem(str(round(gamma,4))+'/'+str(round(self.winddata.wind_gamma_sheet_.loc[dateSelect,OptionProduct_[j]],4)))
			OptionGamma[j].setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
			self.OptionTable.setItem(j,4,OptionGamma[j])
			j=j+1

		j=0
		OptionVega={}
		for vega in OptionVega_:
			OptionVega[j]=QTableWidgetItem(str(round(vega,4))+'/'+str(round(self.winddata.wind_vega_sheet_.loc[dateSelect,OptionProduct_[j]],4)))
			OptionVega[j].setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
			self.OptionTable.setItem(j,5,OptionVega[j])
			j=j+1
		j=0
		OptionTheta={}
		for theta in OptionTheta_:
			OptionTheta[j]=QTableWidgetItem(str(round(theta,4))+'/'+str(round(self.winddata.wind_theta_sheet_.loc[dateSelect,OptionProduct_[j]],4)))
			OptionTheta[j].setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
			self.OptionTable.setItem(j,6,OptionTheta[j])
			j=j+1
		
		j=0
		OptionImpliedVolatility={}
		for product in OptionProduct_:
			OptionImpliedVolatility[j]=QTableWidgetItem(str(round(self.sheetData.impliedVolatility_sheet_.loc[dateSelect,product],4))+'/'+str(round(self.winddata.wind_impliedVolatility_sheet_.loc[dateSelect,OptionProduct_[j]],4)))	
			OptionImpliedVolatility[j].setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
			self.OptionTable.setItem(j,7,OptionImpliedVolatility[j])
			j=j+1
		
		j=0
		OptionTheoryValue={}
		for product in OptionProduct_:
			OptionTheoryValue[j]=QTableWidgetItem(str(round(self.sheetData.theoryvalue_sheet_.loc[dateSelect,product],4))+'/'+str(round(self.winddata.wind_theoryValue_sheet_.loc[dateSelect,OptionProduct_[j]],4)))
			OptionTheoryValue[j].setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
			self.OptionTable.setItem(j,8,OptionTheoryValue[j])
			j=j+1
		
class optionAnalysis(QWidget):
	def __init__(self,sheetData):
		super(optionAnalysis,self).__init__()
		self.data=sheetData
		self.winddata=dt.winddata()
		self.realizedVolatility=dt.realizedVolatility()
		self.option_names=self.data.option_names
		self.CreateLabel()
		self.CreateEdit()
		self.CreateComboBox()
		self.CreateImage()
		self.CreateCheckBox()
		self.comboBoxAct()
		self.initUI2()
		self.ParasTransit='delta'
	
	def CreateLabel(self):
		self.lblOptionProduct=QLabel('期权品种',self)
		self.lblOptionType=QLabel('期权类型',self)
		self.lblOptionStartDate=QLabel('期权起始日期',self)
		self.lblOptionEndDate=QLabel('期权到期日期',self)
		self.lblParas=QLabel('参数类型',self)
	def CreateEdit(self):
		self.OptionTypeEdit=QLineEdit(self)
		self.OptionStartDateEdit=QLineEdit(self)
		self.OptionEndDateEdit=QLineEdit(self)
		
	def CreateComboBox(self):
		self.comboOptionProduct=QComboBox(self)
		self.comboOptionProduct.addItem('')
		for i in self.option_names:
			self.comboOptionProduct.addItem(i)

		self.comboParas=QComboBox(self)
		self.comboParas.addItem('')
		self.comboParas.addItem('delta')
		#self.comboParas.addItem('WWModel')
		#self.comboParas.addItem('ZakamoulineModel')
		self.comboParas.addItem('gamma')
		#self.comboParas.addItem('vega')
		self.comboParas.addItem('impliedVolatility')
		self.comboParas.addItem('optionPrice')
		self.comboParas.addItem('realizedVol')
	def CreateImage(self):
		self.figure=plt.figure()

		self.axes=self.figure.add_subplot(111)
		self.axes.hold(False)
		self.canvas=FigureCanvas(self.figure)
	def CreateCheckBox(self):
		self.cb=QCheckBox()
		self.cb.stateChanged.connect(self.axesChange)
	def comboBoxAct(self):
		self.comboOptionProduct.activated[str].connect(self.onActivatedOptionProduct)
		self.comboParas.activated[str].connect(self.onActivatedParas)
	def initUI2(self):
		grid=QGridLayout()
		grid.addWidget(self.lblOptionProduct,0,0)
		grid.addWidget(self.comboOptionProduct,0,1)
		grid.addWidget(self.lblOptionType,1,0)
		grid.addWidget(self.OptionTypeEdit,1,1)
		grid.addWidget(self.lblOptionStartDate,1,2)
		grid.addWidget(self.OptionStartDateEdit,1,3)
		grid.addWidget(self.lblOptionEndDate,1,4)
		grid.addWidget(self.OptionEndDateEdit,1,5)
		grid.addWidget(self.lblParas,2,0)
		grid.addWidget(self.comboParas,2,1)
		grid.addWidget(self.cb,2,2)

		vbox=QVBoxLayout()
		vbox.addLayout(grid)
		vbox.addWidget(self.canvas)
		self.setLayout(vbox)

		self.setGeometry(300,300,900,700)
		self.setWindowTitle('optionAnalysis')
		#self.show()
	def onActivatedOptionProduct(self,optionProduct):
		self.optionProductTransit=optionProduct
		self.OptionTypeEdit.setText(u'认'+optionProduct[5])
		temp=self.data.mktprice_sheet_.loc[:,optionProduct].dropna()
		self.OptionStartDateEdit.setText(str(temp.index[0])[:10])
		self.OptionEndDateEdit.setText(self.Exerciseday(str(temp.index[0])[:10]))
		self.onActivatedParas(self.ParasTransit)
	def Exerciseday(self,date):
		year=int(date[:4])
		month=int(date[5:7])
		day=int(date[8:10])
		today=Date(day,month,year)
		china_calendar=China()
		temp=self.data.ptmtradeday_sheet_.loc[:,self.optionProductTransit].dropna()
		period=Period(int(temp.values[0])-1,Days)
		exerciseday=china_calendar.advance(today,period)
		year_ =str(exerciseday.year())
		month_=str(exerciseday.month())
		day_=str(exerciseday.dayOfMonth())
		if len(month_)==1:
			month_=str(0)+month_
		else:
			pass
		if len(day_)==1:
			day_=str(0)+day_
		else:
			pass
		return year_+'-'+month_+'-'+day_
	def onActivatedParas(self,Paras):
		if Paras=='delta':
			self.DeltaPlot()
		#elif Paras=='WWModel':
			#self.WWPlot()
		#elif Paras=='ZakamoulineModel':
			#self.ZakaPlot()
		elif Paras=='gamma':
			self.GammaPlot()
		elif Paras=='vega':
			self.VegaPlot()
		elif Paras=='impliedVolatility':
			self.ImpliedVolatilityPlot()
		elif Paras=='optionPrice':
			self.pricePlot()
		elif Paras=='realizedVol':
			self.realizedVolatilityPlot()
		else:
			pass
		self.ParasTransit=Paras		
	def DeltaPlot(self):
		temp=self.data.delta_sheet_.loc[:,self.optionProductTransit].dropna()
		t=temp.index
		start=t[0]
		end=t[-1]
		s=temp.values
		temp_wind=self.winddata.wind_delta_sheet_.loc[start:end,self.optionProductTransit]
		t_wind=temp_wind.index
		s_wind=temp_wind.values
		
		self.axes.plot(t,s,label=r'delta')
		self.axes.hold(True)
		self.axes.plot(t_wind,s_wind,label=r'wind_delta')
		self.axes.legend(loc=2)
		self.canvas.draw()
		self.axes.hold(False)
		self.axesChange(self.stateTransit)
	def WWPlot(self):
		temp_inf=self.data.WWBandInf_sheet_.loc[:,self.optionProductTransit].dropna()
		temp_sup=self.data.WWBandSup_sheet_.loc[:,self.optionProductTransit].dropna()
		temp_delta=self.data.delta_sheet_.loc[:,self.optionProductTransit].dropna()
		temp_delta_hold=self.data.WWDeltaHold_sheet_.loc[:,self.optionProductTransit].dropna()
		t=temp_inf.index
		s_inf=temp_inf.values
		s_sup=temp_sup.values
		s_delta=temp_delta.values	
		s_delta_hold=temp_delta_hold.values
		self.axes.plot(t,s_inf,label=r'inf')
		self.axes.hold(True)
		self.axes.plot(t,s_sup,label=r'sup')
		self.axes.plot(t,s_delta,label=r'delta')
		self.axes.plot(t,s_delta_hold,label=r'delta_hold')
		self.axes.legend(loc=2)
		self.canvas.draw()
		self.axes.hold(False)
		self.axesChange(self.stateTransit)
	def ZakaPlot(self):
		temp_inf=self.data.ZakamoulineBandInf_sheet_.loc[:,self.optionProductTransit].dropna()
		temp_sup=self.data.ZakamoulineBandSup_sheet_.loc[:,self.optionProductTransit].dropna()
		temp_delta=self.data.ZakamoulineDelta_sheet_.loc[:,self.optionProductTransit].dropna()
		temp_delta_hold=self.data.ZakamoulineDeltaHold_sheet_.loc[:,self.optionProductTransit].dropna()
		t=temp_inf.index
		s_inf=temp_inf.values
		s_sup=temp_sup.values
		s_delta=temp_delta.values	
		s_delta_hold=temp_delta_hold.values
		self.axes.plot(t,s_inf,label=r'inf')
		self.axes.hold(True)
		self.axes.plot(t,s_sup,label=r'sup')
		self.axes.plot(t,s_delta,label=r'delta')
		self.axes.plot(t,s_delta_hold,label=r'delta_hold')
		self.axes.legend(loc=2)
		self.canvas.draw()
		self.axes.hold(False)
		self.axesChange(self.stateTransit)
	def GammaPlot(self):
		temp=self.data.gamma_sheet_.loc[:,self.optionProductTransit].dropna()
		t=temp.index
		start=t[0]
		end=t[-1]
		temp_wind=self.winddata.wind_gamma_sheet_.loc[start:end,self.optionProductTransit]
		t_wind=temp_wind.index
		s_wind=temp_wind.values
		s=temp.values
		self.axes.plot(t,s,label=r'gamma')
		self.axes.hold(True)
		self.axes.plot(t_wind,s_wind,label=r'wind_gamma')
		self.axes.legend(loc=2)
		self.canvas.draw()
		self.axes.hold(False)
		self.axesChange(self.stateTransit)
	def VegaPlot(self):
		temp=self.data.vega_sheet_.loc[:,self.optionProductTransit].dropna()
		t=temp.index
		start=t[0]
		end=t[-1]
		temp_wind=self.winddata.wind_vega_sheet_.loc[start:end,self.optionProductTransit]
		t_wind=temp_wind.index
		s_wind=temp_wind.values
		s=temp.values
		self.axes.plot(t,s,label=r'vega')
		self.axes.hold(True)
		self.axes.plot(t_wind,s_wind,label=r'wind_vega')
		self.axes.legend(loc=2)
		self.canvas.draw()
		self.axes.hold(False)
		self.axesChange(self.stateTransit)
	def ImpliedVolatilityPlot(self):
		temp=self.data.impliedVolatility_sheet_.loc[:,self.optionProductTransit].dropna()
		t=temp.index
		start=t[0]
		end=t[-1]
		temp_wind=self.winddata.wind_impliedVolatility_sheet_.loc[start:end,self.optionProductTransit]
		t_wind=temp_wind.index
		s_wind=temp_wind.values
		s=temp.values
		self.axes.plot(t,s,label=r'impliedVolatility')
		self.axes.hold(True)
		self.axes.plot(t_wind,s_wind,label=r'wind_impliedVolatility')
		self.axes.legend(loc=2)
		self.canvas.draw()
		self.axes.hold(False)
		self.axesChange(self.stateTransit)
	def pricePlot(self):
		temp1=self.data.theoryvalue_sheet_.loc[:,self.optionProductTransit].dropna()
		temp2=self.data.mktprice_sheet_.loc[:,self.optionProductTransit].dropna()
		t1=temp1.index
		start=t1[0]
		end=t1[-1]
		s1=temp1.values
		t2=temp2.index
		s2=temp2.values
		temp1_wind=self.winddata.wind_theoryValue_sheet_.loc[start:end,self.optionProductTransit]
		t_wind=temp1_wind.index
		s_wind=temp1_wind.values
		self.axes.plot(t1,s1,label=r'theoryvalue',color='blue')
		self.axes.hold(True)
		self.axes.plot(t2,s2,label=r'mktprice',color='red')
		self.axes.plot(t_wind,s_wind,label=r'wind_theoryvalue',color='green')
		self.axes.legend(loc=2)
		self.canvas.draw()
		self.axes.hold(False)
		self.axesChange(self.stateTransit)
	def realizedVolatilityPlot(self):
		temp1=self.data.theoryvalue_sheet_.loc[:,self.optionProductTransit].dropna()
		temp2=self.data.mktprice_sheet_.loc[:,self.optionProductTransit].dropna()
		t1=temp1.index
		start=t1[0]
		end=t1[-1]
		temp=self.realizedVolatility.realizedVol[start:end]
		t=temp.index
		s_10=temp.loc[:,'realizedVol_10']
		s_20=temp.loc[:,'realizedVol_20']
		s_30=temp.loc[:,'realizedVol_30']
		s_60=temp.loc[:,'realizedVol_60']
		s_90=temp.loc[:,'realizedVol_90']
		self.axes.plot(t,s_10,label=r'realizedVol_10')
		self.axes.hold(True)
		self.axes.plot(t,s_20,label=r'realizedVol_20')
		self.axes.plot(t,s_30,label=r'realizedVol_30')
		self.axes.plot(t,s_60,label=r'realizedVol_60')
		self.axes.plot(t,s_90,label=r'realizedVol_90')
		self.axes.legend(loc=2)
		self.canvas.draw()
		self.axes.hold(False)
		self.axesChange(self.stateTransit)
	def axesChange(self,state):
		if state==Qt.Checked:
			self.axes.hold(True)
		else:
			self.axes.hold(False)
		self.stateTransit=state
	
if __name__=='__main__':
	sns.set(color_codes=True)
	app=QApplication(sys.argv)
	costrate=0.0025
	sheetData=dt.sheetData(costrate)
	ex=option(sheetData)
	sys.exit(app.exec_())























		
