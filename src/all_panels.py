
# -*- coding: utf-8 -*-

#--------------------------------------------------------------------------
# Python code generated with wxFormBuilder (version 3.9.0 Jun 14 2020)
# http://www.wxformbuilder.org/
#
# PLEASE DO *NOT* EDIT THIS FILE!
#--------------------------------------------------------------------------

import wx
import wx.xrc
import wx.grid

import gettext
_ = gettext.gettext


def _apply_button_style(button):
	button.SetFont(wx.Font( 9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False ))
	button.SetForegroundColour(wx.Colour( 255, 255, 255 ))
	button.SetBackgroundColour(wx.Colour( 25, 25, 112 ))
	return button

#--------------------------------------------------------------------------
#  Class main_panel
#---------------------------------------------------------------------------

class main_panel ( wx.Frame ):

	def __init__(self, parent):
		wx.Frame.__init__ (self, parent, id = wx.ID_ANY, title = wx.EmptyString, pos = wx.DefaultPosition, size = wx.Size( 800,460 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL)

		self.SetSizeHints(wx.DefaultSize, wx.DefaultSize)
		self.SetBackgroundColour(wx.Colour( 255, 255, 255 ))

		root = wx.BoxSizer(wx.HORIZONTAL)

		word_lib = wx.BoxSizer(wx.VERTICAL)

		self.tip_set_wordlib = wx.StaticText(self, wx.ID_ANY, _(u"选择词句库"), wx.DefaultPosition, wx.DefaultSize, 0)
		self.tip_set_wordlib.Wrap(-1)

		self.tip_set_wordlib.SetFont(wx.Font( 18, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, wx.EmptyString ))

		word_lib.Add(self.tip_set_wordlib, 0, wx.ALL | wx.EXPAND, 5)

		m_listBox1Choices = []
		self.m_listBox1 = wx.ListBox(self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, m_listBox1Choices, 0)
		word_lib.Add(self.m_listBox1, 1, wx.EXPAND | wx.ALL, 5)

		root.Add(word_lib, 0, wx.EXPAND | wx.ALL, 5)

		self.workbar = wx.Notebook(self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.NB_TOP)
		root.Add(self.workbar, 1, wx.EXPAND | wx.ALL, 5)

		self.SetSizer(root)
		self.Layout()
		self.Centre(wx.BOTH)

		self.SetSize(wx.Size(800, 460))

	def __del__( self ):
		pass


#--------------------------------------------------------------------------
#  Class wordlib_grid
#---------------------------------------------------------------------------

class wordlib_grid ( wx.Panel ):

	def __init__(self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.Size( 800,460 ), style = wx.TAB_TRAVERSAL, name = wx.EmptyString):
		wx.Panel.__init__ (self, parent, id = id, pos = pos, size = size, style = style, name = name)

		root = wx.BoxSizer(wx.VERTICAL)

		self.wordlib_path = wx.TextCtrl(self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0)
		root.Add(self.wordlib_path, 0, wx.EXPAND, 5)

		self.grid_wordlib = wx.grid.Grid(self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, 0)

		# Grid
		self.grid_wordlib.CreateGrid(200, 2)
		self.grid_wordlib.EnableEditing(True)
		self.grid_wordlib.EnableGridLines(True)
		self.grid_wordlib.EnableDragGridSize(True)
		self.grid_wordlib.SetMargins(0, 0)

		# Columns
		self.grid_wordlib.SetColSize(0, 300)
		self.grid_wordlib.SetColSize(1, 311)
		self.grid_wordlib.EnableDragColMove(False)
		self.grid_wordlib.EnableDragColSize(True)
		self.grid_wordlib.SetColLabelSize(30)
		self.grid_wordlib.SetColLabelValue(0, _(u"词句"))
		self.grid_wordlib.SetColLabelValue(1, _(u"中文释义(留空自动机翻)"))
		self.grid_wordlib.SetColLabelAlignment(wx.ALIGN_CENTER, wx.ALIGN_BOTTOM)

		# Rows
		self.grid_wordlib.SetRowSize(0, 1)
		self.grid_wordlib.EnableDragRowSize(True)
		self.grid_wordlib.SetRowLabelSize(60)
		self.grid_wordlib.SetRowLabelAlignment(wx.ALIGN_CENTER, wx.ALIGN_CENTER)

		# Label Appearance
		self.grid_wordlib.SetLabelBackgroundColour(wx.SystemSettings.GetColour( wx.SYS_COLOUR_INFOBK ))

		# Cell Defaults
		self.grid_wordlib.SetDefaultCellBackgroundColour(wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOW ))
		self.grid_wordlib.SetDefaultCellAlignment(wx.ALIGN_LEFT, wx.ALIGN_TOP)
		root.Add(self.grid_wordlib, 1, wx.EXPAND, 5)


		self.SetSizer( root )
		self.Layout()

	def __del__( self ):
		pass


