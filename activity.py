from __future__ import print_function
import wx
import GUI
import time
import json
import sys
import netifaces
import json
import threading
from sys import platform

if platform == "win32":
    from ctypes import Structure, windll, c_uint, sizeof, byref
    import win32gui
    import win32process
    import win32api
    import win32con
    import _winreg as wr

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

elif platform == "linux" or platform =="linux2":
    import pyxhook
    def get_inactive_windows():
        win_list = [] 
        return win_list

class ActivityFramesGUI(GUI.GUI): 
   def __init__(self,parent): 
      GUI.GUI.__init__(self,parent)  
		
   def snooze(self,event): 
      num = int(self.m_textCtrl1.GetValue()) 
      self.m_textCtrl2.SetValue (str(num*num)) 

   def exit(self,event): 
      num = int(self.m_textCtrl1.GetValue()) 
      self.m_textCtrl2.SetValue (str(num*num))  

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
    # networks = {}
    # networks['ipv4'] = ipv4()
    # interfaces = netifaces.interfaces()
    # for interface in interfaces:
    #     networks[interface] = netifaces.ifaddresses(interface)
    # return networks

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

#     import subprocess
#     import re
#     proc = subprocess.check_output("ipconfig" )
#     print("\n".join(re.findall(r"(?<=IPv4 Address. . . . . . . . . . . : )(\d+\.\d+\.\d+\.\d+)",proc)))
#     print(re.findall(r"(?<=Connection-specific DNS Suffix  . : )(.+)",proc))
#     networks['type'] = 
#     networks['ipv4'] = re.findall(r"(?<=IPv4 Address. . . . . . . . . . . : )(\d+\.\d+\.\d+\.\d+)",proc)
#     networks['dns_suffixes'] = re.findall(r"(?<=Connection-specific DNS Suffix  . : )([a-z].+)",proc)
#     return networks

# def prettyprint(frames):
#     jframes = []
#     for frame in frames:
#         jframe = {}
#         jframe['id'] = frame.seqCount
#         jframe['title'] = frame.window['name']
#         jframe['process'] = frame.window['process']
#         jframe['events'] = frame.events
#         print(json.dumps(jframe))
		# print("Sequence ID: "+str(frame.seqCount))
		# print("Window Title"+str(frame.window['name'])+"\nProcess: "+str(frame.window['process']))
		# print("Events: "+str(frame.events)+"\n\n")

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

    # print(json.dumps(jframe))
    # sys.stdout.flush()

def OnKeyboardEvent(event):
    global running
    global word
    global activity_frame
    
    hwnd = win32gui.FindWindow(None, event.WindowName)
    threadid,pid = win32process.GetWindowThreadProcessId(hwnd)
    handle = win32api.OpenProcess(win32con.PROCESS_QUERY_INFORMATION | win32con.PROCESS_VM_READ, False, pid)
    proc_name = win32process.GetModuleFileNameEx(handle, 0)

    if activity_frame.events == [] and activity_frame.window == {}:
        if 'x95' in event.WindowName:
            event.WindowName = "Unsaved Sublime Text File"
        activity_frame.window['name'] = event.WindowName
        # print(activity_frame.window['name'])
        activity_frame.window['process'] = proc_name
    
    if proc_name!=activity_frame.window['process']:
        if word!='':
            activity_frame.events.append((word,time.time()))
        word = ''
        activity_frame.inactive = get_inactive_windows()
        activity_frame.network = get_active_networks()
        activity_frames.append(activity_frame)
        prettyprint(activity_frame)
        del activity_frame
        activity_frame = ActivityFrame([],{},[],[])
    
    if event.Ascii == 27:
        if word!='':
            activity_frame.events.append((word,time.time()))
            activity_frame.inactive = get_inactive_windows()
            activity_frame.network = get_active_networks()
            activity_frames.append(activity_frame)
            prettyprint(activity_frame)
        # del activity_frame
        # activity_frame = ActivityFrame([],{})
        # print(activity_frames[0].window)
        exit()
    elif event.Ascii == 32 or event.Ascii == 13 or event.Ascii == 9:
        if word!='':
            activity_frame.events.append((word,time.time()))
        word = ''
    else:
        word+=event.Key

    return True

