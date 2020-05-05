#!/usr/bin/python3
"""
It performs a parameter sweep through RSSI and TxPower levels,
to determine the least bad default TxPower to use as a default
(for when the TxPower level is not known),
given our confidence level that the RSSI reading
represents a distance of 1.5m or less.

This script is slow.
Tor the given MIN/MAX RSSI levels (-81 to -60)
and MIN/MAX TxPower levels (-72 to -49)
the least bad default TxPower seems to be -60.4

IMPORTANT NOTE
--------------
This model assumes that all observed TxPower levels
and RSSI values in the range are equally likely.
This is naieve (and almost certainly untrue).

If/when the data becomes available,
it would be better to iterate through
all actual observations (with a TxPower)
and minimise the naieve baysean error.

Better still, the distribution of actual distances
in an given set of encounters is likely to be similar.
Encounter_set_percentile will be covariant with TxPower.
In other words, for any given set of encounters,
the ones with the highest RSSI values
are likely to represent similar distances
to the highest RSSI values in another encounter set
even between devices with different TxPower calibrations.

So, when TX power is not known,
we could estimated distance
(based on encounter_set_percentile)
rather than using a fixed default TxPower.

Even better still,
we could used the RSSI and estimated distances
(based on encounter_set_percentile)
to estimate the TxPower,
and then feed that back into a model
to make a second order distance estimate.
"""
import lib


# Values used in parameter sweep
#
# values taken from the opentrace ground-truth data
MAX_TXPOWER = -49  # actual max 49.4 dBm
MIN_TXPOWER = -72  # actual min 61.6 dBm
# expected values from approximately 1.5m range
# given opentrace ground-truth txpower data
MAX_RSSI = -60
MIN_RSSI = -81

# multiply by 10 for one decimal place,
# 100 for 2 decimal places, etc.
# this eats RAM, start with small numbers
GRANULARITY = 10


def sample_agreement(txpower_default):
    matches = []
    mismatches = []    
    for rssi_inc in range(
            MAX_RSSI * GRANULARITY,
            MIN_RSSI * GRANULARITY + 1,
            -1):
        rssi = float(rssi_inc) / GRANULARITY

        for p_inc in range(
                MAX_TXPOWER * GRANULARITY,
                MIN_TXPOWER * GRANULARITY + 1,
                -1):
            p = float(p_inc) / GRANULARITY

            c = lib.confidence(rssi, p)
            # sanity check
            if p <= rssi:
                assert c == lib.HIGH

            c2 = lib.confidence2(rssi, txpower_default=txpower_default)

            if c == c2:
                # default txpower has same result as actual txpower
                # i.e. default txpower gives the correct confidence reading
                matches.append(
                    {
                        'rssi': rssi, 'txpower': p,
                        'comparison': '%s == %s' % (c, c2)
                    }
                )
            else:
                # default txpower gives incorrect confidence reading
                mismatches.append(
                    {
                        'rssi': rssi, 'txpower': p,
                        'compariso121n': '%s != %s' % (c, c2)
                    }
                )

    return (matches, mismatches)


if __name__ == '__main__':

    best = None
    equal_best = []
    worst = None
    sample = {}

    # sweep -49dBm to -72dBm
    for i in range(
            MAX_TXPOWER * GRANULARITY,
            MIN_TXPOWER * GRANULARITY - 1,
            -1):

        point = float(i)/GRANULARITY
        matches, mismatches = sample_agreement(point)
        sample[point] = {"matches": matches, "mismatches": mismatches}

    for k in sample.keys():
        matches = sample[k]["matches"]
        mismatches = sample[k]["mismatches"]
        num_matches = len(matches)
        num_mismatches = len(mismatches)
        agreement = float(num_matches) / (num_matches + num_mismatches)
        if not best or best["agreement"] < agreement:
            best = {"default": k, "agreement": agreement}
            equal_best = [best, ]
        if best and best["agreement"] == agreement:
            equal_best.append({"default": k, "agreement": agreement})

        if not worst or worst["agreement"] > agreement:
            worst = {"default": k, "agreement": agreement}
    print("best = %s" % best)
    print("worst = %s" % worst)

    best_range_min = None
    best_range_max = None
    for eb in equal_best:
        if not best_range_min or best_range_min > eb["default"]:
            best_range_min = eb["default"]
        if not best_range_max or best_range_max < eb["default"]:
            best_range_max = eb["default"]
    if best_range_min != best_range_max:
        print("equal_best from %s to %s" % (best_range_min, best_range_max))
