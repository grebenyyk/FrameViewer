# FrameViewer
<img src="/FV_window.png" width="300">

Minimalist GUI to dispaly Siemens Frame Format (SFRM) files. The parser is implemented according to [GSAS2 SFRM parser](https://gsas-ii.readthedocs.io/en/latest/_modules/G2img_SFRM.html#GetSFRMData). Also check Tim Grüne's [sfrmtools](https://homepage.univie.ac.at/tim.gruene/research/programs/conv/sfrmtools/) for additional reference on the SFRM frame format. 

Live calculation of pointer 2θ value is implemented according to the [book](https://onlinelibrary.wiley.com/doi/book/10.1002/9781119356080) by Bob He and is based on the instrument parameters parsed from the frame header (detector distance and detector center). Avoid making serious decisions based on the 2θ readings: they can be unreliable, as no refinement of the instrument parameters is implemented. 

#### Dependencies
[numpy](https://numpy.org/install/), [matplotlib](https://matplotlib.org/stable/users/installing/index.html), [scikit-image](https://scikit-image.org/docs/stable/install.html)
