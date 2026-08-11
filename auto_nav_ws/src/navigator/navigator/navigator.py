import rclpy
from rclpy.node import Node
from std_msgs.msg import String

import asyncio
import threading
import websockets

class Navigator(Node):
    def __init__(self):
        super().__init__("navigator")

        self.publisher = self.create_publisher(String, "chatter", 10)
        self.url = "ws://localhost:8765"

        self.is_running = True

        self.loop = asyncio.new_event_loop()
        self.thread = threading.Thread(target=self.run_event_loop,
                                       daemon=True)
        self.thread.start()

        asyncio.run_coroutine_threadsafe(self.connect_socket(), self.loop)

    def run_event_loop(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    async def connect_socket(self):
        while self.is_running and rclpy.ok():
            try:
                async with websockets.connect(self.url) as socket:
                    while self.is_running and rclpy.ok():
                        waypoints = await socket.recv()

                        msg = String()
                        msg.data = str(waypoints)
                        self.publisher.publish(msg)

            except(websockets.exceptions.ConncetionClosedError,
                   ConnectionRefusedError) as e:
                self.get_logger().warn(f"Connection lost: {e}")
                await asyncio.sleep(2.0)

            except Exception as e:
                self.get_logger().warn(f"Error: {e}")
                await asyncio.sleep(2.0)

    def destroy_node(self):
        self.is_running = False
        if self.loop.is_running:
            self.loop.call_soon_threadsafe(self.loop.stop)
        super.destroy_node()


def main():
    rclpy.init()
    node = Navigator()

    rclpy.spin(node)

    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()