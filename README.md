# Raman Map Fitting

These scripts process Renishaw WiRe Raman spectroscopy data files, allowing for easy processing of Raman map data for statistical analyses.

The number, name, and initial guess parameters for new peaks can be controlled by editing the 'user_peaks' dictionary in the 'RamanProcessing.py' script.

Future updates will allow for visual addition of peaks through a GUI, allowing for more versatile, intuitive and user-friendly peak fitting.

## Usage

1) The peak dictionary in 'RamanProcessing.py' should be editted to reflect the number of peaks, and their initial guess conditions. For example, a typical Raman spectrum of graphene will display 3 peaks, the D, G, and 2D mode. Thus, the 'user_peaks' dictionary is definied as follows:

```
user_peaks = {
    'D':[[0., 10000., 40.],[1300,1390, 1350.],[0.,300., 25.]],
    'G':[[0., 10000., 250.],[1520,1610, 1590.],[0.,300., 10.]],
    '2D':[[0., 10000., 100.],[2620,2780, 2700.],[0.,300., 25.]]
    }
```

  Peak entries are defined by their lower and upper bounds, and initial guess conditions for their *Intensity*, *Position/Wavenumber* and *FWHM*.
```
'Name':[[intensity_lower_bound, intensity_upper_bound, intensity_initial_guess], [[position_lb, position_ub, position_ig],[FWHM_lb, FWHM_ub, FWHM_ig]]
'D':[[0., 10000., 40.],[1300,1390, 1350.],[0.,300., 25.]]
```

  Initial paramaters and bounds should be determnined by visually inspecting the spectra in WiRe (considering a background subtraction for intensity initial guesses). Initial parameters can be very approximate and will be updated for efficiency by fitting the defined peaks on the average spectrum of the map; this will be presented visually to determine suitability.

2) Run the script through a terminal; you will be prompted to drag and drop the '.wdf' file that you are processing onto the terminal. Hit enter. A background calculated using a polynomial fit of the data excluding peak regions will be fitted and subtracted.
![Background](https://user-images.githubusercontent.com/29359990/199729765-924319c8-c96d-414a-8ce2-f193edb704fd.png)

  Closing the figure continues the script. If not appropriate, cancel the fit and update the peak bounds or polynomial order of the background fit 'bg_order' in 'RamanProcessing.py'. Peak parameters are updated using an average spectrum, and are presented visually.

![Peaks](https://user-images.githubusercontent.com/29359990/199730389-df0cecdb-9ea7-4522-844e-a200b6631a9d.png)

  Closing the figure continues the script. If not appropriate, consider whether more peaks are required or a different peak shape is suitable. Peaks are currently fitted using Lorentzian lineshapes. Other shapes are not implemented currently.

3) Fitted peak parameters for individual spectra will be stored as 'I_'+key, 'c_'+key, 'w_'+key with the key as the defined peak name. Ratios of interest can be defined in the 'map_proc' function defined in 'RamanProcFunctions.py' using the defined peak names. e.g. for I(D)/I(G) ratios in graphene spectra:
```
df['ID/IG'] = df.I_D/df.I_G
```

  Plots of resulting fitted peaks/ratios can be defined in the main function body.

5) Fitted peak parameters and defined ratios are exported as a .csv file with the same name as the processed .wdf file, in the same directory as the .wdf file. This can be changed in the main function body.
<img width="656" alt="Screen Shot 2022-11-03 at 1 21 17 PM" src="https://user-images.githubusercontent.com/29359990/199731974-d946971a-1785-4ff5-abe1-3bb17bfa1b85.png">
