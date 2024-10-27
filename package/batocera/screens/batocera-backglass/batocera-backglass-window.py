#!/usr/bin/env python3

import webview
from http.server  import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse
from urllib.parse import parse_qs
import urllib.request
import json
import hashlib
import argparse
import os
import re

class BackglassAPI(BaseHTTPRequestHandler):

    def sendHeaders(self, contentType):
        self.send_response(200)
        self.send_header("Content-type", contentType)
        self.end_headers()

    def gameShortName(self, path):
        # just filename without extension
        res = os.path.splitext(os.path.basename(path))[0]
        # remove anything in parenthesis
        res = re.sub(r"\([^)]*\)", "", res)
        # remove anything non alpha
        res = re.sub(r"[^A-Za-z0-9]", "", res)
        # lowercase
        return res.lower()

    def do_GET(self):

        try:
            query = urlparse(self.path)
            qs = parse_qs(query.query)

            if query.path == "/game":
                self.sendHeaders("text/plain")
                system = qs["system"][0]
                path   = qs["path"][0]
                hash   = hashlib.md5(path.encode('utf-8')).hexdigest()
                data   = {}
                with urllib.request.urlopen("http://localhost:1234/systems/{}/games/{}".format(system, hash)) as url:
                    data = json.load(url)
                    for prop in ["image", "video", "marquee", "thumbnail", "fanart", "manual", "titleshot", "bezel", "magazine", "manual", "boxart", "boxback", "wheel", "mix"]:
                        if prop in data:
                            shortname = self.gameShortName(path)
                            if os.path.exists("/userdata/system/backglass/systems/{}/games/{}/{}.png".format(system, prop, shortname)):
                                data[prop] = "http://localhost:2033/static/images/systems/{}/games/{}/{}.png".format(system, prop, shortname)
                            elif os.path.exists("/userdata/system/backglass/systems/{}/games/{}/{}.jpg".format(system, prop, shortname)):
                                data[prop] = "http://localhost:2033/static/images/systems/{}/games/{}/{}.jpg".format(system, prop, shortname)
                            else:
                                data[prop] = "http://localhost:1234" + data[prop]
                    window.evaluate_js("onGame(" + json.dumps(data) + ")")
                self.wfile.write(bytes("OK\n", "utf-8"))

            elif query.path == "/system":
                self.sendHeaders("text/plain")
                system = qs["system"][0]
                data   = {}
                with urllib.request.urlopen("http://localhost:1234/systems/{}".format(system)) as url:
                    data = json.load(url)
                    for prop in ["logo"]:
                        if prop in data:
                            if os.path.exists("/userdata/system/backglass/systems/{}/{}.png".format(system, prop)):
                                data[prop] = "http://localhost:2033/static/images/systems/{}/{}.png".format(system, prop)
                            elif os.path.exists("/userdata/system/backglass/systems/{}/{}.jpg".format(system, prop)):
                                data[prop] = "http://localhost:2033/static/images/systems/{}/{}.jpg".format(system, prop)
                            else:
                                data[prop] = "http://localhost:1234" + data[prop]

                    window.evaluate_js("onSystem(" + json.dumps(data) + ")")
                self.wfile.write(bytes("OK\n", "utf-8"))

            elif query.path == "/location":
                self.sendHeaders("text/plain")
                url = qs["url"][0]
                window.load_url(url)

            elif query.path.startswith("/static/images/"):
                if ".." not in  query.path: # don't allow to escape
                    with open("/userdata/system/backglass/{}".format(query.path[15:]), "rb") as fd:
                        if query.path.endswith(".png"):
                            self.sendHeaders("image/png")
                        elif query.path.endswith(".jpg"):
                            self.sendHeaders("image/jpg")
                        else:
                            raise Exception("Invalid extension")
                        self.wfile.write(fd.read())

        except Exception as e:
            print(e)
            self.wfile.write(bytes("ERROR\n", "utf-8"))

def handle_api(window):
    webServer = HTTPServer(("localhost", 2033), BackglassAPI)
    print("Server started http://%s:%s" % ("localhost", 2033))
    try:
        webServer.serve_forever()
    except:
        webServer.server_close()

parser = argparse.ArgumentParser(prog="batocera-backglass")
parser.add_argument("--www", default="/usr/share/batocera-backglass/www/backglass-default/index.htm", help="path to the web page")
parser.add_argument("--x",      type=int, default=0,   help="window x position")
parser.add_argument("--y",      type=int, default=0,   help="window y position")
parser.add_argument("--width",  type=int, default=800, help="window width")
parser.add_argument("--height", type=int, default=600, help="window height")
args = parser.parse_args()

window = webview.create_window('backglass', args.www, x=args.x, y=args.y, width=args.width, height=args.height, focus=False)
webview.start(handle_api, window)
