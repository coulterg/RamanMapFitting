from renishawWiRE import WDFReader
import matplotlib.pyplot as plt
import numpy as np
from numpy.polynomial import Polynomial
import scipy as sp
from scipy.optimize import curve_fit
import pandas as pd

from RamanProcFunctions import *

to_process = input('Please drop the file to be processed here - ').rstrip()

bg_order = 5

reader = WDFReader(to_process)
wn = reader.xdata # np array of wavenumber/Raman shifts in spectra
spectra = reader.spectra # Either single spectrum or 3D array of map data

# TODO update initial Intensity parameters to be max value within a peak-range bound
# update initial fitting parameters to first spectrum fitted parameters


# Define peaks bounds and initial parameters to fit

user_peaks = {
    # 'D':[[0., 10000., 40.],[1300,1390, 1350.],[0.,300., 25.]],
    # 'G':[[0., 10000., 250.],[1520,1610, 1590.],[0.,300., 10.]],
    # "D_prime":[[0.,5000.,30.,],[1605.,1620.,1610.],[0.,50.,15.]],
    # '2D':[[0., 10000., 100.],[2620,2680, 2645.],[0.,300., 25.]]
    'G':[[0., 10000., 250.],[1520,1620, 1600.],[0.,300., 10.]]
}

def main():

    # Check spectrum data type - if 1, do single spectrum, if 3 do map processing

    if reader.measurement_type == 1:    # Single spectrum

        single_spectrum_proc(spectra, wn, user_peaks)


    elif reader.measurement_type == 3:  # Map data

        df = map_proc(spectra, wn, user_peaks, bg_order, reader)

        # fig, axes = plt.subplots(2)
        # axes[0].hist(df['ID/IG'], bins=50, range=(0,1))
        # axes[0].set_title('Histogram of ID/IG ratios')
        # axes[0].annotate(f"ID/IG: {np.mean(df['ID/IG']):.2f} +- {np.std(df['ID/IG']):.2f}", xy=(0.05, 0.8), xycoords='axes fraction')
        # # axes[1].hist(df['ID/ID_prime'], bins=100, range=(0,4))
        # # axes[1].set_title('Histogram of ID/ID_prime ratios')
        # # axes[1].annotate(f"ID/ID-PRIME: {np.mean(df['ID/ID_prime']):.2f} +- {np.std(df['ID/ID_prime']):.2f}", xy=(0.05, 0.8), xycoords='axes fraction')
        # axes[1].hist(df['I2D/IG'], bins=50, range=(0,1))
        # axes[1].set_title('Histogram of I2D/IG ratios')
        # axes[1].annotate(f"I2D/IG: {np.mean(df['I2D/IG']):.2f} +- {np.std(df['I2D/IG']):.2f}", xy=(0.05, 0.8), xycoords='axes fraction')
        #
        # plt.tight_layout()
        # plt.show()

        filename = to_process.split('.')[0]+'.xlsx'
        print(filename)
        df.to_excel(filename)



if __name__ == '__main__':
    main()
