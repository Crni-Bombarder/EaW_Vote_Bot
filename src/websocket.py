# Define the web server getting POST request from the Github Hook

import asyncio
from quart import Quart, request
from hypercorn.config import Config
from hypercorn.asyncio import serve

from src.watched_refs import Refs

class HttpsServer:

    GITHUBHOOK_TARGET = "/github"

    def __init__(self, watched_refs_file, secret_file=None):
        self.secret_file = secret_file
        self.refs = Refs(watched_refs_file)
        self.server = Quart("Github_Webhook_Server")

        def add_refs(self, new_refs):
            

        @self.server.route(HttpsServer.GITHUBHOOK_TARGET, methods = ["POST"])
        async def post_handler():
            if request.method =="POST":
                print("ok")
                return "Ok"
    
    async def run(self, port=8080):
        config = Config()
        config.bind = [f"localhost:{port}"]
        server_task = asyncio.create_task(serve(self.server, config))
        print("The server is launched")
        await server_task

if __name__ == "__main__":
    serv = HttpsServer()
    asyncio.run(serv.run())
