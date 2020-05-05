#!/usr/bin/python3
#

import lib


if __name__ == '__main__':
    for rssi in range(-60, -81, -1):
        # TODO: generate a bunch of ground-truth rssi values
        # to validate the range being evaluated here
        for p in range(-49, -80, -1):
            c = lib.confidence(rssi, p)
            # by definition, if TxPower < RSSI then distance < 1m
            if p <= rssi:
                assert c == lib.HIGH
