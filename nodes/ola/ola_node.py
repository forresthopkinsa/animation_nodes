"""OLA Node things."""

from collections import defaultdict

import sys
import json
import array

import bpy
from ... base_types.node import AnimationNode
from ... base_types.socket import AnimationNodeSocket
from ... ui.info_popups import showTextPopup
from bpy.props import (
    StringProperty,
    # BoolProperty,
    # IntProperty,
    # FloatProperty,
    # FloatVectorProperty,
    EnumProperty,
    # PointerProperty,
)

# import needed ola helper modules
from . olathreaded import OLAThread, OLAThreadReceive, OLAThread_States

olapath = "/home/stefan/ola/python"

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


class OLAClient(bpy.types.Node, AnimationNode):
    """Animation Node to connect to OLA Deamon."""

    bl_idname = "an_OLAClientNode"
    bl_label = "OLA Client"
    options = {"No Subprogram"}

    config_defaults = {
        # "init_done": False,
        "universe": None,
        "ola_manager": None,
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

    olapath = StringProperty(
        name="API Path",
        description="set path to OLA python api on your disc. "
        "if you change this you have to "
        "save & restart blender to take effect"
        "or reload all scripts with F8",
        default="/home/stefan/ola/python/"
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
        # others are handled in the draw function as ui elements.
        # self.newInput(
        #     "String",
        #     "OLA Path",
        #     "olapath",
        #     value="/home/stefan/ola/python"
        # )
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

        row = layout.row(align=True)
        # connectButton
        connectButtonLabel = cache[self.identifier].get(
            "connectButtonLabel",
            "n/a"
        )
        self.invokeFunction(
            row,
            "connectButtonToggle",
            text=connectButtonLabel,
            description="toggle OLA Client connection",
            icon="PLUGIN"
        )
        self.invokeFunction(
            row,
            "connectButtonUpdate",
            text="",
            description="update label",
            icon="FILE_REFRESH"
        )

        # test button
        self.invokeFunction(
            layout,
            "test_things",
            text="test things",
            description="random test things",
            icon="NONE"
            # icon="TEXT"
            # icon="LONGDISPLAY"
        )

        layout.prop(self, "olapath")

    def connectButtonUpdate(self):
        """Update connectButton label."""
        print("connectButtonUpdate:")
        if (
            (self.identifier in cache) and
            ("init_done" in cache[self.identifier]) and
            (cache[self.identifier]["init_done"] is True)
        ):
            ola_manager = cache[self.identifier]["ola_manager"]
            state = ola_manager.state
            print("state: {!r}".format(state))
            cache[self.identifier]["connectButtonLabel"] = state.name
            # if state == OLAThread_States.standby:
            #     # currently disconnected. so button opens connection
            #     cache[self.identifier]["connectButtonLabel"] = "connect"
            # elif state == OLAThread_States.running:
            #     # currently connected. so button closes connection
            #     cache[self.identifier]["connectButtonLabel"] = "close"
            print(
                "connectButtonLabel: ",
                cache[self.identifier]["connectButtonLabel"]
            )
        else:
            print("not available yet.")
            cache[self.identifier]["connectButtonLabel"] = "n/a"

    def connectButtonToggle(self):
        """Toggle connection state."""
        if (
            (self.identifier in cache) and
            ("init_done" in cache[self.identifier]) and
            (cache[self.identifier]["init_done"] is True)
        ):
            ola_manager = cache[self.identifier]["ola_manager"]
            state = ola_manager.state
            print("state: ", state)
            # print("OLAThread_States.standby:", OLAThread_States.standby)
            # print("repr state:")
            # repr(state)
            # print("repr 2:")
            # repr(OLAThread_States.standby)
            # print("- end of tests")
            # if state == OLAThread_States.standby:
            #     print("connect!!")
            #     self.connect()
            # elif state == OLAThread_States.running:
            #     print("close!!")
            #     self.close()
            # else:
            #     print("state is not nown?!")
            ola_manager.toggle_connection()
            self.connectButtonUpdate()

    def test_things(self):
        if (
            (self.identifier in cache) and
            ("init_done" in cache[self.identifier]) and
            (cache[self.identifier]["init_done"] is True)
        ):
            # lines = cache[self.identifier]["serialio"].readlines()
            print("send test frame:")
            cache[self.identifier]["ola_manager"].dmx_send_frame(
                1,
                array.array('B', [255, 100, 0, 5])
            )
            print("done.")
            print("##### TESTS #####")
            print("self.identifier", self.identifier)
            repr(self.identifier)
            # print("check what OLAThread_States standby & running repr:")
            # blender internal repr is broken!!
            # repr(OLAThread_States.standby)
            # repr(OLAThread_States.running)
            # print("{!r}".format(OLAThread_States.standby))
            # print("{!r}".format(OLAThread_States.running))
            # print("check OLAThread_States repr:")
            # print("{!r}".format(OLAThread_States))
            # print("check OLAThread_States print:")
            # print(OLAThread_States)
            # print("check OLAThread_States.__dict__ repr:")
            # repr(OLAThread_States.__dict__)
            # print("done")
            print("list(OLAThread_States):")
            print(list(OLAThread_States))
            print("ola_manager.state: {!r}".format(
                cache[self.identifier]["ola_manager"].state
            ))
            print("##### END #####")
        else:
            print("have to do my init...")

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

        # execute (fill output with data)

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

        # cache[self.identifier]["data_received"] = [
        #     0, 200, 255,    # 1 türkis
        #     0, 255, 0,      # 4 green
        #     150, 100, 0,      # 7 yellow
        #     100, 0, 200,    # 10 lounge
        # ]
        ola_manager = cache[self.identifier]["ola_manager"]
        data_raw = ola_manager.get_received_data()
        # handle special case that there are no data available
        data_as_list = []
        if data_raw:
            data_as_list = data_raw.tolist()
            # print("data_raw", data_raw)
            # print("data_as_list", data_as_list)
        cache[self.identifier]["data_received"] = data_as_list

        # return cached data
        # print(
        #     "Node {}:  data_received: {}".format(
        #         self.identifier,
        #         cache[self.identifier]["data_received"]
        #     )
        # )
        return cache[self.identifier]["data_received"]

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

        init_successfull = True

        # setup import path for ola
        # sys.path.append("home/stefan/ola/python/")
        sys.path.append(self.olapath)
        try:
            # setup ola_manager
            # cache[self.identifier]["ola_manager"] = OLAThread()
            cache[self.identifier]["ola_manager"] = OLAThreadReceive()
        except Exception as e:
            init_successfull = False
            error_message = (
                "Error during creating ola_manager: " +
                str(e) + " " +
                "check your API Path!!"
            )
            showTextPopup(
                text=error_message,
                title="Error",
                icon="INFO"
            )
            print(error_message)
            raise e
        else:
            self.connectButtonUpdate()
            # print("universeListItemsUpdate")
            self.universeListItemsUpdate()

        # lastly set init done flag:
        cache[self.identifier]["init_done"] = init_successfull
        # if init_successfull:
        #     self.connect()

    def delete(self):
        """Clean up."""
        self.identifier

    ##########################################
    # internal functions

    def connect(self):
        """Connect to OLA Deamon."""
        ola_manager = cache[self.identifier]["ola_manager"]
        ola_manager.start_connection()
        self.connectButtonUpdate()

    def close(self):
        """Open Serial Port."""
        ola_manager = cache[self.identifier]["ola_manager"]
        ola_manager.stop_connection()
        self.connectButtonUpdate()


# class OLAClientSocket(bpy.types.NodeSocket, AnimationNodeSocket):
#     bl_idname = "an_OLAClientSocket"
#     bl_label = "OLAClient Socket"
#     dataType = "OLAClient"
#     allowedInputTypes = ["Object"]
#     drawColor = (0.5, 0.9, 1.0, 1)
#     storable = False
#     comparable = False
#
#     @classmethod
#     def getDefaultValue(cls):
#         return None
#
#     @classmethod
#     def getDefaultValueCode(cls):
#         return "None"
