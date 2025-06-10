#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os
sys.path.append(os.pardir)  # 親ディレクトリのファイルをインポートするための設定
import numpy as np
import matplotlib.pyplot as plt



def get_catalyst_positions(particles):
    positions = []
    for x in range(particles.shape[0]):
        for y in range(particles.shape[1]):
            if particles[x, y]['type'] == 'CATALYST':
                positions.append((x, y))
    return positions

def get_catalyst_manhattan_distances(positions, initial_positions):
    distances = []
    for idx, pos in enumerate(positions):
        if idx < len(initial_positions):
            x0, y0 = initial_positions[idx]
            x, y = pos
            d = abs(x - x0) + abs(y - y0)
            distances.append(d)
    return distances
