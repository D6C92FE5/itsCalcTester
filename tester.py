# -*- coding: utf-8 -*-

import sys
import time
import subprocess
import random

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


import subprocess
import random

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
CalcKeyXp = set('0123456789.+-*/=←C±√') | \
          {'Backspace', 'CE', '1/x', '+/-', 'sqt'}
CalcKeyMap = {'←':'Backspace', '±':'+/-', '√':'sqt', }
CalcKeyMapXp = {'←':'Backspace', '±':'+/-', '√':'sqt', }
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
        elif "STATIC" in ClassName or "EDIT" in ClassName:
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

def InitCalcKeyHandleSysXp(hwnd):
    def Callback(hwnd, lParam=None):
        global CalcKey
        global CalcKeyHandleSys
        ClassName = GetClassNameByHwnd(hwnd)
        if "Button" in ClassName:
            s = GetWindowTextByHwnd(hwnd)
            if s in CalcKey:
                CalcKeyHandleSys[s] = hwnd
        elif "Edit" in ClassName:
            s = GetWindowTextByHwnd(hwnd)
            if s == "0. ":
                CalcKeyHandleSys['result'] = hwnd
        return True
    CallbackT = CFUNCTYPE(c_int, c_int)
    CallbackC = CallbackT(Callback)
    EnumChildWindows(hwnd, CallbackC)

def ClickButton(handle):
    SendMessage(handle, BM_CLICK, 0, 0)

path_system_calc = "calc.exe"
def GenerateTestData(input):
    calc = subprocess.Popen(path_system_calc)
    while True:
        WaitForInputIdleByPid(calc.pid)
        global CalcKeyHandleSys
        CalcKeyHandleSys = {}
        InitCalcKeyHandleSys(GetHwndByPid(calc.pid))
        if len(CalcKeyHandleSys) != 0:
            break
        time.sleep(0.1)

    for k, v in CalcKeyMap.items():
        if k not in CalcKeyHandleSys:
            CalcKeyHandleSys[k] = CalcKeyHandleSys[v]

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
        global CalcKeyHandle
        CalcKeyHandle = {}
        InitCalcKeyHandle(GetHwndByPid(calc.pid))
        if len(CalcKeyHandle) != 0:
            break
        time.sleep(0.1)

    for k, v in CalcKeyMap.items():
        if k not in CalcKeyHandle:
            CalcKeyHandle[k] = CalcKeyHandle[v]

    inputs = []
    isPass = True
    for x in testdata:
        ClickButton(CalcKeyHandle[x['input']])
        inputs.append(x['input'])
        output = GetWindowTextByHwnd(CalcKeyHandle['result'])
        if not IsResultEqual(output, x['output']):
            isPass = False
            print("测试没有通过")
            print("点击的按钮：", " ".join(inputs))
            print("正确的结果：", x['output'])
            print("实际的结果：", output)
            break
    if isPass:
        print("测试通过")
        print("点击的按钮：", " ".join(inputs))

    calc.terminate()

    return isPass

def IsResultEqual(a, b):
    if a == b:
        return True
    try:
        if (len(a) > 14 or len(b) > 14) and \
           (abs(1 - float(a) / float(b)) < 10e14):
            return True
    except:
        pass
    if '+/-' in CalcKey and a.strip(". ") == b.strip(". "):
        return True
    return False

def test_from_file():
    with open("testdata.txt", 'r', encoding='utf-8') as fp:
        testdata = [x.strip('\n') for x in fp.readlines()]

    testdata = [x.split() for x in testdata if len(x) > 0]

    test_count = 0
    pass_count = 0
    for x in testdata:
        test_count += 1
        print(x[0])
        data = GenerateTestData(x[1:])
        if TestCalc(sys.argv[1], data):
            pass_count += 1
        print()
    print("测试计数：", test_count)
    print("通过计数：", pass_count)

def test_from_rand():
    test_count = 0
    pass_count = 0
    for i in range(100):
        test_count += 1
        rand = []
        for x in range(100):
            rand.append(random.choice(list(CalcKey)))
        data = GenerateTestData(rand)
        if TestCalc(sys.argv[1], data):
            pass_count += 1
        print()
    print("测试计数：", test_count)
    print("通过计数：", pass_count)

def main():
    """global path_system_calc
    path_system_calc = r"D:\temp\calc.exe"
    global CalcKey, CalcKeyXp
    CalcKey = CalcKeyXp
    global InitCalcKeyHandleSys, InitCalcKeyHandleSysXp
    InitCalcKeyHandleSys = InitCalcKeyHandleSysXp"""
    test_from_rand()
    #test_from_file()

main()
