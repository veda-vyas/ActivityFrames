# -*- coding: utf-8 -*- 

###########################################################################
## Python code generated with wxFormBuilder (version Jun 17 2015)
## http://www.wxformbuilder.org/
##
## PLEASE DO "NOT" EDIT THIS FILE!
###########################################################################

import wx
import wx.xrc

###########################################################################
## Class GUI
###########################################################################

class GUI ( wx.Frame ):
	
	def __init__( self, parent ):
		wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = "Activity Frames", pos = wx.DefaultPosition, size = wx.Size( 250,150 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )
		
		self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )
		
		fgSizer1 = wx.FlexGridSizer( 0, 2, 0, 0 )
		fgSizer1.SetFlexibleDirection( wx.BOTH )
		fgSizer1.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_spinCtrl2 = wx.SpinCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 90,-1 ), wx.SP_ARROW_KEYS, 0, 10, 5 )
		fgSizer1.Add( self.m_spinCtrl2, 0, wx.ALL, 5 )
		
		self.m_button9 = wx.Button( self, wx.ID_ANY, u"Snooze", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer1.Add( self.m_button9, 0, wx.ALL, 5 )
		
		bSizer2 = wx.BoxSizer( wx.VERTICAL )
		
		self.m_button8 = wx.Button( self, wx.ID_ANY, u"Exit", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer2.Add( self.m_button8, 0, wx.ALL, 5 )
		
		
		fgSizer1.Add( bSizer2, 1, wx.EXPAND, 5 )
		
		
		self.SetSizer( fgSizer1 )
		self.Layout()
		
		self.Centre( wx.BOTH )
		
		# Connect Events
		self.m_button9.Bind( wx.EVT_BUTTON, self.snooze )
		self.m_button8.Bind( wx.EVT_BUTTON, self.exit )
	
	def __del__( self ):
		pass
	

	# Virtual event handlers, overide them in your derived class
	def snooze( self, event ):
		event.Skip()
	
	def exit( self, event ):
		event.Skip()