# FrameViewer
<img src="/CeO2.png" width="300">

Minimalist GUI to dispaly Siemens Frame Format (SFRM) files. 
The script parses the header and the data and displays the image with a possibility to save it as a PNG. 
The parser is implemented according to [GSAS2 SFRM parser](https://gsas-ii.readthedocs.io/en/latest/_modules/G2img_SFRM.html#GetSFRMData). 
Also check Tim Grüne's [sfrmtools](https://homepage.univie.ac.at/tim.gruene/research/programs/conv/sfrmtools/) for additional reference on the SFRM frame format. 

#### Dependencies
[numpy](https://numpy.org/install/), [matplotlib](https://matplotlib.org/stable/users/installing/index.html), [scikit-image](https://scikit-image.org/docs/stable/install.html)

#### To be implemented later
Switching through several frames in a directory, various colormaps
