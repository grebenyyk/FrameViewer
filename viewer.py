import contextlib
import pathlib
import tkinter as tk
from tkinter import filedialog
import numpy as np
import os
import time
import matplotlib
from matplotlib import cm
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import skimage.exposure as exposure
import ast
import glob

matplotlib.use("TkAgg")
root = tk.Tk()
root.title("FrameViewer")
root.resizable(False, False)

# Adding a plotting area
fig = Figure(figsize=(3,4.8), dpi=120)
ax = fig.add_subplot()
ax.set_axis_off()
fig.tight_layout()
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.draw()
canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH)

#colormap_names = [m for m in cm.datad]
colormap_names = ['hot', 'viridis', 'gray', 'plasma', 'inferno', 'gnuplot', 'cividis']
colormap_var = tk.StringVar()
colormap_var.set('hot')
colormap_dropdown = tk.OptionMenu(root, colormap_var, *colormap_names)

# Reading and parsing .sfrm file
def read_sfrm(filename):
    File = open(filename, "rb")
    sizexy = [0,0]
    pixSize = [135,135]
    cent = [0,0]
    wave = 0.710730
    dist = 89
    stream = File.read()
    if 'bytes' in str(type(stream)):
        stream = stream.decode("latin-1")
    starter = 'IMG: '
    meanwaves = {'Cu':1.54051,'Ti':2.74841,'Cr':2.28962,'Fe':1.93597,
	        'Co':1.78892,'Mo':0.70926,'Ag':0.559363}
    imageBeg = stream.find(starter)+4
    head = np.array(list(stream[:imageBeg].split('CFR: ')[0]))
    head = head.reshape(-1,80)
    lines = []
    for line in head:
        line = ''.join(line)
        lines.append(line)
        fields = line.split(':')[1].split()
        if "TARGET" in line:
            wave = meanwaves[fields[0]]
            target = fields[0].capitalize()
        elif "DISTANC" in line:
            dist = float(fields[0])*10
        elif "ANGLES" in line:
            twoth = float(fields[0])
        elif "CENTER" in line:
            cent = [float(fields[0]), float(fields[1])]
        elif "NROWS" in line:
            sizexy[1] = int(fields[0])
        elif "NCOLS" in line:
            sizexy[0] = int(fields[0])
        elif "HDRBLKS" in line:
            imageBeg = 512*int(fields[0])
        elif "NOVERFL" in line:
            Nunder = int(fields[0])
            N2byte = 2*int(fields[1])
            if N2byte%16:
                N2byte = (N2byte//16+1)*16
            N4byte = 4*int(fields[2])
            if N4byte%16:
                N4byte = (N4byte//16+1)*16
    
    nxy = sizexy[0]*sizexy[1]
    cent = [cent[0]*pixSize[0]/1000.0, cent[1]*pixSize[1]/1000.0]
    
    # No center displacement to implement 2θD calculation as in [Tsymbarenko et al. JAC (2022)]
    # as well as in [He, B. B. (2018). Two-dimensional X-ray diffraction]
    #cent[0] += dist*np.tan(np.pi*twoth/180.0)
    
    File.seek(imageBeg)
    img = File.read(nxy)
    img2byte = File.read(N2byte)
    img4byte = File.read(N4byte)
    time0 = time.time()
    img = np.array(np.frombuffer(img, dtype='u1'), dtype=np.int32)
    img2byte = np.array(np.frombuffer(img2byte, dtype="u2"), dtype=np.int32)
    img4byte = np.array(np.frombuffer(img4byte, dtype="u4"), dtype=np.int32)
    ins2byte = np.argwhere(img == 255)
    for j,i in enumerate(list(ins2byte)):
        img[i] = img2byte[j]
    ins4byte = np.argwhere(img == 65535)
    for j,i in enumerate(list(ins4byte)):
        img[i] = img4byte[j]
    image = np.reshape(img, (sizexy[1],sizexy[0]))
    print(f"import time: {time.time()-time0:.3f}")
    data = {'pixelSize':pixSize, 'wavelength':wave, 'distance':dist, 'center':cent,
            'det2theta':0.0, 'size':sizexy, 'target':target, 
            'tilt':-twoth, 'rotation':90., 'twoth':str(round(twoth,1))}
    with open("current_header.txt", "w") as file:
        file.write(str(data))
    return lines, data, image  

def load_file(file_path):
    last_dir = os.path.dirname(file_path)
    dir_path, filename = os.path.split(file_path)
    dirs = dir_path.split(os.path.sep)
    last_two_dirs = os.path.sep.join(dirs[-1:])
    result = f".../{last_two_dirs}{os.path.sep}{filename}"
    label3.config(text=f'{result}')
    with open("last_dir.txt", "w") as file:
        file.write(last_dir)
    ax.clear()
    lines, data, image = read_sfrm(file_path)

    # def update_gamma(*args):
        # gamma = contrast_slider.get()
        # image_upd = exposure.adjust_gamma(image, gamma=gamma)
        # im = ax.imshow(image_upd, extent=(0, image.shape[1], 0, image.shape[0]), cmap='hot')
        # canvas.draw()
        # contrast_slider.bind("<ButtonRelease-1>", update_gamma)
    # update_gamma()
    
    def update_contrast(*args):
        black_level = black_slider.get()
        white_level = white_slider.get()
        p2, p98 = np.percentile(image, (black_level * 100, white_level * 100))
        image_upd = exposure.rescale_intensity(image, in_range=(p2, p98))
        im = ax.imshow(image_upd, extent=(0, image.shape[1], 0, image.shape[0]), cmap='hot')
        cmap_name = colormap_var.get()
        cmap = cm.get_cmap(cmap_name)
        im.set_cmap(cmap)
        canvas.draw()
        black_slider.bind("<ButtonRelease-1>", update_contrast)
        white_slider.bind("<ButtonRelease-1>", update_contrast)
    update_contrast()
    colormap_var.trace("w", update_contrast)
    ax.set_axis_off()
    canvas.draw()

# Function to open the file dialog and select a file
def open_file():
    global file_index, file_list
    last_dir = ""
    with contextlib.suppress(Exception):
        with open("last_dir.txt", "r") as file:
            last_dir = file.read()
    file_path = filedialog.askopenfilename(initialdir=last_dir, title="Select file", filetypes=(("Bruker frames", "*.sfrm"), ("all files", "*.*")))
    if file_path:
        last_dir = os.path.dirname(file_path)
        with open("last_dir.txt", "w") as file:
            file.write(last_dir)
        file_index = 0
        file_list = sorted(glob.glob(os.path.join(last_dir, '*.sfrm')))
        load_file(file_path)

button_frame0 = tk.Frame(root, height=20)
button_frame0.pack(fill=tk.X)
bg_color = '#f0f0f0'
black_slider = tk.Scale(button_frame0, from_=0.55, to=0, 
                        orient=tk.HORIZONTAL, resolution=0.005, showvalue=False,
                        length=200, width=15, troughcolor=bg_color)
black_slider.set(0)
black_slider.place(relx=0.05, rely=0.5, anchor=tk.W)

white_slider = tk.Scale(button_frame0, from_=1, to=0.6, 
                        orient=tk.HORIZONTAL, resolution=0.005, showvalue=False,
                        length=200, width=15, troughcolor=bg_color)
white_slider.set(1)
white_slider.place(relx=0.95, rely=0.5, anchor=tk.E)
colormap_dropdown.place(relx=0.74, rely=0.83)
colormap_label = tk.Label(root, text="Colormap:")
colormap_label.place(relx=0.57, rely=0.831)

# Adding buttons 
button_frame = tk.Frame(root)
button_frame.pack(side=tk.BOTTOM, fill=tk.X)
button1 = tk.Button(button_frame, text="Open", width=20, command=open_file)
button1.pack(side=tk.LEFT, anchor=tk.W, padx=20, pady=10)

def save_as():
    last_dir = ""
    with contextlib.suppress(Exception):
        with open("last_dir.txt", "r") as file:
            last_dir = file.read()
    file_path = filedialog.asksaveasfilename(initialdir = last_dir, title = "Save file", filetypes = (("PNG files", "*.png"), ("all files", "*.*")))
    if file_path:
        fig.subplots_adjust(left=0, bottom=0, right=1, top=1, wspace=0, hspace=0)
        fig.savefig(file_path, dpi=300, bbox_inches = 'tight')
button2 = tk.Button(button_frame, text="Save As...", width=20, command=save_as)
button2.pack(side=tk.RIGHT, anchor=tk.E, padx=20, pady=10)

coord_label = tk.Label(master=root)
coord_label.pack(padx=20,anchor='w')
coord_label2 = tk.Label(master=root)
coord_label2.pack(padx=20, anchor='w')
label3 = tk.Label(master=root)
label3.pack(padx=20, anchor='w')

# Global variables for switching through files
file_index = 0
file_list = []
# Function to load the next file in the directory
def load_next_file():
    global file_index, file_list
    if file_index < len(file_list) - 1:
        file_index += 1
    else:
        file_index = 0
    file_path = file_list[file_index]
    load_file(file_path)
# Function to load the previous file in the directory
def load_previous_file():
    global file_index, file_list
    if file_index > 0:
        file_index -= 1
    else:
        file_index = len(file_list) - 1
    file_path = file_list[file_index]
    load_file(file_path)

# Create left arrow button
left_arrow_button = tk.Button(root, text='Previous file', command=load_previous_file, width=20)
left_arrow_button.pack(side=tk.LEFT, padx=20)
# Create right arrow button
right_arrow_button = tk.Button(root, text='Next file', command=load_next_file, width=20)
right_arrow_button.pack(side=tk.RIGHT,padx=20)

def on_mouse_move(event):
    if event.xdata is not None and event.ydata is not None:
        # Mouse is over the image area
        x, y = int(event.xdata), int(event.ydata)
        data_text = pathlib.Path('current_header.txt').read_text()
        data = ast.literal_eval(data_text)
        
        # Calculation of 2theta angle

        # Works only for detector poisition 2theta = 0 
        #curr_two_theta = 2 * 180 / np.pi * np.arctan((((data['center'][0])-(x)*((data['pixelSize'][0])/1000))**2 + ((data['center'][1])-(y)*(data['pixelSize'][1])/1000)**2)**0.5/(data['distance']))    
        
        # as in D. Tsymbarenko et al. JAC (2022)
        # not working as of now, probably something wrong with the code
        xx = (data['center'][0])-(x)*((data['pixelSize'][0])/1000)
        yy = (data['center'][1])-(y)*((data['pixelSize'][1])/1000)
        DD = data['distance']
        twothetad = data['twoth']
        cos2theta = (((float(DD)**2 + xx**2)/(float(DD)**2 + xx**2 + yy**2))**0.5) * np.cos((float(twothetad) - np.arctan(xx/float(DD)) * 180 / np.pi) * np.pi / 180)
        #curr_two_theta = np.arccos(cos2theta) * 180 / np.pi

        # as in B. He. Two-dimensional X-ray diffraction (2018)
        chisl = xx * np.sin(-float(twothetad) * np.pi / 180) + float(DD) * np.cos(-float(twothetad) * np.pi / 180)
        znam = (float(DD)**2 + (xx)**2 + (yy)**2)**0.5
        curr_two_theta = 2 * np.arccos(chisl/znam) * 180 / np.pi

        # Update the label with the current coordinates
        coord_label.config(text=f'X, Y = {x}, {y}')
        coord_label2.config(text=f'2θ = {curr_two_theta:.2f}°')
        # Change the cursor to a crosshair
        root.config(cursor="crosshair")
    else:
        root.config(cursor="")

canvas.mpl_connect('motion_notify_event', on_mouse_move)
root.mainloop()