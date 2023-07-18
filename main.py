
import numpy as np
import cv2 as cv
import os

from shutil import copyfile


CompareSize = (64, 64)

threshold = 5  # changable

def readImageFromPath(fPath):
    stream = open(fPath, "rb")
    byt = bytearray(stream.read())
    stream.close()
    numpyarray = np.asarray(byt, dtype=np.uint8)
    return cv.imdecode(numpyarray, cv.IMREAD_GRAYSCALE)



def LoadImagesFromFolder(folder):
    images = [] #scaled image, shape, file name

    folderList = os.listdir(folder)
    folderItemCount = len(folderList) - 1

    print("\rLoading images: {0}%".format(0), end=" ")

    for index in range(len(folderList)):
        filename = folderList[index]

        img = readImageFromPath(format("{0}/{1}".format(folder, filename)))

        if img is not None:
            images.append((cv.resize(img, CompareSize), img.shape, filename))

        progress = round((index / folderItemCount) * 100, 2)
        print("\rLoading images: {0}%".format(progress), end=" ")

    return images


def Move(filename):
    oldPath = "{0}/{1}".format(folderName, filename)
    newPath = "{0}/{1}".format(newFolderName, filename)

    copyfile(oldPath, newPath)


def SameImages(img1, img2):
    differenceIMG = cv.absdiff(img2, img1)

    avg = np.average(differenceIMG)

    return avg < threshold


def CompareIMGs(imgX, imgY):

    return SameImages(imgX, imgY)


def Compare(i1, i2):
    img1 = i1[0]
    img2 = i2[0]

    return CompareIMGs(img1, img2)

print("The pictures will be resized to {0}.".format(CompareSize))
NewSize = input("Input a number if you want to change the resolution. (Min: 16 / Max: 256)\n>>>")
if(NewSize.isdigit()):
    NewRes = int(NewSize)
    if NewRes <= 256 and NewRes >= 16:
        CompareSize = (NewRes, NewRes)

print("The max threshold between images is {0}.".format(threshold))
NewThreshold = input("Input a number if you want to change the resolution. (Min: 0 / Max: 25)\n>>>")
if(NewSize.isdigit()):
    NewThr = int(NewThreshold)
    if NewThr <= 25 and NewThr > 0:
        threshold = NewThr

folderName = str(input("Name / Path of the folder to import pictures from:\n>>>"))
imgs = LoadImagesFromFolder(folderName)

imageCount = len(imgs)
print("\n{0} images found in \"{1}\" folder".format(str(imageCount), folderName))

newFolderName = str(input("Name of the new folder:\n>>>"))


if not os.path.exists(newFolderName):
    os.makedirs(newFolderName)



indexesToIgnore = []
imagesAdded = 0

n = imageCount - 1
combinationCount = (n * (n + 1)) / 2

xTotal = 0
for i in range(imageCount):
    for j in range(i + 1, imageCount):
        xTotal += 1
        progress = round((xTotal / combinationCount) * 100, 2)
        print("\rProgress: {0}%".format(progress), end=" ")

        willRemove = Compare(imgs[i], imgs[j])

        if willRemove:
            img1 = imgs[i][0]
            img2 = imgs[j][0]

            h1, w1 = imgs[i][1]
            h2, w2 = imgs[j][1]

            if h1 > h2:
                indexesToIgnore.append(j)
            else:
                indexesToIgnore.append(i)



for img in range(len(imgs)):
    if img not in indexesToIgnore:
        imagesAdded += 1

        i = imgs[img]
        Move(i[2])

print("\n{0} images has been transferred to \"{1}\" folder".format(imagesAdded, newFolderName))
