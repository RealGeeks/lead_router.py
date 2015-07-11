'''
Show status of 'leadrouter' tube in beanstalkd on all app servers
'''

import subprocess
import time

def main():
    for i in range(1, 4):  # we have 3 app servers, from 1 to 3
        hostname = 'app%d.web.rg-infrastructure.com' % i
        port = 11300+i
        ssh_forward = ssh_port_forward(hostname, port)
        print(hostname)
        show_stats(port)
        ssh_forward.terminate()


def ssh_port_forward(hostname, port):
    cmd = ('ssh -N -L %s:%s:11300 %s' % (port, hostname, hostname)).split()
    return subprocess.Popen(cmd)


def show_stats(port):
    cmd = ('beanstool stats --tubes=leadrouter --host=localhost:%s' % port).split()
    n = 5
    while n != 0:
        p = subprocess.Popen(cmd, stderr=subprocess.PIPE)
        p.wait()
        if p.returncode == 0:
            return
        n -= 1
        time.sleep(1)


if __name__ == '__main__':
    main()
