import tornado.ioloop
import tornado.web
import tornado.websocket
import subprocess  



class EchoWebSocket(tornado.websocket.WebSocketHandler):
    def run(self,command):  
        p = subprocess.Popen(command, stdin = subprocess.PIPE,
            stdout = subprocess.PIPE, stderr = subprocess.PIPE, shell = True,cwd=self.cwd)  
        return p.stdout.read()  +p.stderr.read()
    def save(self,file,content):
        with open(file,'w') as f:
            f.write(content)
        return 'saved'
    def shell(self,command):
        if str(command).startswith('cd '):command+=";pwd"
        result=self.run(command)
        if str(command).startswith('cd '):self.cwd=result.strip()
        return result

    def open(self):
        print "WebSocket opened"
        self.cwd="."

    def on_message(self, message):
        print message
        if message.startswith('save '):
            p=message.find(':')
            result=self.save(message[5:p],message[p+1:])
        else:
            result=self.shell(message)
        self.write_message(result)

    def on_close(self):
        print "WebSocket closed"

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('app.html')

application = tornado.web.Application([
    (r"/", MainHandler),
    (r"/ws", EchoWebSocket),

],debug=True,)

if __name__ == "__main__":
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()