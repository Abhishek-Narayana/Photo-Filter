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
    Creates and returns the base dir if not exists
    """
    base_dir = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop', 'Photo Filter')
    if not os.path.exists(base_dir):
        os.mkdir(base_dir)

    """
    Creates instance dir for the current task
    """
    cur_dir_name = os.path.join(base_dir, 'Photos_' + datetime.now().strftime("%Y_%b_%d_%I_%M_%S"))
    if not os.path.exists(cur_dir_name):
        os.mkdir(cur_dir_name)

    return cur_dir_name


def get_encoded_face(input_image):
    """
    Encodes the given image
    :param input_image: Image containing face
    :return: face encoding
    """
    numpy_image = fr.load_image_file(input_image)
    return fr.face_encodings(numpy_image)[0]


def get_face(image):
    image_numpy = fr.load_image_file(image)
    if len(fr.face_locations(image_numpy)) >= 1:
        return fr.face_encodings(image_numpy)[0]
    return None


def get_images(image_source_dir):
    # returns all image files
    images = []
    for image in glob.iglob(os.path.join(image_source_dir, "*.jpg")):
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
    pri_image = r'C:\Users\z003u7sd\Desktop\Images\megha.jpeg'

    # replace with read primary face function
    pri_face = get_face(pri_image)
    if pri_face is None:
        print("Invalid primary image")
    else:
        print("Successfully read the primary face")
        # Represents present working directory
        pwd = create_folder_structure()

        # replace with reading collection of pics
        image_source_dir = r'C:\Users\z003u7sd\Desktop\Images\dummy'

        comparision_data = []
        for image in get_images(image_source_dir):
            comparision_data.append([pri_face, image, pwd])

        with concurrent.futures.ProcessPoolExecutor() as executor:
            executor.map(compare_images, comparision_data)
            
        end = time.perf_counter()
        print(f"Total Time taken {end - start}Second")


if __name__ == '__main__':
    main()
