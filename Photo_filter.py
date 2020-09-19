# *************************     Welcome to Photo filter project     ******************************

from datetime import datetime
from tkinter import *
from tkinter import ttk, filedialog, messagebox
from PIL import ImageTk, Image
import face_recognition as fr
import concurrent.futures
import os
import glob
import shutil
import subprocess


def on_image_browse(master):
    """
    Reads primary image for comparision and display it
    :param master: master widget
    :return: None
    """
    filename = filedialog.askopenfilename(initialdir="/", title="Select a Image", filetypes=(("jpeg files", "*.jpg"),))
    if filename:
        master.pri_image = ImageTk.PhotoImage(Image.open(filename).resize((150, 150), Image.ANTIALIAS))
        master.pri_image_label.config(image=master.pri_image)
        master.pri_image_face = get_face(filename)
        if master.pri_image_face is None:
            master.choose_button.state(['disabled'])
            master.label_image_error.config(text="Couldn't find face in an image, Retry")
        else:
            master.choose_button.state(['!disabled'])
            master.label_image_error.config(text=" ")


def on_choose(master):
    """
    Reads image collection and display in canvas
    :param master: master widget
    :return: None
    """
    filename = filedialog.askdirectory(initialdir="/", title="Select a folder", mustexist=True)

    # Resize all images to show in canvas
    master.secondary_images = []
    for image in get_sec_images_for_canvas(filename):
        master.secondary_images.append(ImageTk.PhotoImage(Image.open(image).resize((90, 90), Image.ANTIALIAS)))

    if len(master.secondary_images) > 0:
        master.secondary_image_loc = filename
        master.geometry('640x600+450+100')
        master.sec_image_v_scroll.pack(side=RIGHT, fill=Y)
        master.sec_image_canvas.config(yscrollcommand=master.sec_image_v_scroll.set)
        master.sec_image_canvas.pack(side=LEFT, expand=True, fill=BOTH)

        ttk.Label(master.home_frame, text="Note: Displayed top 25 images here", font=master.small_font) \
            .place(x=70, y=280, width=500, height=30)

        # Display images in canvas
        count = 0
        master.sec_image_canvas.config(scrollregion=(0, 0, 500, (len(master.secondary_images) * 20) + 100))
        for col in range(0, 500, 100):
            for row in range(0, 500, 100):
                if count < len(master.secondary_images):
                    master.sec_image_canvas.create_image(row, col, anchor=NW, image=master.secondary_images[count])
                    count += 1
        del count

        master.sec_image_frame.place(x=70, y=310, width=520, height=200)
        master.filter_button.place(x=490, y=530, width=100, height=30)
        master.filter_button.state(['!disabled'])
    else:
        ttk.Label(master.home_frame, text="Folder doesn't contain any image", font=master.small_font, foreground='red')\
            .place(x=70, y=280, width=500, height=30)
        master.sec_image_frame.place_forget()
        master.geometry('650x350+450+100')


def on_filter(master):
    """
    Filters the images using face recognition algorithm
    :param master: master widget
    :return: none
    """
    # Getting images for Core image comparision
    pwd = create_folder_structure()
    comparision_data = []
    for image in get_sec_images(master.secondary_image_loc):
        comparision_data.append([master.pri_image_face, image, pwd])

    # Core image comparision
    with concurrent.futures.ProcessPoolExecutor() as executor:
        executor.map(compare_images, comparision_data)

    messagebox.showinfo(title="Information", message="Successfully filtered images")
    subprocess.Popen('explorer "{0}"'.format(pwd))


def create_folder_structure():
    """
    Creates dir structure and returns the sub dir
    """
    base_dir = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop', 'Photo Filter')
    sub_dir = os.path.join(base_dir, 'Photos_' + datetime.now().strftime("%Y_%b_%d_%I_%M_%S"))
    if not os.path.exists(sub_dir):
        os.makedirs(sub_dir)
    return sub_dir


