#!/usr/bin/env python3
# Eclipse SUMO, Simulation of Urban MObility; see https://eclipse.dev/sumo
# Copyright (C) 2025-2026 German Aerospace Center (DLR) and others.
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License 2.0 which is available at
# https://www.eclipse.org/legal/epl-2.0/
# SPDX-License-Identifier: EPL-2.0

import os
import random
import sys

sys.path.append(os.path.join(os.environ["SUMO_HOME"], "tools"))
import sumolib


def main():
    f = sys.argv[1]
    outf = f.replace("vehicles", "persons")
    routes = {}
    for r in sumolib.xml.parse(sys.argv[1], "route"):
        edges = r.edges.split()
        routes[r.id] = (edges[0], edges[-1], [s.busStop for s in r.stop])
    with sumolib.openz(outf, "w") as out:
        sumolib.xml.writeHeader(out, root="routes")
        for v in sumolib.xml.parse(sys.argv[1], "vehicle"):
            depart = float(v.depart)
            total = 0
            if 6 * 3600 < depart < 7 * 3600:
                o, d, stops = routes[v.route]
                number = random.randint(5, 12 if v.type in ("bus", "tram") else 250)
                total += number
                print("""    <personFlow id="p%s" begin="triggered" period="0.1" number="%s" color="random">
        <ride from="%s" to="%s" lines="%s"/>
    </personFlow>""" % (v.id, number, o, d, v.id), file=out)
                for s in stops:
                    number = random.randint(5, 12 if v.type in ("bus", "tram") else 250)
                    total += number
                    if total > 85:
                        break
                    print("""    <personFlow id="p%s_%s" begin="triggered" period="0.1" number="%s" color="random">
        <ride from="%s" busStop="%s" lines="%s"/>
    </personFlow>""" % (v.id, s, number, o, s, v.id), file=out)
        print("</routes>", file=out)


if __name__ == "__main__":
    main()
