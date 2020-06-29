# *************************     Welcome to Photo filter project     ******************************

from datetime import datetime
import face_recognition as fr
import concurrent.futures
import time
import os
import glob
import shutil


def create_folder_structure():
    """
    Creates dir structure and returns the sub dir
    """
    base_dir = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop', 'Photo Filter')
    sub_dir = os.path.join(base_dir, 'Photos_' + datetime.now().strftime("%Y_%b_%d_%I_%M_%S"))
    if not os.path.exists(sub_dir):
        os.makedirs(sub_dir)

    return sub_dir


def get_pri_face():
    """
    returns primary face used for comparision
    :return: primary face 
    """
    pri_image_loc = input("Enter primary face location ( complete path )\n")
    while not os.path.exists(pri_image_loc):
        pri_image_loc = input("Invalid file path, retry\n")
    else:
        print("Successfully read the primary face")

    image_numpy = fr.load_image_file(pri_image_loc)
    if len(fr.face_locations(image_numpy)) >= 1:
        return fr.face_encodings(image_numpy)[0]
    return None


def get_sec_images():
    """
    returns all image files in the given folder location is valid
    :return: list of images
    """
    sec_image_loc = input("Enter folder path having image collection to compare face\n")
    while not os.path.exists(sec_image_loc):
        sec_image_loc = input("Invalid file path, retry\n")
    else:
        print("Reading images....\n")

    images = []
    for image in glob.iglob(os.path.join(sec_image_loc, "*.jpg")):
        images.append(image)
    return images


def compare_images(comparision_input):
    unknown_image_numpy = fr.load_image_file(comparision_input[1])
    unknown_encoding = fr.face_encodings(unknown_image_numpy)
    if len(unknown_encoding):
        for face in unknown_encoding:
            if fr.compare_faces([comparision_input[0]], face, 0.5)[0]:
                shutil.copy(comparision_input[1], comparision_input[2])


def main():
    # Read primary image used for comparision and verify that it contains at least 1 face.
    start = time.perf_counter()
    pri_face = get_pri_face()
    if pri_face is None:
        print("Couldn't find face in given image.")
    else:
        # Represents present working directory
        pwd = create_folder_structure()

        comparision_data = []
        for image in get_sec_images():
            comparision_data.append([pri_face, image, pwd])

        with concurrent.futures.ProcessPoolExecutor() as executor:
            executor.map(compare_images, comparision_data)

        end = time.perf_counter()
        print(f"Total Time taken {end - start}Second")


if __name__ == '__main__':
    main()
