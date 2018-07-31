from __future__ import print_function
import wx 
import pyHook 
import wx
import GUI
import time
import json
import sys
import netifaces
import json
import threading
from sys import platform

class ActivityFrame:
    seqCount = 0
    def __init__(self, events, window, inactive, network):
        self.events = events
        self.window = window
        self.inactive = inactive
        self.network = network
        ActivityFrame.seqCount += 1
        self.seqCount = ActivityFrame.seqCount

    def windowDetails(self):
        return self.window

    def getEvents(self):
        return self.events

    def getActiveNetworks(self):
        return self.events

    def getInactiveWindows(self):
        return self.events

def get_active_networks():
    rst = {}
    iface_prefix = ''
    for ifacename in netifaces.interfaces():
        if not ifacename.startswith(iface_prefix):
            continue
        addrs = netifaces.ifaddresses(ifacename)
        if netifaces.AF_INET in addrs and netifaces.AF_LINK in addrs:
            ips = [addr['addr'] for addr in addrs[netifaces.AF_INET]]
            for ip in ips:
                try:
                    reg = wr.ConnectRegistry(None, wr.HKEY_LOCAL_MACHINE)
                    reg_key = wr.OpenKey(reg, r'SYSTEM\CurrentControlSet\Control\Network\{4D36E972-E325-11CE-BFC1-08002BE10318}')
                    reg_subkey = wr.OpenKey(reg_key, ifacename + r'\Connection')
                    ifacename = wr.QueryValueEx(reg_subkey, 'Name')[0]
                    rst[ifacename] = {'INET': addrs[netifaces.AF_INET],
                                      'LINK': addrs[netifaces.AF_LINK]}
                except:
                    pass
    networks = []
    for i in rst:
        nobj = {}
        nobj['type'] = i
        nobj['ips'] = rst[i]["INET"]
        
        nobj['location'] = "unknown"
        for k in known_networks:
            for j in nobj['ips']:
                if j['addr'].startswith(k):
                    nobj['location'] = known_networks[k]
        networks.append(nobj)
    return networks

def prettyprint(frame):
    jframe = {}
    jframe['id'] = frame.seqCount
    line=frame.window['name'].decode('utf-8','ignore').encode("utf-8")
    jframe['title'] = line
    jframe['process'] = frame.window['process']
    jframe['events'] = frame.events
    jframe['network'] = frame.network
    jframe['inactive_windows'] = []
    
    if '\x95' in jframe['title']:
        jframe['title'] = "Unsaved Sublime Text File"
    
    for i in frame.inactive:
        i=i.decode('utf-8','ignore').encode("utf-8")
        if '\x95' in i:
            jframe['inactive_windows'].append("Unsaved Sublime Text File")
        else:
            jframe['inactive_windows'].append(i)
    
    if jframe['title'] in jframe['inactive_windows']:
        jframe['inactive_windows'].remove(jframe['title'])
    frames = []
    try:
        with open("activity_frames.json", mode='r') as framesjson:
            if framesjson:
                frames = json.load(framesjson)
            else:
                frames = []
            print(framesjson)
    except Exception as e:
        if "No such file" in str(e):
            with open('activity_frames.json', mode='w') as f:
                json.dump([], f)
        else:
            print(e)
    try:
        with open("activity_frames.json", mode='w') as framesjson:
            frames.append(jframe)
            json.dump(frames, framesjson)
    except Exception as e:
        print(e)
        pass

