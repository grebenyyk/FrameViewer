# FrameViewer
<img src="/CeO2.png" width="300">

Minimalist GUI to dispaly Siemens Frame Format (SFRM) files. 
The script parses the header and the data and displays the image with a possibility to save it as a PNG. 
The parser is implemented according to [GSAS2 SFRM parser](https://gsas-ii.readthedocs.io/en/latest/_modules/G2img_SFRM.html#GetSFRMData). 
Also check Tim Grüne's [sfrmtools](https://homepage.univie.ac.at/tim.gruene/research/programs/conv/sfrmtools/) for additional reference on the SFRM frame format. 

Live calculation of pointer 2θ value is implemented according to the [book by Bob He](https://onlinelibrary.wiley.com/doi/book/10.1002/9781119356080) based on the instrument parameters (detector distance and detector center) parsed from the frame header. Avoid making serious decisions based on the readings of 2θ values: they can be unreliable, as the refinement of the instrument parameters is not implemented so far. Also check [our recent paper](https://onlinelibrary.wiley.com/doi/epdf/10.1107/S1600576722005878?sentby=iucr) for another implementation of 2θ calculation.

#### Dependencies
[numpy](https://numpy.org/install/), [matplotlib](https://matplotlib.org/stable/users/installing/index.html), [scikit-image](https://scikit-image.org/docs/stable/install.html)

#### To be implemented later
Switching through several frames in a directory, various colormaps
