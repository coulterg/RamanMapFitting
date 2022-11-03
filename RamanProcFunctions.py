import numpy as np
from numpy.polynomial import Polynomial
import scipy as sp
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
import pandas as pd

def single_peak_excl(wn, data, peak, tolerance=110):
    # Receives a spectrum and peak position and returns the spectrum without that peak+-tolerance

    # Get array indices of peak-range xdata
    # x_indices = np.array([])

    x = wn[np.where((wn >= (peak-tolerance)) & (wn <= (peak+tolerance)))] # array of x values contained in the peak range

    inds = np.where(np.isin(wn, x))[0] # array index values for peak-range xvalues
    # remove indices from the 5 first and last datapoints - want to always include these
    ends = list(range(0, 5, 1))+list(range(len(wn)-5, len(wn), 1))

    new_inds = [x for x in inds if x not in ends]

    # x_indices = np.append(x_indices, new_inds)
    # x_indices =

    # Remove the wavenumber (x data) and corresponding spectrum data (y data)
    wn_excluded = np.delete(wn, new_inds)
    data_excluded = np.delete(data, new_inds)

    assert len(wn_excluded) == len(data_excluded)

    # return new arrays

    return wn_excluded, data_excluded

def poly_bg_sub(spectrum, raman_shift, peaks, order=6, plotter=False):
    '''This function:
    - receives a Raman spectrum with its Raman Shifts, and rough peak centres to exclude
    - fits a polynomial curve to the data, of the order specified (default=6)
    - subtracts the fitted curve from the data,
    - returns a background-subtracted spectrum array'''

    # Generate 'peakless' data in order to fit a proper background

    x_exclude, y_exclude = raman_shift, spectrum

    for peak in peaks:
        x_exclude, y_exclude = single_peak_excl(x_exclude, y_exclude, peak)

    # Fit polynomial background of order given

    pfit = Polynomial.fit(x_exclude, y_exclude, order)

    # Subtract fitted background from spectrum

    y_bg = pfit(raman_shift) # generates background at all x values required

    new_spectrum = spectrum-y_bg

    # Plot first map to check
    if plotter == True:
        plt.plot(raman_shift, spectrum)
        plt.plot(x_exclude, y_exclude)
        plt.plot(raman_shift, y_bg)
        plt.plot(raman_shift, new_spectrum)
        plt.title('Is the background appropriate?')
        plt.show()

    # Return bg subtracted spectrum

    return new_spectrum

def lorentzian_1(x, I1, x1, gam1):

    return((I1*gam1**2/((x-x1)**2+gam1**2)))

def lorentz_multi(x, *args):
    """Returns a f(x) at x given an arbitrary number of Lorentzian peaks
    as inferred by the number of *args which will always be:
    [I0, c0, gam0, I1, c1, gam1, ..., In, cn, gamn]"""

    lorentz_sum = 0
    for i, arg in enumerate(args):
        if i%3==0: I=arg
        elif i%3==1: c=arg
        elif i%3==2:
            gam=arg

            lorentz_sum += lorentzian_1(x, I, c, gam)


    return lorentz_sum

def peak_fit(wn, spectrum, peak_dict):
    '''Returns a dictionary of Intensity, Peak Centre, and FWHM of each fitted peak, labelled by the peak name,
    given a Raman spectrum, with its corresponding wavenumbers wn, and a dictionary of bounds for each parameter,
    which is by default set to D, G, and 2D with appropriate bounds'''

    bounds_lower, bounds_upper = [], []

    # TODO when looping through each spectrum, update the initial parameters to be those that fall out of the first fit

    initial_params = []

    # Put bounds and initial guesses into respective lists

    for peaks in peak_dict.values():

        for peak in peaks:
            bounds_lower += [peak[0]]
            bounds_upper += [peak[1]]
            initial_params += [peak[2]]

    # Fit the required number of Lorentzians to each spectrum

    popt_lorentz, pcov_lorentz = curve_fit(lorentz_multi, wn, spectrum, p0=initial_params, bounds=(bounds_lower, bounds_upper))

    # Create peak dictionary with each corresponding fitted params

    fitted_params = {}
    peaks = list(peak_dict)

    for i in range(len(peaks)):

        start = i*3

        fitted_params[peaks[i]] = [popt_lorentz[start:start+3]]

    return fitted_params



