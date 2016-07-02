"""Serial Node things."""

from collections import defaultdict

import bpy
from ... base_types.node import AnimationNode

cache = defaultdict(dict)


class SerialPort(bpy.types.Node, AnimationNode):
    """"Animation Node to get data from a SerialPort.""""

    bl_idname = "an_SerialPortNode"
    bl_label = "Serial Port"

    internals_default = {
        "serial": None,
        "text_received": "",
        "text_send": "",
    }

    def create(self):
        """Create node type."""
        # inputs
        self.newInput("String", "Port", "port")
        self.newInput("String", "Baudrate", "baudrate")

        # self.newOutput("an_IntegerListSocket")
        self.newOutput("String", "Received Text", "text_received")

    def execute(self):
        """Execute Node."""
        if self.identifier not in cache:
            cache[self.identifier] = self.initNode()

        result_text_received = cache[self.identifier]["text_received"]
        return result_text_received

    def initNode(self):
        """Init node instance."""
        return internals_default.copy()