def get_face(pri_image):
    """
    returns primary face used for comparision
    :return: primary face
    """
    print(pri_image)
    image_numpy = fr.load_image_file(pri_image)
    if len(fr.face_locations(image_numpy)) >= 1:
        return fr.face_encodings(image_numpy)[0]
    return None


def get_sec_images_for_canvas(sec_image_loc):
    """
    returns all image files in the given folder location is valid
    :return: list of 25 images
    """
    return [image.replace('\\', '/') for image, _ in zip(glob.iglob(os.path.join(sec_image_loc, "*.jpg")), range(0, 25))]


def get_sec_images(sec_image_loc):
    """
    returns all image files in the given folder location is valid
    :return: list of images
    """
    return [image.replace('\\', '/') for image in glob.iglob(os.path.join(sec_image_loc, "*.jpg"))]


def compare_images(comparision_input):
    unknown_image_numpy = fr.load_image_file(comparision_input[1])
    unknown_encoding = fr.face_encodings(unknown_image_numpy)
    if len(unknown_encoding):
        for face in unknown_encoding:
            if fr.compare_faces([comparision_input[0]], face, 0.5)[0]:
                shutil.copy(comparision_input[1], comparision_input[2])


def run_photo_filter():
    # Create master window and configure
    master = Tk()
    master.title("Photo Filter")
    master.geometry('640x350+450+100')
    master.resizable(False, False)
    master.big_font = ("Helvetica", 18, "bold")
    master.small_font = ("Helvetica", 10, "bold")

    # Create notebooks and configure
    notebook = ttk.Notebook(master)
    notebook.grid()
    notebook.config(width=640, height=600)

    about_frame = ttk.Frame(notebook)
    help_frame = ttk.Frame(notebook)
    home_frame = ttk.Frame(notebook)
    home_frame.grid()
    home_frame.config(relief=RIDGE)
    master.home_frame = home_frame

    notebook.add(home_frame, text='Home')
    notebook.add(about_frame, text='About')
    notebook.add(help_frame, text='Help')

    ttk.Label(home_frame, text="Whom you want to filter", font=master.big_font).place(x=70, y=80, width=400, height=50)

    # Display primary image
    master.pri_image = ImageTk.PhotoImage(Image.open("dummy_face.jpg").resize((150, 150), Image.ANTIALIAS))
    pri_image_label = ttk.Label(home_frame, image=master.pri_image, relief="groove")
    pri_image_label.place(x=410, y=30, width=150, height=150)
    pri_image_label.bind('<ButtonPress>', lambda e: on_image_browse(master))
    master.pri_image_label = pri_image_label

    # Display if error on primary image
    label_image_error = ttk.Label(master.home_frame, text=" ", font=master.small_font, foreground='red')
    label_image_error.place(x=70, y=120, width=250, height=50)
    master.label_image_error = label_image_error

    ttk.Label(home_frame, text="Where we should look into", font=master.big_font).place(x=190, y=210, width=400, height=50)

    choose_button = ttk.Button(home_frame, text="Choose", command=lambda: on_choose(master), state=['disabled'])
    choose_button.place(x=70, y=220, width=100, height=30)
    master.choose_button = choose_button

    # Create widgets to display secondary image
    sec_image_frame = Frame(master.home_frame)
    sec_image_canvas = Canvas(sec_image_frame, bg='#FFFFFF')
    sec_image_v_scroll = Scrollbar(sec_image_frame, orient=VERTICAL, command=sec_image_canvas.yview)
    master.sec_image_frame = sec_image_frame
    master.sec_image_canvas = sec_image_canvas
    master.sec_image_v_scroll = sec_image_v_scroll

    filter_button = ttk.Button(home_frame, text="Filter", command=lambda: on_filter(master), state=['disabled'])
    master.filter_button = filter_button

    master.mainloop()


if __name__ == '__main__':
    run_photo_filter()