class ActivityFramesGUI(GUI.GUI): 
    def __init__(self,parent): 
        GUI.GUI.__init__(self,parent) 
        self.start()
        wx.EVT_CLOSE(self, self.OnClose) 

    def start(self):
        self.activity_frame = ActivityFrame([],{},[],[])
        self.sleepstate = False
        self.watch_idle_time()
        self.hm = pyHook.HookManager() 
        self.hm.KeyDown = self.OnKeyboardEvent 
        self.hm.HookKeyboard() 
        self.hm.SubscribeMouseAllButtonsDown(self.OnMouseEvent)
        self.hm.HookMouse()
        toaster.show_toast("ActivityFrames Active",
                   "Inputs are monitored. Use snooze option to pause (or) exit to quit the app.",
                   icon_path='python.ico',
                   duration=5,
                   threaded=True)
        # while toaster.notification_active(): time.sleep(0.1)
        # self.hm.MouseLeftDown=self.OnKeyboardEvent 
        # self.hm.HookMouse()

    def snooze(self,event): 
        num = int(self.m_spinCtrl2.GetValue()) 
        toaster.show_toast("ActivityFrames Paused",
                   "Inputs are not monitored for "+str(num)+" minutes. This will auto-resume with a notification",
                   icon_path='python.ico',
                   duration=5,
                   threaded=True)
        activity_frame = ActivityFrame([],{},[],[])
        activity_frame.window['name'] = "snooze"
        activity_frame.window['process'] = 'snooze'
        activity_frame.events = [(num,time.time())]
        activity_frame.inactive = get_inactive_windows()
        activity_frame.network = get_active_networks()
        activity_frames.append(activity_frame)
        prettyprint(activity_frame)
        del self.hm 
        self.snooze = threading.Timer(num*60.0, self.start)
        self.snooze.start()

    def exit(self,event): 
        self.OnClose(event)

    def OnGetAO(self, event): 
        self.tc.Value+=event.MessageName+"\n" 

    def OnKeyboardEvent(self, event): 
        global running
        global word
        global activity_frame
        self.sleepstate = False
        hwnd = win32gui.FindWindow(None, event.WindowName)
        threadid,pid = win32process.GetWindowThreadProcessId(hwnd)
        handle = win32api.OpenProcess(win32con.PROCESS_QUERY_INFORMATION | win32con.PROCESS_VM_READ, False, pid)
        proc_name = win32process.GetModuleFileNameEx(handle, 0)
        # print(proc_name)
        if self.activity_frame.window == {}:
            if 'x95' in event.WindowName:
                event.WindowName = "Unsaved Sublime Text File"
            self.activity_frame.window['name'] = event.WindowName
            # print(self.activity_frame.window['name'])
            self.activity_frame.window['process'] = proc_name
        
        if proc_name!=self.activity_frame.window['process']:
            if word!='':
                self.activity_frame.events.append((word,time.time()))
            word = ''
            self.activity_frame.inactive = get_inactive_windows()
            self.activity_frame.network = get_active_networks()
            activity_frames.append(self.activity_frame)
            prettyprint(self.activity_frame)
            self.activity_frame = ActivityFrame([],{},[],[])
        
        if event.Ascii == 27:
            if word!='':
                self.activity_frame.events.append((word,time.time()))
                self.activity_frame.inactive = get_inactive_windows()
                self.activity_frame.network = get_active_networks()
                activity_frames.append(self.activity_frame)
                prettyprint(self.activity_frame)
            # del activity_frame
            # activity_frame = ActivityFrame([],{})
            # print(activity_frames[0].window)
            exit()
        elif event.Ascii == 32 or event.Ascii == 13 or event.Ascii == 9:
            if word!='':
                self.activity_frame.events.append((word,time.time()))
            word = ''
        else:
            word+=event.Key

        return True
        wx.CallAfter(self.OnGetAO, event) 

    def OnMouseEvent(self, event):
        # called when mouse events are received
        # print('MessageName:',event.MessageName)
        # print('Message:',event.Message)
        # print('Time:',event.Time)
        # print('Window:',event.Window)
        # print('WindowName:',event.WindowName)
        # print('Position:',event.Position)
        # print('Wheel:',event.Wheel)
        # print('Injected:',event.Injected)
        # print('---')

        global running
        global word
        global activity_frame
        self.sleepstate = False

        if event.WindowName == 'Running applications':
            proc_name = 'Taskbar'
        elif event.WindowName == 'Exit':
            proc_name = 'ActivityFrames Exit'
        elif event.WindowName == 'Activity Frames':
            proc_name = 'activity_frames.exe'
        elif event.WindowName == 'Chrome Legacy Window':
            proc_name = 'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe'
        else:
            hwnd = win32gui.FindWindow(None, event.WindowName)
            threadid,pid = win32process.GetWindowThreadProcessId(hwnd)
            handle = win32api.OpenProcess(win32con.PROCESS_QUERY_INFORMATION | win32con.PROCESS_VM_READ, False, pid)
            proc_name = win32process.GetModuleFileNameEx(handle, 0)
            # print(proc_name)            
        

        if word!='':
            self.activity_frame.events.append((word,time.time()))
            word = ''

        if self.activity_frame.window != None and self.activity_frame.window != {}:
            # print(self.activity_frame.window)
            if proc_name == self.activity_frame.window['process']:
                print("appending")
                self.activity_frame.events.append(((event.MessageName,event.Position),time.time()))
            else:
                print("writing")
                if self.activity_frame.events != []:
                    self.activity_frame.inactive = get_inactive_windows()
                    self.activity_frame.network = get_active_networks()
                    prettyprint(self.activity_frame)
                    self.activity_frame = ActivityFrame([],{},[],[])

        else:
            print("creating")
            self.activity_frame = ActivityFrame([],{},[],[])
            self.activity_frame.window['name'] = event.WindowName
            self.activity_frame.window['process'] = proc_name
            self.activity_frame.events.append(((event.MessageName,event.Position),time.time()))
            self.activity_frame.inactive = get_inactive_windows()
            self.activity_frame.network = get_active_networks()

            
        print("new"+proc_name)
        # print("existing"+self.activity_frame.window['process'])

        return True
        wx.CallAfter(self.OnGetAO, event) 
    
    def watch_idle_time(self):
        global lasttime
        global idle_time
        import win32api
        self.timer = threading.Timer(1.0, self.watch_idle_time)
        self.timer.daemon = True
        self.timer.start()
        liinfo = win32api.GetLastInputInfo()
        if lasttime is None: 
            lasttime = liinfo
        if lasttime != liinfo:
            if(idle_time>=60):    
                activity_frame = ActivityFrame([],{},[],[])
                activity_frame.window['name'] = "idle"
                activity_frame.window['process'] = 'idle'
                activity_frame.events = [(idle_time,time.time())]
                activity_frame.inactive = get_inactive_windows()
                activity_frame.network = get_active_networks()
                activity_frames.append(activity_frame)
                prettyprint(activity_frame)
            lasttime = liinfo
            idle_time = 0
        else:
            idle_time = (win32api.GetTickCount() - liinfo) / 1000.0

    def OnClose(self, event): 
        global activity_frame
        toaster.show_toast("Terminating ActivityFrames",
                   "Click on the application file to start again.",
                   icon_path='python.ico',
                   duration=2,
                   threaded=True)
        print(self.activity_frame.events)
        if self.activity_frame.events!=[] and self.activity_frame.window!={}:
            activity_frames.append(self.activity_frame)
            prettyprint(self.activity_frame)

        activity_frame = ActivityFrame([],{},[],[])
        activity_frame.window['name'] = "close"
        activity_frame.window['process'] = 'close'
        activity_frame.events = [(None,time.time())]
        activity_frame.inactive = get_inactive_windows()
        activity_frame.network = get_active_networks()
        activity_frames.append(activity_frame)
        prettyprint(activity_frame)
        try:
            del self.hm 
            del self.timer
            del self.snooze
            self.Destroy() 
        except:
            self.Destroy()

