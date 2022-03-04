from scipy.io import loadmat
import numpy as np
import pandas as pd

import csv

path = r"C:\Users\moham\OneDrive\Documents\Signal-Viewer\Signal-Viewer\Samples\EMG\emg_healthy.dat"

# read flash.dat to a list of lists
datContent = [i.strip().split() for i in open(path, errors="ignore",encoding="utf-8").readlines()]

print(datContent)