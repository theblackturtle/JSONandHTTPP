# -*- coding:utf-8 -*-
# Author: Vulkey_Chen
# Blog: gh0st.cn
# Team: MSTSEC

import json
import re

from burp import IBurpExtender, ITab
from javax.swing import JPanel, JButton, JTextArea, JScrollPane, BorderFactory
from java.awt import BorderLayout, GridLayout


class BurpExtender(IBurpExtender, ITab):
    def registerExtenderCallbacks(self, callbacks):
        print "JSON&HTTPP by [Vulkey_Chen]\nBlog: gh0st.cn\nTeam: MSTSEC"
        self._cb = callbacks
        self._hp = callbacks.getHelpers()
        self._cb.setExtensionName("JSON&HTTPP")
        self.mainPanel = JPanel()
        self.mainPanel.setLayout(BorderLayout())

        self.jsonTextArea = JTextArea(20, 0)
        self.jsonTextArea.setLineWrap(True)

        self.dictTextArea = JTextArea()
        self.dictTextArea.setLineWrap(True)

        self.keyTextArea = JTextArea()
        self.keyTextArea.setLineWrap(True)

        self.valueTextArea = JTextArea()
        self.valueTextArea.setLineWrap(True)

        self.resultPanel = JPanel()
        # self.resultPanel.setLayout(BorderLayout())
        self.resultPanel.layout = GridLayout(1, 3)

        self.jsonTextWrapper = JPanel()
        self.jsonTextWrapper.setLayout(BorderLayout())
        self.jsonTextWrapper.border = BorderFactory.createTitledBorder("Input")
        self.dictTextWrapper = JPanel()
        self.dictTextWrapper.setLayout(BorderLayout())
        self.dictTextWrapper.border = BorderFactory.createTitledBorder("Output")
        self.keyTextWrapper = JPanel()
        self.keyTextWrapper.setLayout(BorderLayout())
        self.keyTextWrapper.border = BorderFactory.createTitledBorder("Keys")
        self.valueTextWrapper = JPanel()
        self.valueTextWrapper.setLayout(BorderLayout())
        self.valueTextWrapper.border = BorderFactory.createTitledBorder("Values")

        self.jsonScrollPane = JScrollPane(self.jsonTextArea)
        self.dictScrollPane = JScrollPane(self.dictTextArea)
        self.valueScrollPane = JScrollPane(self.valueTextArea)
        self.keyScrollPane = JScrollPane(self.keyTextArea)

        self.jsonTextWrapper.add(self.jsonScrollPane, BorderLayout.CENTER)
        self.dictTextWrapper.add(self.dictScrollPane, BorderLayout.CENTER)
        self.keyTextWrapper.add(self.keyScrollPane, BorderLayout.CENTER)
        self.valueTextWrapper.add(self.valueScrollPane, BorderLayout.CENTER)

        self.resultPanel.add(self.dictTextWrapper, BorderLayout.WEST)
        self.resultPanel.add(self.keyTextWrapper, BorderLayout.CENTER)
        self.resultPanel.add(self.valueTextWrapper, BorderLayout.EAST)

        self.mainPanel.add(self.jsonTextWrapper, BorderLayout.NORTH)
        self.mainPanel.add(self.resultPanel, BorderLayout.CENTER)

        self.beautifyButton_1 = JButton("JSON2HTTPP", actionPerformed=self.onClick1)
        self.beautifyButton_2 = JButton("HTTPP2JSON", actionPerformed=self.onClick2)
        self.clearButton = JButton("CLEAR", actionPerformed=self.onClear)

        self.buttons = JPanel()
        self.buttons.add(self.beautifyButton_1, BorderLayout.CENTER)
        self.buttons.add(self.beautifyButton_2, BorderLayout.CENTER)
        self.buttons.add(self.clearButton, BorderLayout.CENTER)

        self.mainPanel.add(self.buttons, BorderLayout.SOUTH)

        self._cb.customizeUiComponent(self.mainPanel)
        self._cb.addSuiteTab(self)

    def onClick1(self, event):
        _jsontext = self.jsonTextArea.getText().strip()
        try:
            _jsontext = json.loads(re.search(r"\({.*?}\)", _jsontext).group().replace("(", "").replace(")", ""))
        except:
            _jsontext = json.loads(_jsontext)
        self._result = []
        # resultDict format: ["aa=bb","cc=ddd"]
        resultDict = self.json2dict(_jsontext)
        self.dictTextArea.append("\n".join(resultDict))
        keyList = set()
        valueList = set()
        for result in resultDict:
            key, value = result.split("=")[0], result.split("=")[1]
            if len(key) > 0:
                keyList.add(key)
            if len(value) > 0:
                valueList.add(value)
        self.keyTextArea.append("\n".join(keyList))
        self.valueTextArea.append("\n".join(valueList))

        self.dictTextArea.append("\n")
        self.keyTextArea.append("\n")
        self.valueTextArea.append("\n")

    def onClick2(self, event):
        _jsontext = self.jsonTextArea.getText().strip()
        _res = []
        keyList = set()
        valueList = set()
        for i in _jsontext.split("&"):
            args = i.split("=")
            for x in args:
                _res.append(x)
            if len(args[0]) > 0:
                keyList.add(args[0])
            if len(args[1]) > 0:
                valueList.add(args[1])
        self.dictTextArea.append(json.dumps(dict(zip(_res[0::2], _res[1::2]))))
        self.keyTextArea.append("\n".join(keyList))
        self.valueTextArea.append("\n".join(valueList))

        self.dictTextArea.append("\n")
        self.keyTextArea.append("\n")
        self.valueTextArea.append("\n")

    def onClear(self, event):
        self.dictTextArea.setText("")
        self.keyTextArea.setText("")
        self.valueTextArea.setText("")

    def json2dict(self, _jsontext):
        keyValue = ""
        if isinstance(_jsontext, dict):
            for key in _jsontext.keys():
                keyValue = _jsontext.get(key)
                if isinstance(keyValue, dict):
                    self.json2dict(keyValue)
                elif isinstance(keyValue, list):
                    for json_array in keyValue:
                        self.json2dict(json_array)
                else:
                    if type(keyValue) is int or type(keyValue) == long or type(keyValue) == str:
                        self._result.append(str(key) + "=" + str(keyValue))
                    elif type(keyValue) is bool:
                        self._result.append(str(key) + "=" + str(int(keyValue)))
                    elif type(keyValue) == type(None):
                        self._result.append(str(key) + "=" + "")
                    else:
                        self._result.append(str(key) + "=" + keyValue)
        elif isinstance(_jsontext, list):
            for _jsontext_array in _jsontext:
                self.json2dict(_jsontext_array)
        return self._result

    def getTabCaption(self):
        return "JSON&HTTPP"

    def getUiComponent(self):
        return self.mainPanel
