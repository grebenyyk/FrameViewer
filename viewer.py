import contextlib
import tkinter as tk
from tkinter import filedialog
import numpy as np
import os
import time
import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import skimage.exposure as exposure

matplotlib.use("TkAgg")
root = tk.Tk()
root.title("Frame View")

# Adding a plotting area
fig = Figure(figsize=(3,5), dpi=120)
ax = fig.add_subplot(111)
ax.set_axis_off()
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.draw()
canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
fig.tight_layout()

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
    cent[0] += dist*np.tan(np.pi*twoth/180.0)
    File.seek(imageBeg)
    img = File.read(nxy)
    img2byte = File.read(N2byte)
    img4byte = File.read(N4byte)
    time0 = time.time()
    img = np.array(np.frombuffer(img, dtype='u1'), dtype=np.int32)
    img2byte = np.array(np.frombuffer(img2byte, dtype="u2"), dtype=np.int32)
    img4byte = np.array(np.frombuffer(img4byte, dtype="u4"), dtype=np.int32)
    #ins2byte = np.argwhere(img == 255)
    #for j,i in enumerate(list(ins2byte)):
    #    img[i] = img2byte[j]
    ins4byte = np.argwhere(img == 65535)
    for j,i in enumerate(list(ins4byte)):
        img[i] = img4byte[j]
    image = np.reshape(img, (sizexy[1],sizexy[0]))
    print(f"import time: {time.time()-time0:.3f}")
    data = {'pixelSize':pixSize, 'wavelength':wave, 'distance':dist, 'center':cent,
            'det2theta':0.0, 'size':sizexy, 'target':target, 
            'tilt':-twoth, 'rotation':90., 'twoth':str(round(twoth,1))}
    return lines, data, image  

def open_file():
    last_dir = ""
    with contextlib.suppress(Exception):
        with open("last_dir.txt", "r") as file:
            last_dir = file.read()
    file_path = filedialog.askopenfilename(initialdir = last_dir, title = "Select file", filetypes = (("Bruker frames", "*.sfrm"), ("all files", "*.*")))
    if file_path:
        last_dir = os.path.dirname(file_path)
        with open("last_dir.txt", "w") as file:
            file.write(last_dir)
        ax.clear()
        lines, data, image = read_sfrm(file_path)

        def update_gamma(*args):
            gamma = contrast_slider.get()
            image_upd = exposure.adjust_gamma(image, gamma=gamma)
            im = ax.imshow(image_upd, extent=(0, image.shape[1], 0, image.shape[0]), cmap='hot')
            canvas.draw()
            contrast_slider.bind("<ButtonRelease-1>", update_gamma)
        update_gamma()

        ax.set_axis_off()
        canvas.draw()

# Adding buttons and sliders
button_frame = tk.Frame(root)
button_frame.pack(side=tk.BOTTOM, fill=tk.X)

contrast_slider = tk.Scale(button_frame, from_=1.5, to=0.1, 
                           orient=tk.HORIZONTAL, resolution=0.005, showvalue=False,
                           length=400, label="Exposure")
contrast_slider.pack(side=tk.TOP, anchor=tk.W, padx=40, pady=10)
contrast_slider.set(1)

button1 = tk.Button(button_frame, text="Open", width=15, command=open_file)
button1.pack(side=tk.LEFT, anchor=tk.W, padx=40, pady=10)

def save_as():
    last_dir = ""
    with contextlib.suppress(Exception):
        with open("last_dir.txt", "r") as file:
            last_dir = file.read()
    file_path = filedialog.asksaveasfilename(initialdir = last_dir, title = "Save file", filetypes = (("PNG files", "*.png"), ("all files", "*.*")))
    if file_path:
        fig.subplots_adjust(left=0, bottom=0, right=1, top=1, wspace=0, hspace=0)
        fig.savefig(file_path, dpi=300, bbox_inches = 'tight')
button2 = tk.Button(button_frame, text="Save As...", width=15, command=save_as)
button2.pack(side=tk.RIGHT, anchor=tk.E, padx=40, pady=10)

root.mainloop()