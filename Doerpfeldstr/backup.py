#!/usr/bin/env python3
# Eclipse SUMO, Simulation of Urban MObility; see https://eclipse.dev/sumo
# Copyright (C) 2025-2026 German Aerospace Center (DLR) and others.
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License 2.0 which is available at
# https://www.eclipse.org/legal/epl-2.0/
# SPDX-License-Identifier: EPL-2.0

from datetime import datetime
import os
import shutil
import sys

sys.path.append(os.path.join(os.environ["SUMO_HOME"], "tools"))
import sumolib


def main():
    configs = sys.argv[1:] if len(sys.argv) > 1 else ["view.sumocfg"]
    files = list(configs)
    for f in configs:
        for c in sumolib.options.readOptions(f):
            if c.name in ('net-file', 'route-files', 'additional-files', 'gui-settings-file'):
                files += c.value.split(',')
    if files:
        dirname = datetime.strftime(datetime.now(), 'bak/%Y%m%d-%H%M%S')
        os.makedirs(dirname)
        for f in files:
            shutil.copy2(f, dirname)
        shutil.copy2("tile.jpg", dirname)


if __name__ == "__main__":
    main()
