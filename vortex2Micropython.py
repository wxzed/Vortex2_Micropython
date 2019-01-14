import os
import sys
import argparse
import pywinusb.hid as hid
import pythoncom
import PyHook3 as pyHook
import serial
import time
import logging
import threading


writeboot0=0
writeboot1=1
writeapp  =2
datacs    =0
updata_done = 1
report_id  = [0x00]
device_num = [0x00]
hh_data    = [0xff]*22
flash_data = [0x00]*54#去除数据头和report id 的有效数据
contorl_commands = 0
down_over = 0
now_status = 0
times = 0
'''CTR0-->read/write  CTR1-->boot0/boot1/app/softdevice/'''
'''                                      LEN  CS  CTR0 CTR1 ADD0 ADD1 ADD2 ADD3          '''
write_boot0           =      [0x55,0xAA,0x00,0x00,0x01,0x00,0x00,0x02,0xB0,0x00]
write_boot1           =      [0x55,0xAA,0x00,0xA5,0x01,0x01,0x00,0x03,0xA0,0x00]
write_app             =      [0x55,0xAA,0x00,0x97,0x01,0x02,0x00,0x04,0x90,0x00]
data_head             =      [0x55,0xAA,0x00,0x02,0x01,0x01,0x00,0x00,0x00,0x00]
data_head_update_done =      [0x55,0xAA,0x00,0xC3,0x10,0x10,0x00,0x03,0xA0,0x00]
app_addr    =0x00049000
offset_addr    =0x00000000

def updata_datahead(data):
    global updata_done
    global data_head
    global data_head_update_done
    if data is updata_done:
        data_head = data_head_update_done
class hidHelper(object):
    def __init__(self, vid=0x1915,pid=0x521a):
        self.alive = False
        self.device = None
        self.report = None
        self.vid = vid
        self.pid = pid
        
    def start(self):
        _filter = hid.HidDeviceFilter(vendor_id = self.vid, product_id = self.pid)
        hid_device = _filter.get_devices()
        if len(hid_device) > 0:
            self.device = hid_device[0]
            self.device.open()
            self.report = self.device.find_output_reports()
            self.alive = True
            
    def stop(self):
        self.alive = False
        if self.device:
            self.device.close()
            
    def setcallback(self):
        if self.device:
            self.device.set_raw_data_handler(self.read)
            
    def read(self,data):
        for i in range(1,17):
            if data[i] is 0x00:
                return
            sys.stdout.write(chr(data[i]))
            sys.stdout.flush()
        
    def write(self,send_list):
        if self.device:
            if self.report:
                self.report[0].set_raw_data(send_list)
                bytes_num = self.report[0].send()
                return bytes_num

def hidRestart():
    myhid.stop()
    myhid.start()
    while myhid.alive is False:
        myhid.start()
    if myhid.alive:
        myhid.setcallback()

def onKeyboardEvent(event):
    #print("Ascii:",event.Ascii,chr(event.Ascii))
    data = [0x00]*17
    data[1] = event.Ascii
    try:
        myhid.write(data)
    except:
        hidRestart()
    return True

def hid_thread():
    myhid.start()
    while myhid.alive is False:
        myhid.start()
    if myhid.alive:
        myhid.setcallback()
    while True:
        time.sleep(0.1)

def main():
    hm = pyHook.HookManager()
    hm.KeyDown = onKeyboardEvent
    hm.HookKeyboard()
    pythoncom.PumpMessages()
if __name__ == '__main__':
    myhid = hidHelper()
    t = threading.Thread(target=hid_thread, name='hidThread')
    t.start()
    main()
    '''
    while True:
        data = [0x00]*17
        indata = input();
        for i in range(0,len(indata)):
            data[i+1] = str.encode(indata)[i]
            data[i+2] = 0x0D
            data[i+3] = 0x0A
        myhid.write(data)
    myhid.stop()'''
