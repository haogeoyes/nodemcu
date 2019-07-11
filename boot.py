'''
    连接mqtt后自动导入mainInit函数 
    发送消息类型
    快闪5 接收到消息
    快闪3 报错
    慢闪5 连接上wifi
'''
import gc
import os
from simple import MQTTClient
from machine import Pin
from app import run
import network
import time
import machine
import json
# import ujson

class initMain():
    def __init__(self):
        self._topic = '001'
        self._host = '192.168.43.73'

    def mqttMain(self):
        try:
            c =MQTTClient("umqtt_client", server=self._host,port=1883)
            self.c = c
            # c =MQTTClient("umqtt_client", server="192.168.50.53",port=1883)
            c.set_callback(self.sub_cb)
            c.connect()
            # c.subscribe("001")
            print('mqtt connect ok')
            return c
        except OSError as e:
            ledTrue(2,0.1)
            _str = 'error:%s' % e
            print(_str)
            machine.reset()
        

    def sub_cb(self,topic, msg):
        '''
            mqtt接收到消息回调函数
        '''
        try:
            print(topic,msg)
            self.ledTrue(5,0.1)
            self.checkMqtt(msg)
            # 热更新固件
            run()
        except:
            self.ledTrue(3,0.1)
        run()

    # def writeFun():
    def subCreate(self):
        '''
            监听主题消息，保证监听程序一定可用
        '''
        try:
            while True:
                self.c.check_msg()
                time.sleep(0.1)
        except:
            self.subCreate()


    def connectWifi(self):
        self.ledTrue(1,1)
        sta_if = network.WLAN(network.STA_IF)
        sta_if.active(True)
        #sta_if.scan()                             #  扫描当前可连接的WiFi名称
        sta_if.connect("tianwanggaidihu", "dabingjiayiqie")               # 设置要连接WiFi的名称和连接密码
        #ledTrue(5,1)
        self.ledTrue(2,1)
        return sta_if

    def ledTrue(self,num,t):
        #t间隔时间
        for i in range(num):
            led=Pin(2,Pin.OUT)
            led.value(1)              #turn off
            time.sleep(t)
            led.value(0)              #turn on
            time.sleep(t)


    def checkMqtt(self,msg):
        '''
            消息主题可更新部分
        '''
        try:
            msg = msg.decode()
            _str = json.loads(msg)
            try:
                #热更新代码
                #"{'type':'write','file':'app.py','body':'代码','action':'reboot/reload'}"
                if _str['type'] == 'write':
                    self.c.publish(self._topic,'11111')
                    f = open(_str['file'],'w')
                    f.write(_str['body'])
                    f.close()
                    if _str['action'] == 'reboot':
                        machine.reset()
                    self.c.publish(self._topic,'11111')
                if _str['type'] == 'exec':
                    out = exec("%s" % _str['body'])
                    # self.c.publish(self._topic,out)
            except OSError as e:
                _str = '写入文件或执行动作失败 %s' % (e)
                self.c.publish(self._topic,_str)
                self.ledTrue(3,0.1)
                print(_str)
        except OSError as e:
            # _str = '接收消息加载json失败 %s' % e
            # _str = '接收消息加载json失败' 
            # c.publish(_topic,e)
            self.ledTrue(3,0.1)
            # print(e)
            # print(_str)

    def initFun(self):
        try:
            print('connect wifi')
            wifi = self.connectWifi()
            status = wifi.isconnected()
            msg = ''
            if status:  #连接wifi成功
                #   global c 
                print('connect mqtt')
                c = self.mqttMain()
                self.c = c
                c.subscribe(self._topic)
                c.publish(self._topic,'connnect 001 successufly')

                # 消息主题监听函数
                self.subCreate()
                # while True:
                #     try:
                #         c.check_msg()
                #         time.sleep(0.1)
                #     except OSError as e:
                #         self.ledTrue(3,0.1)
                        # _str = 'error:%s' % e
                        # c.publish(_topic,_str)
                        # print(_str)
                        #machine.reset() #重启
            else: #wifi 连接失败
                print('connect fail reset')
                self.initFun()
        except OSError as e:
            self.initFun()




if __name__ == "__main__":
    Esp = initMain()
    Esp.initFun()
