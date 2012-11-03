# -*- coding: utf-8 -*-

import sys
import time
import subprocess

from ctypes import *
EnumChildWindows = windll.User32.EnumChildWindows
FindWindow = windll.User32.FindWindowW
SendMessage = windll.User32.SendMessageW
GetClassName = windll.User32.GetClassNameW
GetWindowThreadProcessId = windll.User32.GetWindowThreadProcessId
EnumWindows = windll.User32.EnumWindows
WaitForInputIdle = windll.User32.WaitForInputIdle
OpenProcess = windll.Kernel32.OpenProcess

WM_GETTEXT = 0x000D
BM_CLICK = 0x00F5
PROCESS_QUERY_INFORMATION = 0x0400

buffer = create_string_buffer(1000)
def GetWindowTextByHwnd(hwnd):
    global buffer
    l = SendMessage(hwnd, WM_GETTEXT, int(len(buffer) / 2), buffer)
    return buffer[:l * 2].decode('utf-16')
def GetClassNameByHwnd(hwnd):
    global buffer
    l = GetClassName(hwnd, buffer, int(len(buffer) / 2))
    return buffer[:l * 2].decode('utf-16')

def GetHwndByPid(pid):
    def Callback(hwnd, lParam=None):
        pidT = c_int()
        GetWindowThreadProcessId(hwnd, byref(pidT))
        if pidT.value == pid:
            nonlocal result
            result = hwnd
            return False
        return True
    CallbackT = CFUNCTYPE(c_int, c_int)
    CallbackC = CallbackT(Callback)
    result = 0
    EnumWindows(CallbackC)
    return result

def WaitForInputIdleByPid(pid):
    hProcess = OpenProcess(PROCESS_QUERY_INFORMATION, False, pid)
    WaitForInputIdle(hProcess, 10000)

CalcKey = set('0123456789.+-*/=←C±√') | {'CE', '1/x'}
CalcKeyHandle = {}
def InitCalcKeyHandle(hwnd):
    def Callback(hwnd, lParam=None):
        global CalcKey
        global CalcKeyHandle
        ClassName = GetClassNameByHwnd(hwnd)
        if "BUTTON" in ClassName:
            s = GetWindowTextByHwnd(hwnd)
            if s in CalcKey:
                CalcKeyHandle[s] = hwnd
        elif "STATIC" in ClassName:
            s = GetWindowTextByHwnd(hwnd)
            if s == "0":
                CalcKeyHandle['result'] = hwnd
        return True
    CallbackT = CFUNCTYPE(c_int, c_int)
    CallbackC = CallbackT(Callback)
    EnumChildWindows(hwnd, CallbackC)

CalcKeyHandleSys = {}
def InitCalcKeyHandleSys(hwnd):
    def Callback(hwnd, lParam=None):
        ClassName = GetClassNameByHwnd(hwnd)
        if "Button" in ClassName:
            handles.append(hwnd)
        elif "Static" in ClassName:
            s = GetWindowTextByHwnd(hwnd)
            if s == "0":
                handles.append(hwnd)
        return True

    CallbackT = CFUNCTYPE(c_int, c_int)
    CallbackC = CallbackT(Callback)
    handles = []
    EnumChildWindows(hwnd, CallbackC)
    keys = ['result',
            'MC', '←', '7', '4', '1', '0',
            'MR', 'CE', '8', '5', '2',
            'MS', 'C', '9', '6', '3', '.',
            'M+', '±', '/', '*', '-', '+',
            'M-', '√', '%', '1/x', '=']
    global CalcKeyHandleSys
    CalcKeyHandleSys = dict(zip(keys, handles))

def ClickButton(handle):
    SendMessage(handle, BM_CLICK, 0, 0)

def GenerateTestData(input):
    calc = subprocess.Popen("calc.exe")
    while True:
        WaitForInputIdleByPid(calc.pid)
        InitCalcKeyHandleSys(GetHwndByPid(calc.pid))
        if len(CalcKeyHandleSys) != 0:
            break
        time.sleep(0.1)

    data = []
    for x in input:
        ClickButton(CalcKeyHandleSys[x])
        result = GetWindowTextByHwnd(CalcKeyHandleSys['result'])
        data.append({'input':x, 'output':result})
    calc.terminate()
    return data

def TestCalc(path, testdata):
    calc = subprocess.Popen(path)
    while True:
        WaitForInputIdleByPid(calc.pid)
        InitCalcKeyHandle(GetHwndByPid(calc.pid))
        if len(CalcKeyHandle) != 0:
            break
        time.sleep(0.1)

    ClickButton(CalcKeyHandle['1'])
    print(GetWindowTextByHwnd(CalcKeyHandle['result']))
    ClickButton(CalcKeyHandle['0'])
    print(GetWindowTextByHwnd(CalcKeyHandle['result']))
    ClickButton(CalcKeyHandle['+'])
    print(GetWindowTextByHwnd(CalcKeyHandle['result']))
    ClickButton(CalcKeyHandle['2'])
    print(GetWindowTextByHwnd(CalcKeyHandle['result']))
    ClickButton(CalcKeyHandle['='])
    print(GetWindowTextByHwnd(CalcKeyHandle['result']))

    calc.terminate()

def main():
    #TestCalc(r"C:\project\AlCalc\AlCalc\bin\Release\AlCalc.exe", None)#sys.argv[1]

    GenerateTestData(list("1.0+2="))

main()
