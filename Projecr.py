import math
import sys
import numpy as np
import cv2
import tkinter as tk
import tkinter.font as font
from tkinter import Button, filedialog
from PIL import Image, ImageTk
from tkinter.messagebox import showinfo


class Images:
    im = None


root = tk.Tk()
root.configure(background='black')
canv = tk.Canvas(root, width=700, height=700)
canv.place(x=350, y=40)


def showimage():
    canv.delete()
    im = filedialog.askopenfile(title='Please select one (any) frame from your set of images.',
                                filetypes=[('Image Files', ['.jpeg', '.jpg', '.png'])])
    global test
    global im2
    im2 = cv2.imread(im.name, 0)
    image = Image.fromarray(im2)
    test = ImageTk.PhotoImage(image)
    canv.create_image(50, 10, anchor=tk.NW, image=test)
    showinfo(
        title='Selected File',
        message=im.name
    )

    Images.im = im2


btn = tk.Button(root, text=" Browse Image ", bg='#0080ff', pady=20, padx=40, command=lambda: showimage())
btn.grid(row=2, column=1, columnspan=1)
##############################
btn2 = tk.Button(root, text="    Exit    ", command=lambda: exit())
btn.grid(row=1, column=1)

###############################
Lablace_Button = Button(root, text=" Lablace ", pady=20, padx=40, bg='#0080ff', command=lambda: filter_laplace)
Lablace_Button.grid(row=2, column=1)

##############################
min_button = Button(root, text="     Min     ", bg='#0080ff', pady=20, padx=40)
min_button.grid(row=3, column=1)

#############################
fourir_button = Button(root, text=" Fourir ", bg='#0080ff', pady=20, padx=40, command=lambda: fourir)
fourir_button.grid(row=4, column=1)

#############################
log_button = Button(root, text="     Log     ", bg='#0080ff', pady=20, padx=40, command=lambda: log)
log_button.grid(row=5, column=1)

############################
power_button = Button(root, text="     Power     ", bg='#0080ff', pady=20, padx=40, command=lambda: power)
power_button.grid(row=6, column=1)

############################
histogram_button = Button(root, text=" Histogram ", bg='#0080ff', pady=20, padx=40, command=lambda: histogram)
histogram_button.grid(row=7, column=1)

###########################
gause_button = Button(root, text="    Gause   ", bg='#0080ff', pady=20, padx=40, command=lambda: gause)
gause_button.grid(row=8, column=1)

##########################
median_button = Button(root, text="     Median    ", bg='#0080ff', pady=20, padx=40, command=lambda: filter_median)
median_button.grid(row=9, column=1)

#########################
sobelOperator_button = Button(root, text="     Slope    ", bg='#0080ff', pady=20, padx=40,
                              command=lambda: sobelOperator)
sobelOperator_button.grid(row=10, column=1)

########################
AVG_buttton = Button(root, text="    Average   ", bg='#0080ff', pady=20, padx=40, command=lambda: AVG)
AVG_buttton.grid(row=11, column=1)

root.title("Filters Project")
root.geometry("800x800")
root.mainloop()


def upgrade_image(im):
    canv.delete()
    # im2 = cv2.imread(im.name, 0)
    image = Image.fromarray(im2)
    test = ImageTk.PhotoImage(image)
    canv.create_image(50, 10, anchor=tk.NW, image=test)
    showinfo(
        title='Selected File',
        message=im.name
    )


def im2double(self, image):
    max_val = np.max(image)
    min_val = np.min(image)
    val = (image.astype('float') - min_val) / (max_val - min_val)
    return val


def filter_laplace(im2):
    img = im2
    img_out = img.copy()

    height = img.shape[0]
    width = img.shape[1]

    laplace = (1 / 9) * np.array(
        [[0, 1, 0],
         [1, -4, 1],
         [0, 1, 0]])
    sum(sum(laplace))

    for i in range(1, height - 1):
        for j in range(1, width - 1):
            sum1 = 0
            for k in range(-1, 2):
                for l in range(-1, 2):
                    a = img.item(i + k, j + l)
                    w = laplace[k, l]
                    sum1 = sum1 + (w * a)
            b = sum1
            img_out.itemset((i, j), b)
    img_out = np.array(img_out)
    cv2.imshow("Filter Laplace", img_out)
    return img_out


def filter_min(image2):
    img = image2
    img_out = img.copy()

    height = img.shape[0]
    width = img.shape[1]
    for i in range(3, height - 3):
        for j in range(3, width - 3):
            min1 = 255
            for k in range(-3, 4):
                for x in range(-3, 4):
                    a = img.item(i + k, j + x)
                    if a < min1:
                        min1 = a
        b = min1
        img_out.itemset((i, j), b)
        cv2.imshow("Filter Min", img_out)
        return img_out


