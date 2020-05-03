#!/usr/bin/python3
#
import math


# These are tunable bias (sensitivity) terms.
# They incorporate unknown physical variables,
# such as fade margin, path loss etc.
#
# A range of 2-4 is apparently sensible.
# We should tune them to optimise the classification performance.
# e.g. minimise error surface of sample data
# (with known distance measures).
#
# If the data was available,
# it might be best to measure Reciever Operating Characteristic
# of the contract tracing protocol (rather than distance),
# i.e. tune the classifier against broad clinical outcomes.
#
N_MIN = 2.0  # upper estimate: high false alarms, low miss rate (less noisy)
N_MAX = 4.0  # lower estimate: high hit rate, low correct rejections (more noisy)


def distance(rssi: float, txpower: float, N: float):
    # see https://iotandelectronics.wordpress.com/2016/10/07/how-to-calculate-distance-from-the-rssi-value-of-the-ble-beacon/  # NOQA
    return math.pow(
        10,
        (txpower - rssi) / (10 * N)
    )


# returned values
HIGH = 'HIGH'
MODERATE = 'MODERATE'
LOW = 'LOW'


def confidence(rssi: float, txpower: float):
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
    if upper_estimate <= 1.5:
        c = HIGH
    elif lower_estimate <= 1.5:
        c = MODERATE
    else:
        c = LOW

    DEBUG = True
    if DEBUG:
        print("RSSI: %s  TxPower: %s  confidence: %s" % (rssi, p, c))
        print("upper estimate (bias = %s): %0.2fm" % (N_MIN, upper_estimate))
        print("lower estimate (bias = %s): %0.2fm" % (N_MAX, lower_estimate))
        print("")

    return c


if __name__ == '__main__':
    for rssi in range(-60, -81, -1):
        # TODO: generate a bunch of ground-truth rssi values
        # to validate the range being evaluated here
        for p in range(-49, -80, -1):
            c = confidence(rssi, p)
            
            # by definition, if TxPower < RSSI then distance < 1m
            if p <= rssi:
                assert c == HIGH
