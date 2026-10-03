# -*- coding: utf-8 -*-

#--------------------------------------------------------------------------
# Python code generated with wxFormBuilder (version 3.9.0 Jun 14 2020)
# http://www.wxformbuilder.org/
#
# PLEASE DO *NOT* EDIT THIS FILE!
#--------------------------------------------------------------------------

import wx
import wx.xrc

import gettext
_ = gettext.gettext

REPO_SOURSE = {
	"mirror":"https://gitee.com/loser123zbx/ZeroListen/repository/archive/master.zip",
	"host":"https://github.com/Loser123zbx/ZeroListen/archive/refs/heads/master.zip"
}
"""
repo structure:

ZeroListen/
├── .gitignore
├── LICENSE
├── README.md
├── 用户手册.md
├── src/
│   ├── all_panels.py
│   ├── build.bat
│   ├── config.json
│   ├── download_source.json
│   ├── html_player.py
│   ├── installer.py
│   ├── main.py
│   ├── package.json
│   ├── tts_cli.js
│   ├── tts.js
│   ├── tts.py
│   ├── zerolisten.spec
│   └── wxProjects/
│       ├── panels.fbp
│       └── ZeroListenInstaller.fbp

"""

#--------------------------------------------------------------------------
#  Class MyPanel1
#---------------------------------------------------------------------------

class MyPanel1 ( wx.Panel ):

	def __init__(self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.Size( 800,460 ), style = wx.TAB_TRAVERSAL, name = wx.EmptyString):
		wx.Panel.__init__ (self, parent, id = id, pos = pos, size = size, style = style, name = name)

		self.SetBackgroundColour(wx.Colour( 255, 255, 255 ))

		root = wx.BoxSizer(wx.VERTICAL)

		self.head_text = wx.StaticText(self, wx.ID_ANY, _(u"正在安装ZeroListen"), wx.DefaultPosition, wx.Size( 2000,30 ), 0)
		self.head_text.Wrap(-1)

		self.head_text.SetFont(wx.Font( 15, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, "黑体" ))
		self.head_text.SetForegroundColour(wx.Colour( 255, 255, 255 ))
		self.head_text.SetBackgroundColour(wx.Colour( 25, 25, 112 ))

		root.Add(self.head_text, 0, 0, 5)

		info_bar = wx.BoxSizer(wx.HORIZONTAL)

		self.info_box = wx.TextCtrl(self, wx.ID_ANY, _(u"零听 ZeroListen\n本地离线中/英文词句 TTS 批量生成工具\nhttps://github.com/Loser123zbx/ZeroListen\n\n零听（ZeroListen）是一款运行在 Windows 上的桌面软件，用于把词句库（单词、短语、句子）批量合成为真人级语音，并支持两种导出方式：独立音频文件（WAV）和可跟读的网页播放器（HTML）。所有语音合成均在本地完成，不调用任何云端语音接口；同时内置离线英译中能力（弃用），可自动为词句补充中文释义。\n\n纯本地离线：语音由本地 ONNX 模型（Kokoro-82M）+ kokoro-js 引擎合成，不上传任何文本到云端。\n中英文双语：内置 36 种声音（美音、英音、普通话，男女声齐全）。\n批量生成：一次可为整库或勾选的任意词句批量生成音频。\n网页跟读播放器：导出一个自包含的 HTML 播放器，支持跟读模式、连播、变速等。\n\nMIT LICENSE\nCopyright © 2026 Loser_123_zero(Loser_123_zbx/Stanzero_)\n\nPermission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:\n\nThe above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.\n\nTHE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE."), wx.DefaultPosition, wx.DefaultSize, wx.TE_AUTO_URL|wx.TE_MULTILINE|wx.TE_READONLY)
		info_bar.Add(self.info_box, 1, wx.ALL|wx.EXPAND, 5)


		root.Add(info_bar, 1, wx.EXPAND, 5)

		under_bar = wx.BoxSizer(wx.HORIZONTAL)

		self.help = wx.Button(self, wx.ID_ANY, _(u"获取帮助"), wx.DefaultPosition, wx.DefaultSize, wx.BORDER_NONE)
		self.help.SetFont(wx.Font( 12, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, "黑体" ))
		self.help.SetForegroundColour(wx.Colour( 255, 255, 255 ))
		self.help.SetBackgroundColour(wx.Colour( 70, 120, 180 ))

		under_bar.Add(self.help, 0, wx.ALL, 5)


		under_bar.Add((0, 0), 1, wx.EXPAND, 5)

		self.setup = wx.Button(self, wx.ID_ANY, _(u"安装"), wx.DefaultPosition, wx.DefaultSize, wx.BORDER_NONE)
		self.setup.SetFont(wx.Font( 12, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, "黑体" ))
		self.setup.SetForegroundColour(wx.Colour( 255, 255, 255 ))
		self.setup.SetBackgroundColour(wx.Colour( 70, 120, 180 ))

		under_bar.Add(self.setup, 0, wx.ALL, 5)

		self.cancel = wx.Button(self, wx.ID_ANY, _(u"取消"), wx.DefaultPosition, wx.DefaultSize, wx.BORDER_NONE)
		self.cancel.SetFont(wx.Font( 12, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, "黑体" ))
		self.cancel.SetForegroundColour(wx.Colour( 255, 255, 255 ))
		self.cancel.SetBackgroundColour(wx.Colour( 70, 120, 180 ))

		under_bar.Add(self.cancel, 0, wx.ALL, 5)


		root.Add(under_bar, 0, wx.EXPAND, 5)


		self.SetSizer( root )
		self.Layout()

	def __del__( self ):
		pass


#--------------------------------------------------------------------------
#  Class install_time
#---------------------------------------------------------------------------

class install_time ( wx.Panel ):

	def __init__(self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.Size( 800,460 ), style = wx.TAB_TRAVERSAL, name = wx.EmptyString):
		wx.Panel.__init__ (self, parent, id = id, pos = pos, size = size, style = style, name = name)

		self.SetBackgroundColour(wx.Colour( 255, 255, 255 ))

		root = wx.BoxSizer(wx.VERTICAL)

		self.process = wx.Gauge(self, wx.ID_ANY, 100, wx.DefaultPosition, wx.Size( 30,25 ), wx.GA_HORIZONTAL)
		self.process.SetValue(0)
		self.process.SetForegroundColour(wx.Colour( 77, 146, 249 ))
		self.process.SetBackgroundColour(wx.Colour( 55, 149, 253 ))

		root.Add(self.process, 0, wx.ALL|wx.EXPAND, 5)

		self.info_box = wx.TextCtrl(self, wx.ID_ANY, _(u"正在安装ZeroListen:\n"), wx.DefaultPosition, wx.DefaultSize, wx.TE_MULTILINE)
		root.Add(self.info_box, 1, wx.ALL|wx.EXPAND, 5)

		under_bar = wx.BoxSizer(wx.HORIZONTAL)

		self.cancel = wx.Button(self, wx.ID_ANY, _(u"取消"), wx.DefaultPosition, wx.DefaultSize, wx.BORDER_NONE)
		self.cancel.SetFont(wx.Font( 12, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, "黑体" ))
		self.cancel.SetForegroundColour(wx.Colour( 255, 255, 255 ))
		self.cancel.SetBackgroundColour(wx.Colour( 70, 120, 180 ))

		under_bar.Add(self.cancel, 0, wx.ALL, 5)


		root.Add(under_bar, 0, 0, 5)


		self.SetSizer( root )
		self.Layout()

	def __del__( self ):
		pass