def ipv4():
        """ Get all IPv4 addresses for all interfaces. """
        try:
            from netifaces import interfaces, ifaddresses, AF_INET
            # to not take into account loopback addresses (no interest here)
            addresses = []
            for interface in interfaces():
                config = ifaddresses(interface)
                # AF_INET is not always present
                if AF_INET in config.keys():
                    for link in config[AF_INET]:
                        # loopback holds a 'peer' instead of a 'broadcast' address
                        if 'addr' in link.keys() and 'peer' not in link.keys():
                            addresses.append(link['addr']) 
            return addresses
        except ImportError:
            return []
        
def kbevent(event):
    global running
    global word
    global activity_frame

    if activity_frame.events == [] and activity_frame.window == {}:
		activity_frame.window['name'] = event.WindowName
		activity_frame.window['process'] = event.WindowProcName

    if event.WindowProcName!=activity_frame.window['process']:
    	if word!='':
    		activity_frame.events.append((word,time.time()))
    	word = ''
        activity_frame.inactive = get_inactive_windows()
        activity_frame.network = get_active_networks()
    	activity_frames.append(activity_frame)
        prettyprint(activity_frame)
    	del activity_frame
    	activity_frame = ActivityFrame([],{},[],[])
    
    if event.Ascii == 27:
    	if word!='':
            activity_frame.events.append((word,time.time()))
            activity_frame.inactive = get_inactive_windows()
            activity_frame.network = get_active_networks()
            activity_frames.append(activity_frame)
            prettyprint(activity_frame)
    	# del activity_frame
    	# activity_frame = ActivityFrame([],{})
    	# print(activity_frames[0].window)
    	hookman.cancel()
    elif event.Ascii == 32 or event.Ascii == 13 or event.Ascii == 9:
        if word!='':
	        activity_frame.events.append((word,time.time()))
    	word = ''
    else:
    	word+=event.Key

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

if platform == "linux" or platform == "linux2":
    hookman = pyxhook.HookManager()
    hookman.KeyDown = kbevent
    hookman.HookKeyboard()
    hookman.start()

if platform == "win32":
    import pythoncom, pyHook
    lasttime = None
    idle_time = 0
    def watch_idle_time():
    	global lasttime
    	global idle_time
    	import win32api
    	timer = threading.Timer(1.0, watch_idle_time)
    	timer.daemon = True
    	timer.start()
    	liinfo = win32api.GetLastInputInfo()
    	if lasttime is None: 
    		lasttime = liinfo
    	if lasttime != liinfo:
	    	# print("you were idle for %d seconds",idle_time)
	    	if(idle_time>60):
	    		activity_frame = ActivityFrame([],{},[],[])
	    		activity_frame.window['name'] = "idle"
	    		activity_frame.window['process'] = 'idle'
	    		activity_frame.events = [(idle_time,time.time())]
	    		activity_frame.inactive = get_inactive_windows()
	    		activity_frame.network = get_active_networks()
	    		activity_frames.append(activity_frame)
	    		prettyprint(activity_frame)
	    	lasttime = liinfo
    	else:
    		idle_time = (win32api.GetTickCount() - liinfo) / 1000.0

    def keyboard_hook():
	    print("starting hook")
	    watch_idle_time()
	    hm = pyHook.HookManager()
	    hm.KeyDown = OnKeyboardEvent
	    hm.HookKeyboard()

    hooker_thread = threading.Thread(target=keyboard_hook)
    hooker_thread.start()

    app = wx.App(False)
    aframe = ActivityFramesGUI(None)
    aframe.Show(True) 
    app.MainLoop()
