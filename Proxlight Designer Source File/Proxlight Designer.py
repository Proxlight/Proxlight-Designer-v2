''' Proxlight Designer - Created By Pratyush Mishra (Proxlight)'''


import sys
from tkinter import *
from tkinter import filedialog, messagebox
from turtle import color


############################################################################

import requests
import os


def generate_code(token, link, output_path):

    def get_color(element):
        # Returns HEX form of element RGB color (str)
        el_r = element["fills"][0]["color"]['r'] * 255
        el_g = element["fills"][0]["color"]['g'] * 255
        el_b = element["fills"][0]["color"]['b'] * 255

        hex_code = ('#%02x%02x%02x' % (round(el_r), round(el_g), round(el_b)))

        return hex_code

    def get_coordinates(element):
        # Returns element coordinates as x (int) and y (int)
        x = int(element["absoluteBoundingBox"]["x"])
        y = int(element["absoluteBoundingBox"]["y"])

        return x, y

    def get_dimensions(element):
        # Return element dimensions as width (int) and height (int)
        height = int(element["absoluteBoundingBox"]["height"])
        width = int(element["absoluteBoundingBox"]["width"])

        return width, height

    def get_text_properties(element):
        # Return element font and fontSize (str)
        font = element["style"]["fontPostScriptName"]
        fontSize = element["style"]["fontSize"]

        return font, fontSize

    global fig_window, response

    generated_dir = output_path + "/Proxlight_Designer_Export/"

    lines = []
    lines.extend(['from tkinter import *\n\n',
                  'def btn_clicked():',
                  '    print("Button Clicked")\n\n\n'
                  'window = Tk()'])

    # Getting File Data

    def find_between(s, first, last):
        try:
            start = s.index(first) + len(first)
            end = s.index(last, start)

            return s[start:end]

        except ValueError:
            return ""

    token = token.strip()
    file_url = link.strip()

    file_id = find_between(file_url, "file/", "/")

    try:
        response = requests.get(
            f"https://api.figma.com/v1/files/{file_id}",
            headers={"X-FIGMA-TOKEN": token})

    except ValueError:
        messagebox.showerror(
            "Value Error",
            "Invalid Input. Please check your input and try again.")

    except requests.ConnectionError:
        messagebox.showerror(
            "No Connection",
            "Proxlight Designer requires internet access to work.")

    data = response.json()

    # Getting Window Properties

    try:
        fig_window = data["document"]["children"][0]["children"][0]

        try:
            os.mkdir(generated_dir)

        except FileExistsError:
            messagebox.showinfo("File Exists",
                                "Existing Files will be overwritten.")

        except PermissionError:
            messagebox.showerror("Permission Error",
                                 "Change directory or directory permissions.")

    except KeyError:
        messagebox.showerror(
            "Error",
            "Invalid Input. Please check your input and try again.")

    except IndexError:
        messagebox.showerror(
            "Error",
            "Invalid design file. Does your file contain a Frame?")

    window_width, window_height = get_dimensions(fig_window)

    try:
        window_bg_hex = get_color(fig_window)

    except Exception as e:
        print(e)
        window_bg_hex = "#FFFFFF"

    # Creating Window

    lines.extend([f'\nwindow.geometry("{window_width}x{window_height}")',
                  f'window.configure(bg = "{window_bg_hex}")',
                  'canvas = Canvas(',
                  '    window,',
                  f'    bg = "{window_bg_hex}",',
                  f'    height = {window_height},',
                  f'    width = {window_width},',
                  '    bd = 0,',
                  '    highlightthickness = 0,',
                  '    relief = "ridge")',
                  'canvas.place(x = 0, y = 0)\n'])

    # Getting Elements inside Window

    window_elements = fig_window["children"]

    btn_count = 0
    text_entry_count = 0

    for element in window_elements:

        if element["name"] == "Rectangle" or element["name"] == "rectangle":
            width, height = get_dimensions(element)
            x, y = get_coordinates(element)
            element_color = get_color(element)

            lines.extend(['\ncanvas.create_rectangle(',
                          f'    {x}, {y}, {x}+{width}, {y}+{height},',
                          f'    fill = "{element_color}",',
                          '    outline = "")\n'])

        elif element["name"] == "Button" or element["name"] == "button":
            width, height = get_dimensions(element)
            x, y = get_coordinates(element)
            item_id = element["id"]

            response = requests.get(
                f"https://api.figma.com/v1/images/{file_id}?ids={item_id}",
                headers={"X-FIGMA-TOKEN": f"{token}"})

            image_link = requests.get(response.json()["images"][item_id])

            with open(f"{generated_dir}img{btn_count}.png", "wb") as file:
                file.write(image_link.content)

            lines.extend([
                f'img{btn_count} = PhotoImage(file = f"img{btn_count}.png")',
                f'b{btn_count} = Button(',
                f'    image = img{btn_count},',
                '    borderwidth = 0,',
                '    highlightthickness = 0,',
                '    command = btn_clicked,',
                '    relief = "flat")\n',
                f'b{btn_count}.place(',
                f'    x = {x}, y = {y},',
                f'    width = {width},',
                f'    height = {height})\n'])

            btn_count += 1

        elif element["type"] == "TEXT":
            text = element["characters"]
            x, y = get_coordinates(element)
            width, height = get_dimensions(element)
            color = get_color(element)
            font, fontSize = get_text_properties(element)

            x, y = x + (width / 2), y + (height / 2)

            text = text.replace("\n", "\\n")

            lines.extend([f'canvas.create_text(',
                          f'    {x}, {y},',
                          f'    text = "{text}",',
                          f'    fill = "{color}",',
                          f'    font = ("{font}", int({fontSize})))\n'])

        elif element["name"] in ("TextBox", "TextArea"):
            element_types = {
                "TextArea": "Text",
                "TextBox": "Entry"
            }

            width, height = get_dimensions(element)
            x, y = get_coordinates(element)
            x, y = x + (width / 2), y + (height / 2)
            bg = get_color(element)

            item_id = element["id"]

            response = requests.get(
                f"https://api.figma.com/v1/images/{file_id}?ids={item_id}",
                headers={"X-FIGMA-TOKEN": f"{token}"})

            image_link = requests.get(response.json()["images"][item_id])

            with open(
                    f"{generated_dir}img_textBox{text_entry_count}.png",
                    "wb"
            ) as file:
                file.write(image_link.content)

            lines.extend([f'entry{text_entry_count}_img = PhotoImage('
                          f'file = f"img_textBox{text_entry_count}.png")',
                          f'entry{text_entry_count}_bg = '
                          'canvas.create_image(',
                          f'    {x}, {y},',
                          f'    image = entry{text_entry_count}_img)\n'])

            try:
                corner_radius = element["cornerRadius"]

            except KeyError:
                corner_radius = 0

            if corner_radius > height / 2:
                corner_radius = height / 2

            reduced_width = width - (corner_radius * 2)
            reduced_height = height - 2

            x, y = get_coordinates(element)
            x = x + corner_radius

            lines.extend([f'entry{text_entry_count} = '
                          f'{element_types[element["name"]]}(',
                          '    bd = 0,',
                          f'    bg = "{bg}",',
                          '    highlightthickness = 0)\n',
                          f'entry{text_entry_count}.place(',
                          f'    x = {x}, y = {y},',
                          f'    width = {reduced_width},',
                          f'    height = {reduced_height})\n'])

            text_entry_count += 1

        elif element["name"] == "Background" or element["name"] == "background" or element["name"] == "BG" or element["name"] == "bg":
            width, height = get_dimensions(element)
            x, y = get_coordinates(element)
            x, y = x + (width / 2), y + (height / 2)
            item_id = element["id"]

            response = requests.get(
                f"https://api.figma.com/v1/images/{file_id}"
                f"?ids={item_id}&use_absolute_bounds=true",
                headers={"X-FIGMA-TOKEN": f"{token}"})

            image_link = requests.get(response.json()["images"][item_id])

            with open(f"{generated_dir}background.png", "wb") as file:
                file.write(image_link.content)

            lines.extend(['background_img = PhotoImage('
                          'file = f"background.png")',
                          'background = canvas.create_image(',
                          f'    {x}, {y},',
                          f'    image=background_img)\n'])

    # Adding Generated Code to window.py

    lines.extend(['window.resizable(False, False)', 'window.mainloop()'])
    final_code = [line + "\n" for line in lines]

    with open(f"{generated_dir}window.py", 'w') as py_file:
        py_file.writelines(final_code)

    messagebox.showinfo("Success", "Design Exported successfully!")


