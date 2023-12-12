from flask import Flask, render_template
from flask_socketio import SocketIO
from pyensign.events import Event
from pyensign.ensign import Ensign
import json
import asyncio



app = Flask(__name__)
socketio = SocketIO(app)


class DashboardSubscriber:

    def __init__(self, sub_topic="test2_weighted_score"):
        self.sub_topic = sub_topic
        self.ensign = Ensign(
            client_id="",
            client_secret=""
        )

    async def pull_weighted_score(self, event):
        origin_data = json.loads(event.data)
        if origin_data['weighted_score'] > 0.5:
            origin_data["anomaly"] = 'yes'
        else:
            origin_data["anomaly"] = 'no'
        # Emit the data to the frontend via WebSockets
        socketio.emit('update_data', origin_data)

        await event.ack()

    async def subscribe(self):
        await self.ensign.ensure_topic_exists(self.sub_topic)
        async for event in self.ensign.subscribe(self.sub_topic):
            await self.pull_weighted_score(event)

    def run(self):
        """
        Run the subscriber forever.
        """
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.subscribe())


@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    subscriber = DashboardSubscriber()
    # Start the subscriber and Flask server in parallel
    socketio.start_background_task(target=subscriber.run)
    socketio.run(app,port=5029,allow_unsafe_werkzeug=True)
