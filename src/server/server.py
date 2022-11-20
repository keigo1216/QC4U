import argparse
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from slot import init_slot, play_slot

class MyHandler(BaseHTTPRequestHandler):
    def __init__(self, request, client_address, server):
        super().__init__(request=request, client_address=client_address, server=server)
        
    def do_GET(self):
        content_len = int(self.headers.get('content-length'))
        requestBody = self.rfile.read(content_len).decode('utf-8')
        print("Hello")
        chip = requestBody['chip']
        add_circuit = requestBody['add_circuit']
        if add_circuit is 4:
            angles = []
            for i in range(6):
                angles.append(requestBody['angles' + str(i + 1)])
            print(angles)
            qc1, qc2, qc3, d_chip = init_slot(add_circuit=add_circuit, angles=angles)
        else:
            qc1, qc2, qc3, d_chip = init_slot(add_circuit=add_circuit)

        slot1, slot2, slot3, inc, chip = play_slot(qc1, qc2, qc3, chip, d_chip)

        response = {'status' : 200, 
                    'result' : {
                        'slot1' : int(slot1),
                        'slot2' : int(slot2),
                        'slot3' : int(slot3),
                        'inc' : int(inc),
                        'chip' : int(chip)
                    }}
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        #ヘッダにcontent-lengthを追加する必要があるかもしれない
        self.end_headers()
        responseBody = json.dumps(response)

        self.wfile.write(responseBody.encode('utf-8'))

    def do_POST(self):
        try:
            content_len = int(self.headers.get('content-length'))
            requestBody = self.rfile.read(content_len).decode('utf-8')
            requestBody = parse_request(requestBody)

            chip = requestBody['chip']
            add_circuit = requestBody['add_circuit']
            if add_circuit is 4:
                angles = []
                for i in range(6):
                    angles.append(requestBody['angles' + str(i + 1)])
                print(angles)
                qc1, qc2, qc3, d_chip = init_slot(add_circuit=add_circuit, angles=angles)
            else:
                qc1, qc2, qc3, d_chip = init_slot(add_circuit=add_circuit)

            slot1, slot2, slot3, inc, chip = play_slot(qc1, qc2, qc3, chip, d_chip)

            response = {'status' : 200, 
                        'result' : {
                            'slot1' : int(slot1),
                            'slot2' : int(slot2),
                            'slot3' : int(slot3),
                            'inc' : int(inc),
                            'chip' : int(chip)
                        }}
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            #ヘッダにcontent-lengthを追加する必要があるかもしれない
            self.end_headers()
            responseBody = json.dumps(response)

            self.wfile.write(responseBody.encode('utf-8'))

        except Exception as e:
            print("An error occured")
            print("The information of error is as following")
            print(type(e))
            print(e.args)
            print(e)
            response = {'status' : 500,
                        'msg' : 'An error occured'}
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            responseBody = json.dumps(response)

            self.wfile.write(responseBody.encode('utf-8'))

def parse_request(request):
    """
    &区切りで送られてくるリクエストをdic形式に変換する

    Parameter
    ------------
    request: str
        生の文字列
    
    Return
    ------------
    parsed: dic
    """
    parsed = {}
    request = request.split("&")
    for req in request:
        req = req.split("=")
        key, value = req[0], req[1]
        parsed[key] = int(value)
    return parsed

def importargs():
    parser = argparse.ArgumentParser("This is the simple server") #コマンドライン引数のオプションで指定できるようになるクラス

    parser.add_argument('--host', '-H', required=False, default='localhost')
    parser.add_argument('--port', '-P', required=False, type=int, default=8080)

    args = parser.parse_args()

    return args.host, args.port

def run(server_class=HTTPServer, handler_class=MyHandler, server_name='localhost', port=8000):
    server = server_class((server_name, port), handler_class)
    server.serve_forever()

def main():
    host, port = importargs()
    run(server_name=host, port=port)

if __name__ == "__main__":
    main()