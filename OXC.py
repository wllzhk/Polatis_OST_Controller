import telnetlib
import time


class OXC:
    def __init__(self, ip, port=5025):
        self.ip = ip
        self.port = port
        self.tn = telnetlib.Telnet()
        self.tn.open(self.ip, port=self.port)

    def send_message(self, msg):
        """
        发送消息，等待1s回复
        :param msg:
        :return:
        """
        self.send_message_without_reply(msg)
        return self.tn.read_until(b'\n', timeout=1).decode('ascii')

    def send_message_without_reply(self, msg):
        """
        发送命令，不要求回复
        :param msg: 命令字符串
        :return:
        """
        if '\n' in msg:
            self.tn.write(msg.encode('ascii'))
        else:
            self.tn.write(msg.encode('ascii') + b'\n')

    def check_com(self):
        """
        测试是否连通
        :return:
        """
        b = self.send_message('*idn?')
        if 'Polatis,N-OST-24x24-LA1-DMHNS' in b:
            return True
        else:
            return False

    def add_connection(self, s, d):
        """
        添加链路，且不影响已经存在的链路
        :param s: 左端点
        :param d: 右端点
        :return:
        """
        source = min(s, d)
        destination = max(s, d)
        if source > 24 or destination < 25 or destination > 48:
            raise ValueError('illegal source and destination')
        print('Add connection: ', 'oxc:swit:conn:add (@%d),(@%d)' % (source, destination))
        self.send_message_without_reply('oxc:swit:conn:add (@%d),(@%d)' % (source, destination))

    def destroy(self):
        """
        销毁链接
        :return:
        """
        self.tn.close()

    def init_connection(self, f, t):
        """
        初始化连接，会重置已经存在的链路
        :param f: 左端点list
        :param t: 右端点list
        :return:
        """
        if len(f) != len(t):
            raise ValueError('non-corresponding')
        data = ':oxc:swit:conn:only (@'
        for p in f:
            data = data + str(p) + ','
        data = data[:-1] + '),(@'
        for p in t:
            data = data + str(p) + ','
        data = data[:-1] + ')'
        print('Init connection: ', data)
        self.send_message_without_reply(data)

    def query_port_state(self, p):
        """
        查询端口连接对象，无连接返回空字符串
        :param p:
        :return:
        """
        return self.send_message('oxc:swit:conn:port? %d' % p)

        # self.tn.write(b"*idn?\n")
        # # time.sleep(1)
        # pre = time.time()
        # print(self.tn.read_until(b'\n', timeout=10).decode('ascii'))
        # print(time.time()-pre)
        # print(self.tn.read_very_eager().decode('ascii'))


if __name__ == '__main__':
    host_ip = '10.0.3.6'
    port = 5025
    oxc = OXC(host_ip, port)
    print(oxc.check_com())
    oxc.init_connection(list(range(1, 24)), list(range(25, 48)))
    oxc.add_connection(15, 38)
    print(oxc.query_port_state(15))
    oxc.destroy()
