#  coding: utf-8 
import socketserver, os

# Copyright 2013 Abram Hindle, Eddie Antonio Santos
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/

WWW_DIR = "www"
END_OF_LINE_RESPONSE = "\r\n"
RESPONSE_CODE = {
    "OK": "200",
    "REDIRECT": "301",
    "NOT_FOUND": "404",
    "METHOD_NOT_ALLOWED": "405"
}


class MyWebServer(socketserver.BaseRequestHandler):
    
    def handle(self):
        self.data = self.request.recv(1024).strip().decode('utf-8')

        #print ("Got a request of: %s\n" % self.data)

        response = ""

        (requestMethod, requestPath) = self.parse_request(self.data)

        if requestMethod != "GET":
            response = self.get_response(
                    RESPONSE_CODE["METHOD_NOT_ALLOWED"] + " Method Not Allowed",
                    self.get_response_header(RESPONSE_CODE["METHOD_NOT_ALLOWED"]),
                    self.get_content_type(requestPath, RESPONSE_CODE["METHOD_NOT_ALLOWED"]))
        else:
            if requestPath.endswith("/"):
                requestPath = requestPath + "index.html"

            # redirect
            if self.is_valid_path(requestPath) and self.is_redirect(requestPath):
                response = self.get_response(
                        "",
                        self.get_response_header(RESPONSE_CODE["REDIRECT"]),
                        "Location: " + requestPath + "/" + END_OF_LINE_RESPONSE)
            # valid path
            elif self.is_valid_path(requestPath):
                try:
                    file = open(WWW_DIR + requestPath, "r")
                    fileContent = file.read()
                    response = self.get_response(
                        fileContent,
                        self.get_response_header(RESPONSE_CODE["OK"]),
                        self.get_content_type(requestPath, RESPONSE_CODE["OK"]))
                    file.close()
                except Exception:
                    response = self.get_response(
                    RESPONSE_CODE["NOT_FOUND"] + " File Not Found",
                    self.get_response_header(RESPONSE_CODE["NOT_FOUND"]),
                    self.get_content_type(requestPath, RESPONSE_CODE["NOT_FOUND"]))
            # otherwise, not found
            else:
                response = self.get_response(
                    RESPONSE_CODE["NOT_FOUND"] + " Not Found",
                    self.get_response_header(RESPONSE_CODE["NOT_FOUND"]),
                    self.get_content_type(requestPath, RESPONSE_CODE["NOT_FOUND"]))
        
        #print(response)

        self.request.sendall(bytearray(response, 'utf-8'))

    def parse_request(self, request):
        requestMethod = request.split(" ")[0]
        requestPath = request.split(" ")[1]
        return (requestMethod, requestPath)
    
    def is_redirect(self, path):
        return os.path.isdir(WWW_DIR + path)

    def is_valid_path(self, path):
        return WWW_DIR in os.path.abspath(WWW_DIR + path)

    def get_response_header(self, responseCode):
        if responseCode == RESPONSE_CODE["OK"]:
            return "HTTP/1.1 200 OK" + END_OF_LINE_RESPONSE
        elif responseCode == RESPONSE_CODE["REDIRECT"]:
            return "HTTP/1.1 301 Moved Permanently" + END_OF_LINE_RESPONSE
        elif responseCode == RESPONSE_CODE["NOT_FOUND"]:
            return "HTTP/1.1 404 Not Found" + END_OF_LINE_RESPONSE
        elif responseCode == RESPONSE_CODE["METHOD_NOT_ALLOWED"]:
            return "HTTP/1.1 405 Method Not Allowed" + END_OF_LINE_RESPONSE

    def get_content_type(self, path, responseCode=RESPONSE_CODE["OK"]):
        contentType = "Content-Type: "
        if responseCode != RESPONSE_CODE["OK"]:
            return contentType + "text/plain" + END_OF_LINE_RESPONSE

        if path.endswith(".css"):
            return contentType + "text/css" + END_OF_LINE_RESPONSE
        elif path.endswith(".html"):
            return contentType + "text/html;charset=utf-8" + END_OF_LINE_RESPONSE
        else:
            return contentType + "text/plain" + END_OF_LINE_RESPONSE

    def get_content_length(self, content):
        return "Content-Length: " + str(len(content)) + END_OF_LINE_RESPONSE

    def get_response(self, content, *headerElements):
        response = ""
        for element in headerElements:
            response += element
        response += END_OF_LINE_RESPONSE
        return response + content

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