def fourir(image2):
    img = image2
    f = np.fft.fft2(img)
    fshift = np.fft.fftshift(f)
    magnitude_spectrum = 20 * np.log(np.abs(fshift))
    img_and_magnitude = np.concatenate((img, magnitude_spectrum), axis=1)
    cv2.imshow("Fourir", img_and_magnitude)


def log(image2):
    img = image2
    imagee = image2.im2double(img)
    row, col = np.shape(imagee)
    for r in range(row):
        for c in range(col):
            imagee[r][c] = 5 * (math.log(1 + imagee[r][c]))
    cv2.imshow("Log transmation", imagee)


def power(img2):
    img = img2
    imagee = img2.im2double(img)
    row, col = np.shape(imagee)
    for r in range(row):
        for c in range(col):
            imagee[r][c] = 5 * (math.pow(imagee[r][c], 5))
    cv2.imshow("Power", imagee)


def histogram(image2):
    img = image2
    pix = np.array(img)
    pix2 = np.copy(pix)
    rk, nk = np.unique(pix, return_counts=True)
    pk = nk / img.size
    sk = np.cumsum(pk)
    mul = sk * np.max(pix)
    roundVal = np.round(mul)

    for i in range(len(pix)):
        for j in range(len(pix[0])):
            pix2[i][j] = roundVal[np.where(rk == pix[i][j])]

    cv2.imshow("Histogram", pix2)
    return pix2


def gause(image2):
    img = image2
    global sum1
    img_out = img.copy()

    height = img.shape[0]
    width = img.shape[1]

    gauss = (1.0 / 57) * np.array(
        [[0, 1, 2, 1, 0],
         [1, 3, 5, 3, 1],
         [2, 5, 9, 5, 2],
         [1, 3, 5, 3, 1],
         [0, 1, 2, 1, 0]])

    sum(sum(gauss))

    for i in range(2, height - 2):
        for j in range(2, width - 2):
            sum1 = 0
            for k in range(-2, 3):
                for x in range(-2, 3):
                    a = img.item(i + k, j + x)
                    p = gauss[2 + k, 2 + x]
                    sum1 = sum + (p * a)
            b = sum
            img_out.itemset((i, j), b)
    cv2.imshow("Gause", img_out)
    return img_out


def filter_median(img2):
    img = im2
    img_out = img.copy()

    height = img.shape[0]
    width = img.shape[1]

    for i in range(3, height - 3):
        for j in range(3, width - 3):
            neighbors = []
            for k in range(-3, 4):
                for l in range(-3, 4):
                    a = img.item(i + k, j + l)
                    neighbors.append(a)
            neighbors.sort()
            median = neighbors[24]
            b = median
            img_out.itemset((i, j), b)

    cv2.imshow("Filter Median", img_out)
    return img_out


def sobelOperator(image2):
    img = image2
    container = np.copy(img)
    size = container.shape
    for i in range(1, size[0] - 1):
        for j in range(1, size[1] - 1):
            gx = (img[i - 1][j - 1] + 2 * img[i][j - 1] + img[i + 1][j - 1]) - (
                    img[i - 1][j + 1] + 2 * img[i][j + 1] + img[i + 1][j + 1])
            gy = (img[i - 1][j - 1] + 2 * img[i - 1][j] + img[i - 1][j + 1]) - (
                    img[i + 1][j - 1] + 2 * img[i + 1][j] + img[i + 1][j + 1])
            container[i][j] = min(255, np.sqrt(gx ** 2 + gy ** 2))
    cv2.imshow("Sobel", container)


def AVG(image2):
    img = image2
    height = img.shape[0]
    width = img.shape[1]
    avg = 1 / 9

    for i in range(height, 2, 1):
        for j in range(width, 2, 1):
            img[i][j] = (image2[i - 1][j - 1] * avg + image2[i - 1][j] * avg
                         + image2[i - 1][j + 1] * avg + image2[i][j - 1] * avg
                         + image2[i][j] * avg + image2[i][j + 1] * avg
                         + image2[i + 1][j - 1] * avg + image2[i + 1][j] * avg
                         + image2[i + 1][j + 1] * avg)
            round(img[i][j])

    cv2.imshow("AVG", img)
    return img


""""
def filter_max(im2):
            img = im2
        img_out = img.copy()

        height = img.shape[0]
        width = img.shape[1]

        for i in range(3, height - 3):
            for j in range(3, width - 3):
                max = 0
                for k in range(-3, 4):
                    for l in range(-3, 4):
                        a = img.item(i + k, j + l)
                        if a > max:
                            max = a
                b = max
                img_out.itemset((i, j), b)
        ocv.imshow("Filter Max", img_out)
"""

