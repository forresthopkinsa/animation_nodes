"""OLA Node things."""

from collections import defaultdict

import sys
import json


import bpy
from ... base_types.node import AnimationNode
from ... ui.info_popups import showTextPopup
from bpy.props import *


cache = defaultdict(dict)


##########################################
# global functions


def extend_deep(obj_1, obj_2):
    """
    Extend dicts deeply.

    extends obj_1 with content of obj_2 if not already there.
    """
    # work on obj_1
    if (isinstance(obj_1, dict) and isinstance(obj_2, dict)):
        for key in obj_2:
            if key not in obj_1:
                # key from obj_2 not found in obj_1
                # so add key:
                obj_1[key] = obj_2[key]
            else:
                # key is available.
                # test deeply if extension is needed:
                extend_deep(obj_1[key], obj_2[key])
    else:
        pass
        # don't overriede!
        # obj_1 = obj_2


##########################################
# classes


class OLADeamon(bpy.types.Node, AnimationNode):
    """Animation Node to get data from OLA Deamon."""

    bl_idname = "an_OLADeamonNode"
    bl_label = "OLA Deamon"
    options = {"No Subprogram"}

    config_defaults = {
        # "init_done": False,
        "universe": None,
        "serial": None,
        "serialio": None,
        "data_received": [],
        "data_send": [],
        "buttonLabel": "Test",
        "universelist": [],
    }

    ##########################################
    # user interface elements

    def universeListItemsGet(self, context):
        """Get list of available Universes."""
        if "universelist" not in cache[self.identifier]:
            self.universeListItemsUpdate()
        list = cache[self.identifier]["universelist"]
        return list

    def universeListItemsCreate(self):
        """create list of available Ports."""
        items = [
            ("0", "Output1", "a Universe with output"),
            ("1", "display name", "some description")
        ]
        # items = []
        # for port in universes:
        #     # print(port)
        #     items.append(
        #         (
        #             # identifier
        #             port.device,
        #             # display name
        #             port.device,
        #             # description
        #             port.description,
        #         )
        #     )
        return items

    def universeListItemsUpdate(self):
        """Update list of available Ports."""
        cache[self.identifier]["universelist"] = self.universeListItemsCreate()

    def universeChanged(self, context):
        """Set changed universe to ola obejct."""
        if (
            (self.identifier in cache) and
            ("init_done" in cache[self.identifier]) and
            (cache[self.identifier]["init_done"] is True)
        ):
            # serial port is available.
            # so we close the conneciton and change the device:
            # self.close()
            # cache[self.identifier]["serial"].port = self.port
            print(self.Universe)

    # universelist_items = [("a", "/dev/ttyACM0", )]
    universe = EnumProperty(
        name="Universe",
        description="connect to",
        items=universeListItemsGet,
        # items=[("identifier", "label", "description")]
        update=universeChanged
    )

    # example for checkbox
    # def connectedChanged(self, context):
    #     print("connected has changed...", self.connected)
    #
    # connected = BoolProperty(
    #     name="Connected",
    #     default=False,
    #     description="connect port to physical",
    #     update=connectedChanged
    # )

    def create(self):
        """Create node type."""
        # inputs
        # these are now handled in the draw function as ui elements.
        # self.newInput("String", "Port", "port", value="/dev/ttyACM0")
        # self.newInput("Integer", "Baudrate", "baudrate", value=115200)

        self.newOutput("an_IntegerListSocket", "Data", "data_received")
        # self.newOutput("String", "Received Text", "data_received")

    def draw(self, layout):
        # example for checkbox
        # layout.prop(self, "connected")

        row = layout.row(align=True)
        row.prop(self, "universe", text="")
        self.invokeFunction(
            row,
            "universeListItemsUpdate",
            text="",
            description="update universe list",
            icon="FILE_REFRESH"
        )


        # connectButton
        connectButtonLabel = cache[self.identifier].get(
            "connectButtonLabel",
            "n/a"
        )
        self.invokeFunction(
            layout,
            "connectButtonToggle",
            text=connectButtonLabel,
            description="toggle Serial Port connection",
            icon="PLUGIN"
        )

        # test button
        self.invokeFunction(
            layout,
            "test_readlines",
            text="read lines",
            description="read all incomming lines",
            icon="TEXT"
            # icon="LONGDISPLAY"
        )

    def connectButtonUpdate(self):
        """Update connectButton label."""
        # print("connectButtonUpdate:")
        if (
            (self.identifier in cache) and
            ("init_done" in cache[self.identifier]) and
            (cache[self.identifier]["init_done"] is True)
        ):
            state = cache[self.identifier]["serial"].is_open
            # print("update text: state:", state)
            if state:
                # currently connected. so button closes connection
                cache[self.identifier]["connectButtonLabel"] = "close"
            else:
                # currently disconnected. so button opens connection
                cache[self.identifier]["connectButtonLabel"] = "connect"
            # print(
            #     "connectButtonLabel: ",
            #     cache[self.identifier]["connectButtonLabel"]
            # )

    def connectButtonToggle(self):
        """Toggle serial port connection state."""
        if (
            (self.identifier in cache) and
            ("init_done" in cache[self.identifier]) and
            (cache[self.identifier]["init_done"] is True)
        ):
            state = cache[self.identifier]["serial"].is_open
            if state:
                self.close()
            else:
                self.open()

    def test_readlines(self):
        # lines = cache[self.identifier]["serialio"].readlines()
        lines = "test_readlines n/a"
        print(lines)

    ##########################################
    # main logic

    def execute(self):
        """Execute Node."""
        if (
            (self.identifier not in cache) or
            ("init_done" not in cache[self.identifier]) or
            (cache[self.identifier]["init_done"] is False)
        ):
            # self.initNode(self.universelist, self.baudrate)
            self.initNode()

        # print("execute:")
        # print(
        #     "cache:",
        #     json.dumps(
        #         cache[self.identifier],
        #         sort_keys=True,
        #         indent=4,
        #         separators=(',', ': ')
        #     )
        # )
        # print(
        #     "cache:",
        #     cache[self.identifier]
        # )
        # if cache[self.identifier]["serial"].is_open:
        #     ser = cache[self.identifier]["serial"]
        #     sio = cache[self.identifier]["serialio"]
        #     try:
        #         lines = sio.readlines()
        #     except serial.serialutil.SerialException as e:
        #         error_message = (
        #             "readlines failed at port {}: {}"
        #             .format(
        #                 ser.port,
        #                 e
        #             )
        #         )
        #         showTextPopup(text=error_message, title="Error", icon="INFO")
        #         # print(error_message)
        #         self.close()
        #     else:
        #         # print(lines)
        #         if len(lines) > 0:
        #             last_line = lines[len(lines)-1]
        #             # print(last_line)
        #             cache[self.identifier]["data_received"] = last_line
        cache[self.identifier]["data_received"] = [
            0, 200, 255,    # 1 türkis
            0, 255, 0,      # 4 green
            150, 100, 0,      # 7 yellow
            100, 0, 200,    # 10 lounge
        ]
        # return cached text
        result_data_received = cache[self.identifier]["data_received"]
        # print(
        #     "Node {}:  data_received: {}".format(
        #         self.identifier,
        #         cache[self.identifier]["data_received"]
        #     )
        # )
        # result_data_received = ""
        return result_data_received

    def initNode(self):
        """Init node instance."""
        # setup internal cache
        cache[self.identifier] = {}
        # print("initNode:")
        # print("cache:", cache)
        # print("extend_deep...")
        extend_deep(cache[self.identifier], self.config_defaults.copy())
        # print("cache:", cache)
        # print("cache:", cache[self.identifier])

        # print("universeListItemsUpdate")
        self.universeListItemsUpdate()

        # print("init serial port:")
        # print("self.baudrate", self.baudrate)
        # print("self.port", self.port)

        # setup serial port
        # cache[self.identifier]["serial"] = serial.Serial()
        # cache[self.identifier]["serial"].port = port
        # cache[self.identifier]["serial"].baudrate = baudrate

        # https://pythonhosted.org/pyserial/shortintro.html#eol
        # ser = serial.serial_for_url(
        #     self.port,
        #     baudrate=self.baudrate,
        #     timeout=0,
        #     do_not_open=True
        # )
        # sio = io.TextIOWrapper(io.BufferedRWPair(ser, ser))
        # cache[self.identifier]["serial"] = ser
        # cache[self.identifier]["serialio"] = sio
        self.connectButtonUpdate()
        #
        # sio.write(unicode("hello\n"))
        # # it is buffering. required to get the data out *now*
        # sio.flush()
        # hello = sio.readline()
        # print(hello == unicode("hello\n"))
        # print("done.")

        # lastly set init done flag:
        cache[self.identifier]["init_done"] = True

    def delete(self):
        """Clean up."""
        self.identifier

    ##########################################
    # internal functions

    def open(self):
        """Open Serial Port."""
        if not cache[self.identifier]["serial"].is_open:
            # print("open port:")
            # print(" serial:", cache[self.identifier]["serial"])
            # print(" port:", cache[self.identifier]["serial"].port)
            # print(" baudrate:", cache[self.identifier]["serial"].baudrate)
            # print(" timeout:", cache[self.identifier]["serial"].timeout)
            ser = cache[self.identifier]["serial"]
            try:
                ser.open()
            except serial.serialutil.SerialException as e:
                error_message = (
                    "Port {} is already in use by other program: {}"
                    .format(
                        ser.port,
                        e
                    )
                )
                showTextPopup(
                    text=error_message,
                    title="Error",
                    icon="INFO"
                )
                # print(error_message)
            # print(" is_open:", ser.is_open)

            # port already open check based on:
            # How to check if serial port is already open in Linux,
            # using Python 2.7 and pyserial?
            # http://stackoverflow.com/a/19823120/574981
            # https://docs.python.org/3/library/sys.html#sys.platform
            if sys.platform.startswith('linux'):
                # Linux-specific code here...
                # only try to lock if open was successfully
                if ser.is_open:
                    try:
                        # lock EX exclusive NB nonblocking
                        fcntl.flock(
                            ser.fileno(),
                            fcntl.LOCK_EX | fcntl.LOCK_NB
                        )
                        pass
                    except IOError as e:
                        error_message = (
                            "Port {} is already in use by other program: {}"
                            .format(
                                ser.port,
                                e
                            )
                        )
                        showTextPopup(
                            text=error_message,
                            title="Error",
                            icon="INFO"
                        )
                        # print(error_message)
                        # if lock failed close it.
                        ser.close()
        self.connectButtonUpdate()

    def close(self):
        """Open Serial Port."""
        ser = cache[self.identifier]["serial"]
        if ser.is_open:
            print("close port:")
            if sys.platform.startswith('linux'):
                # unlock
                try:
                    fcntl.flock(ser.fileno(), fcntl.LOCK_UN)
                except IOError as e:
                    print(
                        "execption at unlocking port {}: {}".
                        format(ser.port, e)
                    )
            ser.close()
        self.connectButtonUpdate()
