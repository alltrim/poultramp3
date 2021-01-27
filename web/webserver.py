# coding=cp1251

from http.server import SimpleHTTPRequestHandler, HTTPServer
import os

class ThisHTTPRequestHandler(SimpleHTTPRequestHandler):
    __DATA_DIRECTORY = "data"

    def do_GET(self):
        datafile = self.__DATA_DIRECTORY + self.path
        
        if os.path.exists(datafile) and os.path.isfile(datafile):
            file = open(datafile, "r")
            self.send_response(200)
            self.send_header("Content-type", "text/csv")
        else:
            file = open("web/404.html", "r")
            self.send_response(404)
            self.send_header("Content-type", "text/html")

        self.end_headers()

        data = file.read()
        file.close()

        self.wfile.write(bytes(data, encoding="cp1251"))
        return

def main():
    server = HTTPServer(("127.0.0.1", 5000), ThisHTTPRequestHandler)
    server.serve_forever()

if __name__ == "__main__":
    main()