def single_spectrum_proc(spectra, wn, peak_dict):

    # Set peak centres
    peak_centres=[x[1][2] for x in peak_dict.values()]

    # Subtract background
    spectrum = poly_bg_sub(spectra, wn, peak_centres)

    # Fit peaks
    fit_params = peak_fit(wn, spectrum, peak_dict)
    peaks = {}

    for key in list(fit_params):
        peaks[key] = np.array(lorentzian_1(wn, *fit_params[key][0]))

    fit_sum = sum(peaks[key] for key in list(peaks))

    fig = plt.plot(wn, spectrum, 'lightgrey')

    ax = plt.gca()

    for peak_name, spec in peaks.items():

        ax.plot(wn, spec)
        ax.fill_between(wn, spec, alpha=0.2)

    ax.plot(wn, fit_sum, 'k--', dashes=(5,8))
    plt.show(block=False)
    plt.show()
    return fit_params

def map_proc(spectra, wn, peak_dict, order, reader):
    '''Given a 3D array of Raman map data and their wavenumbers, with a
    dictionary of peaks (peak names with lists of parameter bounds and initial guesses)
    and the map reader object, returns a pandas dataframe containing all fitted
    peak parameters'''

    x = reader.xpos # np array of x coordinates
    y = reader.ypos # np array f=of y coordinates
    w,h = reader.map_shape # pair or integers of map shape in units of xy coordinates

    reader.close()

    # Set peak centres
    peak_centres=[x[1][2] for x in peak_dict.values()]

    # Plot average spectum, fit peaks to check if reasonable, and update initial
    # parameters to those of the fitted average

    bg_sub_spectra = np.empty((w,h, len(wn)))

    # Sub background for each spectrum
    for row in range(w):
        for spectrum in range(h):
            bg_sub_spectra[row][spectrum] = poly_bg_sub(spectra[row][spectrum], wn, peak_centres, order, ((row==0) & (spectrum==0)))

    # Average spectra
    average_spectrum = np.mean(bg_sub_spectra, axis=(0,1))

    av_fit_params = single_spectrum_proc(average_spectrum, wn, peak_dict)

    for peak in peak_dict:
        peak_dict[peak][0][2] = av_fit_params[peak][0][0]
        peak_dict[peak][1][2] = av_fit_params[peak][0][1]
        peak_dict[peak][2][2] = av_fit_params[peak][0][2]


    results = np.array([])

    # Get column name list from peak dictionary - Intensity, centres and widths for all

    columns = []

    for key in peak_dict:
        columns += ['I_'+key, 'c_'+key, 'w_'+key]


    for x in range(w):
        for y in range(h):

            result = peak_fit(wn, bg_sub_spectra[x][y], peak_dict)

            result_keys = list(result)
            result_line = []

            for i in range(len(result)):# Through each peak fitted parameters

                for j in range(len(result[result_keys[i]][0])): # Through each parameter

                    if j==2:
                        result_line += [(result[result_keys[i]][0][j])*2] # Make it FWHM not HWHM
                    else:
                        result_line += [result[result_keys[i]][0][j]]

            results = np.append(results,result_line)

    print('loop finishes')

    results = results.reshape(w*h,len(columns))
    print(results)

    df = pd.DataFrame(results, index = np.arange(0, w*h), columns=columns)

    print(df.head())
    try:
        df['ID/IG'] = df.I_D/df.I_G
    except:
        print('No D or G intensity column')
    try:
        df['ID/ID_prime'] = df.I_D/df.I_D_prime
    except:
        print('No D or D_prime intensity column')
    try:
        df['I2D/IG'] = df.I_2D/df.I_G
    except:
        print('No 2D or G intensity column')

    return df
