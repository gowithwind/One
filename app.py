import tornado.ioloop
import tornado.web
import tornado.websocket
import subprocess  
import json

passkey="test"
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
        if str(command).startswith('cd '):self.cwd=result.strip('\n')
        return result

    def open(self):
        if self.get_secure_cookie('user')!=passkey:
            return None
        print "WebSocket opened"
        self.cwd="."

    def on_message(self, message):
        print message
        data=json.loads(message)
        if data['command']=='save':
            result=self.save(data['file'],data['content'])
        else:
            result=self.shell(data['command'])
        self.write_message(result)

    def on_close(self):
        print "WebSocket closed"

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        if  self.get_argument('u','')==passkey:
            self.set_secure_cookie("user", passkey)
            self.redirect('/')
            return
        self.render('app.html')
        

application = tornado.web.Application([
    (r"/", MainHandler),
    (r"/ws", EchoWebSocket),

],debug=True,cookie_secret="A test cookie_secret")

if __name__ == "__main__":
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()