############################################################################
# Required in order to add data files to Windows executable
path = getattr(sys, '_MEIPASS', os.getcwd())
os.chdir(path)

initialTheme = "light"
theme = "light"


def theme_change():
    global theme, initialTheme
    if theme == initialTheme:
        theme = "dark"
        b1.config(image=moon,bg=dark_theme_color,activebackground=dark_theme_color)
        b0.config(image=create_button_dark,bg=dark_theme_color, activebackground=dark_theme_color)
        background = canvas.create_image(
            474.5, 286.0,
            image=background_img_dark)

    else:
        theme = "light"
        b1.config(image=sun,bg=light_theme_color,activebackground=light_theme_color)
        b0.config(image=create_button_light, bg=light_theme_color,
                  activebackground=light_theme_color)
        background = canvas.create_image(
            474.5, 286.0,
            image=background_img_light)


def btn_clicked():
    token = token_entry.get()
    URL = URL_entry.get()

    if not token:
        messagebox.showerror(title="Empty Fields",
                             message="Please enter Token")

    elif not URL:
        messagebox.showerror(title="Empty Fields",
                             message="Please enter URL")

    elif not output_path:
        messagebox.showerror(title="invalid path",
                             message="Enter a valid output path")

    else:
        generate_code(token, URL, output_path)


