import socket, threading, time, json

def server(addr, port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setblocking(0)
        sock.bind((socket.gethostbyname(addr), port))
        return SocketServerWrapper(SocketThread(sock))

def client(addr, port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setblocking(0)
        return SocketClientWrapper(SocketThread(sock), (socket.gethostbyname(addr), port))

class SocketClientWrapper:
    def __init__(self, sock_thr, dest):
        self.sock_thr = sock_thr
        self.sock_thr.start()
        self.dest = dest

    def send(self, msg):
        with self.sock_thr.send_lock:
            self.sock_thr.send.insert(0, (json.dumps(msg), self.dest))

    def recv(self):
        with self.sock_thr.recv_lock:
            recv, self.sock_thr.recv = self.sock_thr.recv, []
            for i in recv[:]:
                if i[1] == self.dest: recv[recv.index(i)] = json.loads(i[0])
                else: recv.remove(i)

            return recv

    def close(self):
        self.sock_thr.active = False

class SocketServerWrapper:
    def __init__(self, sock_thr):
        self.sock_thr = sock_thr
        self.sock_thr.start()

    def send(self, msg, dest):
        with self.sock_thr.send_lock: 
            self.sock_thr.send.insert(0, (json.dumps(msg), dest))

    def recv(self):
        with self.sock_thr.recv_lock:
            recv, self.sock_thr.recv = self.sock_thr.recv, []
            out = []
            for m in recv:
                out.append([json.loads(m[0])] + m[1:])
            return out

    def close(self):
        self.sock_thr.active = False


class SocketThread(threading.Thread):
    def __init__(self, socket):
        threading.Thread.__init__(self)
        self.socket = socket
        self.recv = []
        self.recv_lock = threading.Lock()
        self.send = []
        self.send_lock = threading.Lock()
        self.active = True

    def run(self):
        while self.active:
            t = time.time()
            try:
                msg, addr = self.socket.recvfrom(512)
                with self.recv_lock:
                    self.recv.append([msg.decode('utf-8'), addr])

            except (socket.error, OSError): pass

            if len(self.send) > 0:
                with self.send_lock:
                    msg, dest = self.send.pop()
                    self.socket.sendto(msg.encode('utf-8'), dest)
            s = (0.01 - (time.time() - t))
            if s > 0: time.sleep(s)
