# Define the web server getting POST request from the Github Hook

import asyncio
from quart import Quart, request
from hypercorn.config import Config
from hypercorn.asyncio import serve

class HttpsServer:

    GITHUBHOOK_TARGET = "/github"
    FORMS_TARGET = "/forms"

    def __init__(self, secret_file=None):
        self.secret_file = secret_file
        self.server = Quart("Discord_Webhook_Server")

        @self.server.route(HttpsServer.GITHUBHOOK_TARGET, methods = ["POST"])
        async def post_handler():
            if request.method =="POST":
                print(await request.get_json())

    async def run(self, port=8080):
        config = Config()
        config.bind = [f"0.0.0.0:{port}"]
        server_task = asyncio.create_task(serve(self.server, config))
        print("The server is launched")
        await server_task

if __name__ == "__main__":
    serv = HttpsServer()
    asyncio.run(serv.run())