#--------------------------------------------------------------------------
#  Class wordlib_editor
#---------------------------------------------------------------------------

class wordlib_editor ( wx.Frame ):

	def __init__(self, parent):
		wx.Frame.__init__ (self, parent, id = wx.ID_ANY, title = wx.EmptyString, pos = wx.DefaultPosition, size = wx.Size( 800,460 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL)

		self.SetSizeHints(wx.DefaultSize, wx.DefaultSize)
		self.SetBackgroundColour(wx.Colour( 255, 255, 255 ))

		root = wx.BoxSizer(wx.HORIZONTAL)

		self.grid_panel = wx.Simplebook( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, 0 )

		root.Add(self.grid_panel, 1, wx.EXPAND |wx.ALL, 5)

		tools = wx.BoxSizer(wx.VERTICAL)

		self.save_json = _apply_button_style(wx.Button(self, wx.ID_ANY, _(u"保存为JSON词库"), wx.DefaultPosition, wx.DefaultSize, wx.BORDER_NONE))
		tools.Add(self.save_json, 0, wx.ALL, 8)

		self.save_excel = _apply_button_style(wx.Button(self, wx.ID_ANY, _(u"保存为Excel词库"), wx.DefaultPosition, wx.DefaultSize, wx.BORDER_NONE))
		tools.Add(self.save_excel, 0, wx.ALL, 8)

		self.tip = wx.StaticText(self, wx.ID_ANY, _(u"提示:两种词库都可以\n进行本软件支持的所有操作，按需求选择。\nJSON词库：\n可以在左侧编辑框编辑，\n占用空间小\nExcel词库：\n可以在左侧编辑框\n或者其他Excel编辑器\n（如微软Excel，WPS等）编辑，\n占用空间较小"), wx.DefaultPosition, wx.DefaultSize, 0)
		self.tip.Wrap(-1)

		tools.Add(self.tip, 0, wx.ALL, 5)

		self.create_empty_excel_wordlib = _apply_button_style(wx.Button(self, wx.ID_ANY, _(u"生成Excel词库模板"), wx.DefaultPosition, wx.DefaultSize, wx.BORDER_NONE))
		tools.Add(self.create_empty_excel_wordlib, 0, wx.ALL, 8)

		self.tip2 = wx.StaticText(self, wx.ID_ANY, _(u"如果想完全在Excel中编辑词库\n请点击“生成Excel词库模板”\n在自动打开的文件管理器中\n找到需要编辑的Excel文件\n打开你的Excel编辑器即可编辑"), wx.DefaultPosition, wx.DefaultSize, 0)
		self.tip2.Wrap(-1)

		tools.Add(self.tip2, 0, wx.ALL, 5)


		root.Add(tools, 0, wx.EXPAND, 5)


		self.SetSizer( root )
		self.Layout()

		self.Centre(wx.BOTH)

	def __del__( self ):
		pass


#--------------------------------------------------------------------------
#  Class welcome_page
#---------------------------------------------------------------------------

class welcome_page ( wx.Panel ):

	def __init__(self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.Size( 800,460 ), style = wx.TAB_TRAVERSAL, name = wx.EmptyString):
		wx.Panel.__init__ (self, parent, id = id, pos = pos, size = size, style = style, name = name)

		self.SetBackgroundColour(wx.Colour(255, 255, 255))
		root = wx.BoxSizer(wx.VERTICAL)

		self.welcome_text = wx.StaticText(self, wx.ID_ANY, _(u"欢迎使用零听(ZeroListen)"), wx.DefaultPosition, wx.DefaultSize, 0)
		self.welcome_text.Wrap(-1)

		self.welcome_text.SetFont(wx.Font( 24, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, wx.EmptyString ))

		root.Add(self.welcome_text, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5)

		self.create_wordlib = _apply_button_style(wx.Button(self, wx.ID_ANY, _(u"创建新词句库"), wx.DefaultPosition, wx.DefaultSize, wx.BORDER_NONE))
		root.Add(self.create_wordlib, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 8)

		self.import_wordlib = _apply_button_style(wx.Button(self, wx.ID_ANY, _(u"导入新词句库"), wx.DefaultPosition, wx.DefaultSize, wx.BORDER_NONE))
		root.Add(self.import_wordlib, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 8)

		self.about = _apply_button_style(wx.Button(self, wx.ID_ANY, _(u"关于"), wx.DefaultPosition, wx.DefaultSize, wx.BORDER_NONE))
		root.Add(self.about, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 8)

		self.visual_settings = _apply_button_style(wx.Button(self, wx.ID_ANY, _(u"视觉设置"), wx.DefaultPosition, wx.DefaultSize, wx.BORDER_NONE))
		root.Add(self.visual_settings, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 8)


		self.SetSizer( root )
		self.Layout()

	def __del__( self ):
		pass


#--------------------------------------------------------------------------
#  Class workbar_page
#---------------------------------------------------------------------------

class workbar_page ( wx.Panel ):

	def __init__(self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.Size( 800,460 ), style = wx.TAB_TRAVERSAL, name = wx.EmptyString):
		wx.Panel.__init__ (self, parent, id = id, pos = pos, size = size, style = style, name = name)

		self.SetBackgroundColour(wx.Colour(255, 255, 255))
		root = wx.BoxSizer(wx.HORIZONTAL)

		wordbar = wx.BoxSizer(wx.VERTICAL)

		self.tip_check_words = wx.StaticText(self, wx.ID_ANY, _(u"选择导出词汇"), wx.DefaultPosition, wx.DefaultSize, 0)
		self.tip_check_words.Wrap(-1)

		self.tip_check_words.SetFont(wx.Font( 14, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, wx.EmptyString ))

		wordbar.Add(self.tip_check_words, 0, wx.ALL, 5)

		check_wordsChoices = []
		self.check_words = wx.CheckListBox(self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, check_wordsChoices, wx.LB_EXTENDED|wx.LB_NEEDED_SB)
		wordbar.Add(self.check_words, 1, wx.ALL|wx.EXPAND, 5)

		self.checkall = _apply_button_style(wx.Button(self, wx.ID_ANY, _(u"全选/取消全选"), wx.DefaultPosition, wx.DefaultSize, wx.BORDER_NONE))
		wordbar.Add(self.checkall, 0, wx.ALL, 8)


		root.Add(wordbar, 1, wx.EXPAND, 5)

		sidebar = wx.BoxSizer(wx.VERTICAL)

		self.output_wav = _apply_button_style(wx.Button(self, wx.ID_ANY, _(u"导出音频"), wx.DefaultPosition, wx.DefaultSize, wx.BORDER_NONE))
		sidebar.Add(self.output_wav, 0, wx.ALL, 8)

		self.output_html = _apply_button_style(wx.Button(self, wx.ID_ANY, _(u"导出html"), wx.DefaultPosition, wx.DefaultSize, wx.BORDER_NONE))
		sidebar.Add(self.output_html, 0, wx.ALL, 8)

		self.tip_output = wx.StaticText(self, wx.ID_ANY, _(u"提示：\n导出音频是\n导出所有词句独立\n的音频文件。\n导出html则是\n以网页的形式导出。\n能够导出一整个\n完整的播放器，\n可以在任何\n现代浏览器运行"), wx.DefaultPosition, wx.DefaultSize, 0)
		self.tip_output.Wrap(-1)

		sidebar.Add(self.tip_output, 0, wx.ALL, 5)

		self.output_audio_config = _apply_button_style(wx.Button(self, wx.ID_ANY, _(u"音频导出配置"), wx.DefaultPosition, wx.DefaultSize, wx.BORDER_NONE))
		sidebar.Add(self.output_audio_config, 0, wx.ALL, 8)


		root.Add(sidebar, 0, wx.EXPAND, 5)


		self.SetSizer( root )
		self.Layout()

	def __del__( self ):
		pass


#--------------------------------------------------------------------------
#  Class progress
#---------------------------------------------------------------------------

class progress ( wx.Dialog ):

	def __init__(self, parent):
		wx.Dialog.__init__ (self, parent, id = wx.ID_ANY, title = wx.EmptyString, pos = wx.DefaultPosition, size = wx.Size( 233,142 ), style = wx.DEFAULT_DIALOG_STYLE)

		self.SetSizeHints(wx.DefaultSize, wx.DefaultSize)

		root = wx.BoxSizer(wx.VERTICAL)

		self.progress_text = wx.StaticText(self, wx.ID_ANY, _(u"导出进度"), wx.DefaultPosition, wx.DefaultSize, 0)
		self.progress_text.Wrap(-1)

		root.Add(self.progress_text, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5)

		self.m_gauge1 = wx.Gauge(self, wx.ID_ANY, 100, wx.DefaultPosition, wx.DefaultSize, wx.GA_HORIZONTAL)
		self.m_gauge1.SetValue(0)
		root.Add(self.m_gauge1, 0, wx.ALL, 5)

		self.info = wx.StaticText(self, wx.ID_ANY, _(u"正在进行第{}项，预计还需时间为{}\n已完成{}% (完成项目数/全部项目数)"), wx.DefaultPosition, wx.DefaultSize, 0)
		self.info.Wrap(-1)

		root.Add(self.info, 0, wx.ALL, 5)


		self.SetSizer( root )
		self.Layout()

		self.Centre(wx.BOTH)

	def __del__( self ):
		pass