def select_path(event):
    global output_path

    # window.withdraw()
    output_path = filedialog.askdirectory()
    path_entry.delete(0, END)
    path_entry.insert(0, output_path)
    # window.deiconify()


def make_label(master, x, y, h, w, *args, **kwargs):
    f = Frame(master, height=h, width=w)
    f.pack_propagate(0)  # don't shrink
    f.place(x=x, y=y)

    label = Label(f, *args, **kwargs)
    label.pack(fill=BOTH, expand=1)

    return label


##################################################################

window = Tk()
window.title("Proxlight Designer")
window.iconbitmap("logo.ico")
window.geometry("975x585")
window.configure(bg="#FFFFFF")
canvas = Canvas(
    window,
    bg="#FFFFFF",
    height=600,
    width=1000,
    bd=0,
    highlightthickness=0,
    relief="ridge")
canvas.place(x=0, y=0)


background_img_light = PhotoImage(file=f"background_light.png")
background_img_dark = PhotoImage(file=f"background_dark.png")
token_entry_img = PhotoImage(file=f"img_textBox0.png")
URL_entry_img = PhotoImage(file=f"img_textBox1.png")
path_entry_img = PhotoImage(file=f"img_textBox2.png")
create_button_light = PhotoImage(file=f"create_button_light.png")
create_button_dark = PhotoImage(file=f"create_button_dark.png")
sun = PhotoImage(file=f"sun.png")
moon = PhotoImage(file=f"moon.png")
light_theme_color = "#167A80"
dark_theme_color = "#343636"

background = canvas.create_image(
    474.5, 286.0,
    image=background_img_light)


token_entry_bg = canvas.create_image(
    703.5, 187.5,
    image=token_entry_img)

token_entry = Entry(
    bd=0,
    bg="#ffffff",
    highlightthickness=0)

token_entry.place(
    x=592, y=174,
    width=210.0,
    height=30)


URL_entry_bg = canvas.create_image(
    703.5, 290.5,
    image=URL_entry_img)

URL_entry = Entry(
    bd=0,
    bg="#ffffff",
    highlightthickness=0)

URL_entry.place(
    x=592, y=277,
    width=210.0,
    height=30)


path_entry_bg = canvas.create_image(
    703.5, 393.5,
    image=path_entry_img)

path_entry = Entry(
    bd=0,
    bg="#ffffff",
    highlightthickness=0)

path_entry.place(
    x=592, y=380,
    width=210.0,
    height=30)

path_entry.bind("<1>", select_path)


b0 = Button(bg=light_theme_color,
            activebackground=light_theme_color,
            image=create_button_light,
            borderwidth=0,
            highlightthickness=0,
            command=btn_clicked,
            relief="flat")

b0.place(
    x=650, y=440,
    width=104,
    height=35)


b1 = Button(bg=light_theme_color,
            activebackground=light_theme_color,
            image=sun,
            borderwidth=0,
            highlightthickness=0,
            command=theme_change,
            relief="flat")

b1.place(
    x=760, y=440,
    width=35,
    height=35)


window.resizable(False, False)
window.mainloop()