if __name__ == '__main__': 
    if platform == "win32":
        from ctypes import Structure, windll, c_uint, sizeof, byref
        import win32gui
        import win32process
        import win32api
        import win32con
        import _winreg as wr
        from win10toast import ToastNotifier
        import pythoncom, pyHook
        lasttime = None
        idle_time = 0
        toaster = ToastNotifier()

        def callback(hwnd, strings):
            if win32gui.IsWindowVisible(hwnd):
                window_title = win32gui.GetWindowText(hwnd)
                left, top, right, bottom = win32gui.GetWindowRect(hwnd)
                if window_title and right-left and bottom-top:
                    strings.append('{}'.format(window_title))
            return True

        def get_inactive_windows():
            win_list = [] 
            win32gui.EnumWindows(callback, win_list)
            return win_list


        class LASTINPUTINFO(Structure):
            _fields_ = [
                ('cbSize', c_uint),
                ('dwTime', c_uint),
            ]

        def get_idle_duration():
            lastInputInfo = LASTINPUTINFO()
            lastInputInfo.cbSize = sizeof(lastInputInfo)
            windll.user32.GetLastInputInfo(byref(lastInputInfo))
            millis = windll.kernel32.GetTickCount() - lastInputInfo.dwTime
            return millis / 1000.0

        events = []
        window = {}
        inactive = []
        network = []
        activity_frame = ActivityFrame(events, window, inactive, network)
        activity_frames = []
        word = ''
        with open("known_networks.json", mode='r') as networksjson:
            if networksjson:
                known_networks = json.load(networksjson)
            else:
                known_networks = []
            print(networksjson)

        
    app = wx.App(0) 
    frame = ActivityFramesGUI(None) 
    app.SetTopWindow(frame) 
    frame.Show() 
    app.MainLoop()