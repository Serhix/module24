from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread
import mimetypes
import pathlib
import socket
import sys
import urllib.parse
import json


UDP_IP = '127.0.0.1'
UDP_PORT = 8080
FILE_NAME_JSON = 'storage/data.json'


class HttpHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        pr_url = urllib.parse.urlparse(self.path)
        if pr_url.path == '/':
            self.send_html_file('index.html')
        elif pr_url.path == '/message':
            self.send_html_file('message.html')
        else:
            if pathlib.Path().joinpath(pr_url.path[1:]).exists():
                self.send_static()
            else:
                self.send_html_file('error.html', 404)

    def do_POST(self):
        data = self.rfile.read(int(self.headers['Content-Length']))
        run_client_udp(UDP_IP, UDP_PORT, data)
        self.send_response(302) #відправляємо відповідь
        self.send_header('Location', '/') #робимо редірект на головну сторін
        self.end_headers()
     
    def send_html_file(self, filename, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        with open(filename, 'rb') as fd:
            self.wfile.write(fd.read())

    def send_static(self):
        self.send_response(200)
        mt = mimetypes.guess_type(self.path)
        if mt:
            self.send_header("Content-type", mt[0])
        else:
            self.send_header("Content-type", 'text/plain')
        self.end_headers()
        with open(f'.{self.path}', 'rb') as file:
            self.wfile.write(file.read())


def run(server_class=HTTPServer, handler_class=HttpHandler):
    server_addres = ('', 3000)
    http = server_class(server_addres, handler_class)
    try:
        http.serve_forever()
    except KeyboardInterrupt:
        http.server_close()


def run_server_udp(ip, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server = ip, port
    sock.bind(server)

    try:
        while True:
            data, address = sock.recvfrom(1024)
            save_data_to_json(data)
    except KeyboardInterrupt:
        sock.close()


def run_client_udp(ip, port, message):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server = ip, port
    sock.sendto(message, server)
    sock.close()


def save_data_to_json(data):
    data_parse = urllib.parse.unquote_plus(data.decode())
    data_dict = {key: value for key, value in [el.split("=") for el in data_parse.split("&")]}
    try:
        with open(FILE_NAME_JSON, 'r', encoding='utf-8') as file:
            data_json = json.load(file)
    except BaseException as e:
            data_json = {}  
    data_json.update({f"{datetime.now()}": data_dict})
    with open(FILE_NAME_JSON, 'w') as file:
        json.dump(data_json, file)


if __name__ == '__main__':
    thread_web = Thread(target=run)
    thread_socket_serwer = Thread(target=run_server_udp, args=(UDP_IP, UDP_PORT))
    thread_web.start()
    thread_socket_serwer.start()