#!/usr/bin/python
#
import math


# these are tunable bias terms that incorporate unknown physical variables,
# such as fade margin, path loss etc.
#
# A range of 2-4 is apparently sensible.
#
# we should tune these to optimise the performance of the classifier,
# e.g. minimise error surface of a large sample data of distance measures, OR
# a measured clinical performance Reciever Operating Characteristic

N_MIN = 2.0  # high false alarms, low miss
N_MAX = 4.0  # high hit, low correct rejections


def distance(rssi, txpower, N):
    # see https://iotandelectronics.wordpress.com/2016/10/07/how-to-calculate-distance-from-the-rssi-value-of-the-ble-beacon/  # NOQA
    #
    # TODO: type inputs to float
    rssi = float(rssi)
    txpower = float(txpower)
    return math.pow(
        10,
        (txpower - rssi) / (10 * N)
    )


for rssi in range(-60, -81, -1):
    # TODO: generate a bunch of ground-truth rssi values
    # to validate the range being evaluated here
    for p in range(-49, -80, -1):
        # TxPower is a "factory-calibrated, read-only constant"
        # indicates whats the expected RSSI at a distance of 1 meter
        #
        # TODO: iterate over the bluetrace anechoic phone samples,
        # rather than these guesses
        #
        # TODO: reference the opentrace code that calcualtes the TxPower
        # and make sure it means what I think it means (inconceivable)
        upper_estimate = distance(rssi, p, N_MIN)
        lower_estimate = distance(rssi, p, N_MAX)

        # TODO: remove the messages.append stuff,
        # (after def confidence: ...)
        messages = ["RSSI: %s  TxPower: %s" % (rssi, p), ]
        messages.append("upper estimate (bias = %s): %0.2fm" % (N_MIN, upper_estimate))  # NOQA
        messages.append("lower estimate (bias = %s): %0.2fm" % (N_MAX, lower_estimate))  # NOQA

        # TODO: def confidence(): ...
        if upper_estimate <= 1.5:
            messages.append("confidence: HIGH")
            if p <= rssi:
                # this should be an "assert" outside the function
                # by definition, if TxPower < RSSI then distance < 1m
                messages.append("Axiomatic (TxPower %s <= RSSI %s)" % (p, rssi))  # NOQA
        elif lower_estimate <= 1.5:
            messages.append("confidence: MODERATE")
        else:
            messages.append("confidence: LOW")

        for m in messages:
            print(m)
        print("")
