import datetime
import math

import _afbpyglue as libafb


class ComputationBinding:
    def __init__(self):
        binder = libafb.binder(
            {
                "uid": "py-binder",
                "verbose": 255,
                "port": 9998,  # no httpd
                "roothttp": ".",
                "rootdir": ".",
                "set": {
                    "modbus-binding.so": {
                        "$schema": "http://iot.bzh/download/public/schema/json/ctl-schema.json",
                        "metadata": {
                            "uid": "modbus-svc",
                            "version": "2.0",
                            "api": "modbus",
                            "info": "Generic KingPigeon default 10.18.2.40:502 slaveid=1 Test Config",
                        },
                        "modbus": [
                            {
                                "uid": "King-Pigeon-MT230",
                                "info": "King Pigeon 'MT230' Modbus TCP Remote I/O Module",
                                "uri": "tcp://127.0.0.1:5003",
                                "slaveid": 1,
                                "timeout": 250,
                                "autostart": 1,
                                "prefix": "mt230",
                                "privilege": "global privilege",
                                "hertz": 1,
                                "sensors": [
                                    {
                                        "uid": "sin",
                                        "type": "Register_Holding",
                                        "format": "UINT16",
                                        "register": 7,
                                        "count": 1,
                                    },
                                    {
                                        "uid": "cos",
                                        "type": "Register_Holding",
                                        "format": "UINT16",
                                        "register": 15,
                                        "count": 1,
                                    },
                                ],
                            }
                        ],
                    },
                    "redis-binding.so": {
                        "$schema": "http://iot.bzh/download/public/schema/json/ctl-schema.json",
                        "metadata": {
                            "uid": "Redis Binding",
                            "version": "1.0",
                            "api": "redis",
                            "info": "Redis Client binding",
                        },
                        "onload": [{"redis": {"hostname": "127.0.0.1", "port": 6379}}],
                    },
                },
            }
        )
        modbus_binding = libafb.binding(
            {
                "uid": "modbus-test",
                "export": "private",
                "path": "/usr/local/redpesk/modbus-binding/lib/modbus-binding.so",
            }
        )

        redis_binding = libafb.binding(
            {
                "uid": "redis",
                "path": "/usr/local/redpesk/redis-tsdb-binding/lib/redis-binding.so",
            }
        )

        libafb.loopstart(binder, self._on_binder_init)

    def _on_binder_init(self, binder, _):
        self._sin = None
        self._cos = None
        self._last_ts = 0

        user_data = binder

        libafb.callsync(binder, "modbus", "mt230/sin", {"action": "subscribe"})
        # the event handlers must live as long as the event callbacks
        # so we attach the return value of `evthandler` to self
        self._sin_handler = libafb.evthandler(
            binder,
            {"uid": "modbus", "pattern": "*/sin", "callback": self.on_sin_value},
            user_data,
        )
        libafb.callsync(binder, "modbus", "mt230/sin", {"action": "subscribe"})

        self._cos_handler = libafb.evthandler(
            binder,
            {"uid": "modbus", "pattern": "*/cos", "callback": self.on_cos_value},
            user_data,
        )
        libafb.callsync(binder, "modbus", "mt230/cos", {"action": "subscribe"})

        return 0

    def on_update_done(self, handle, status, _1, _2, error, error_msg, tag):
        # print("CB", error_msg)
        return 0

    def update_direction(self, binder):
        ts_ms = int(datetime.datetime.timestamp(datetime.datetime.now()) * 1000)
        if ts_ms - self._last_ts < 1:
            return

        if self._sin is not None and self._cos is not None:
            angle_deg = math.atan2(self._sin, self._cos) / math.pi * 180.0
            libafb.callasync(
                binder,
                "redis",
                "add",
                self.on_update_done,
                None,  # context
                {
                    "key": "wind_direction_deg",
                    "timestamp": f"{ts_ms}",
                    "value": angle_deg,
                },
            )

        self._last_ts = ts_ms

    def on_sin_value(self, binder, event_name, user_data, value):
        self._sin = value
        self.update_direction(user_data)

    def on_cos_value(self, binder, event_name, user_data, value):
        self._cos = value
        self.update_direction(user_data)


c = ComputationBinding()
