import os
import numpy as np
import cv2 as cv
from shutil import copyfile

# changable
CompareSize = (64, 64)
Threshold = 5

# unchangable
BlurKernelSize = (3, 3)


def readImageFromPath(fPath):
    stream = open(fPath, "rb")
    byt = bytearray(stream.read())
    stream.close()

    numpyarray = np.asarray(byt, dtype=np.uint8)
    return cv.imdecode(numpyarray, cv.IMREAD_GRAYSCALE)


def LoadImagesFromFolder(folder):
    images = []  # scaled image, shape, file name
    loadedImageCount = 0

    folderList = os.listdir(folder)
    folderItemCount = len(folderList) - 1

    if folderItemCount == 0:
        return

    print("\nScanning for images in folder \"{0}\"".format(folder))

    for index in range(len(folderList)):
        fileName = folderList[index]
        directory = os.path.join(folder, fileName)

        if (os.path.isdir(directory)):
            continue

        img = readImageFromPath(directory)

        if img is not None:
            loadedImageCount += 1
            images.append((cv.GaussianBlur(cv.resize(img, CompareSize), BlurKernelSize, 0), img.shape, fileName))

        progress = round((index / folderItemCount) * 100, 2)
        print("\rScanning: {0}% | Found {1} images.".format(progress, loadedImageCount), end=" ")

    print()
    return images


def SameImages(i1, i2):
    img1 = i1[0]
    img2 = i2[0]

    differenceIMG = cv.absdiff(img2, img1)

    avg = np.average(differenceIMG)

    return avg < Threshold


def FindIndexesToRemove(imageList):
    imageCount = len(imageList)

    indexesToBeRemoved = []
    totalComparisonCount = (imageCount * (imageCount - 1)) / 2

    print("\nSearching for the same images.")
    currentComparisonCount = 0
    removedImageCount = 0
    for img1Index in range(imageCount):
        for img2Index in range(img1Index + 1, imageCount):
            currentComparisonCount += 1

            if SameImages(imageList[img1Index], imageList[img2Index]):

                h1, w1 = imageList[img1Index][1]
                h2, w2 = imageList[img2Index][1]

                if h1 > h2:
                    if img2Index not in indexesToBeRemoved:
                        removedImageCount += 1

                    indexesToBeRemoved.append(img2Index)
                else:
                    if img1Index not in indexesToBeRemoved:
                        removedImageCount += 1

                    indexesToBeRemoved.append(img1Index)

            progress = round((currentComparisonCount / totalComparisonCount) * 100, 2)
            print("\rProgress: {0}% | Found {1} same images.".format(progress, removedImageCount), end=" ")

    print("\n")
    return indexesToBeRemoved

print("The pictures will be resized to {0}.".format(CompareSize))
NewSize = input("Input a number if you want to change the resolution. (Min: 16 / Max: 256)\n>>>")
if (NewSize.isdigit()):
    NewRes = int(NewSize)
    if NewRes <= 256 and NewRes >= 16:
        CompareSize = (NewRes, NewRes)

print("\nThe max threshold between images is {0}.".format(Threshold))
NewThreshold = input("Input a number if you want to change the resolution. (Min: 0 / Max: 25)\n>>>")
if (NewSize.isdigit()):
    NewThr = int(NewThreshold)
    if NewThr <= 25 and NewThr > 0:
        Threshold = NewThr

OriginalFolderName = str(input("\nName / Path of the folder to import pictures from:\n>>>"))
SubFolderPaths = [x[0] for x in os.walk(OriginalFolderName)]

Images = []
FolderImages = []

NextIndex = 0  # Ending index of the directory (n < NextIndex)
for subFolder in SubFolderPaths:
    imagesInFolder = LoadImagesFromFolder(subFolder)

    imageCount = len(imagesInFolder)
    if imageCount == 0:
        continue

    NextIndex += imageCount
    FolderImages.append((subFolder, NextIndex))

    Images.extend(imagesInFolder)


ImageCount = len(Images)
print("\n{0} images found in the folder \"{1}\" and its sub-folders.".format(str(ImageCount), OriginalFolderName))

RemovedIndexes = FindIndexesToRemove(Images)

NewFolderName = str(input("Name of the new folder images will be transferred to:\n>>>"))
print("\nImages are being transferred with the original file structure.")

ImagesAdded = 0
FirstFolderIndex = 0
for folderImageIndex in range(0, len(FolderImages)):
    folderImage = FolderImages[folderImageIndex]

    if folderImageIndex == 0:
        newDirectory = NewFolderName
    else:
        newDirectory = os.path.join(NewFolderName, os.path.normpath(folderImage[0]).split("\\", 1)[1])

    if not os.path.exists(newDirectory):
        os.makedirs(newDirectory)

    lastFolderIndex = folderImage[1]
    for imageIndex in range(FirstFolderIndex, lastFolderIndex):
        FirstFolderIndex = folderImage[1]

        if imageIndex not in RemovedIndexes:
            ImagesAdded += 1

            image = Images[imageIndex]

            oldPath = os.path.join(folderImage[0], image[2])
            newPath = os.path.join(newDirectory, image[2])

            copyfile(oldPath, newPath)


print("\n{0} images has been transferred to the folder \"{1}\".".format(ImagesAdded, NewFolderName))
