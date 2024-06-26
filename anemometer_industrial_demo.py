#!/usr/bin/env python3
import argparse
import datetime
import json
import math

import libafb


class ComputationBinding:
    def __init__(self, binding_config: dict):

        binder = libafb.binder(
            {
                "uid": "py-binder",
                "verbose": 255,
                "port": 9998,
                "roothttp": ".",
                "rootdir": ".",
                "set": binding_config,
            }
        )
        modbus_binding = libafb.binding(
            {
                "uid": "modbus",
                "path": "/usr/redpesk/modbus-binding/lib/modbus-binding.so",
            }
        )

        redis_binding = libafb.binding(
            {
                "uid": "redis",
                "path": "/usr/redpesk/redis-tsdb-binding/lib/redis-binding.so",
            }
        )

        libafb.loopstart(binder, self.on_binder_init)

    def on_binder_init(self, binder, _):
        self._sin = None
        self._cos = None
        self._last_ts = 0

        # the event handlers must live as long as the event callbacks
        # so we attach the return value of `evthandler` to self
        self._sin_handler = libafb.evthandler(
            binder,
            {"uid": "modbus", "pattern": "*/sin", "callback": self.on_sin_value},
        )
        libafb.callsync(binder, "modbus", "m100t/sin", {"action": "subscribe"})

        self._cos_handler = libafb.evthandler(
            binder,
            {"uid": "modbus", "pattern": "*/cos", "callback": self.on_cos_value},
        )
        libafb.callsync(binder, "modbus", "m100t/cos", {"action": "subscribe"})

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
                None,  # update callback,
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
        self.update_direction(binder)

    def on_cos_value(self, binder, event_name, user_data, value):
        self._cos = value
        self.update_direction(binder)


parser = argparse.ArgumentParser(
    description="Binding that computes wind direction and speed and publish them to Redis TSDB"
)

parser.add_argument(
    "-c",
    "--conf",
    action="store",
    help="JSON Binding config file to load",
    required=True,
)
args = parser.parse_args()

with open(args.conf, "r") as fi:
    binding_config = json.load(fi)

c = ComputationBinding(binding_config)
