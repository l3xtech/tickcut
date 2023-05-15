import cv2
import os
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk

# Create a Tkinter root and hide it.
root = tk.Tk()
root.withdraw()

# Prompts the user for the cutting dimensions.
width, height = map(int, input("Enter the dimensions of the slice ('width x height' format): ").split('x'))

# Prompt the user for the image directory
directory = filedialog.askdirectory(title='Select photos directory')

# Create a list of all images in the directory
images = [os.path.join(directory, filename) for filename in os.listdir(directory) if filename.endswith(".jpg") or filename.endswith(".png")]

def process_next_image():
    if images:
	# Fetch the next image in the queue
        img_path = images.pop(0)

	# Read the image with OpenCV
        img = cv2.imread(img_path)

        # Create a new Tkinter window
        window = tk.Toplevel()

        # Open the image with the PIL
        image = Image.open(img_path)

        # Calculate display dimensions
        display_width = 800
        display_height = int(image.height / (image.width / display_width))

        # Resize the image to display dimensions
        image = image.resize((display_width, display_height), Image.ANTIALIAS)

        # Calculates the dimensions of the rectangle based on the aspect ratio of the displayed image
        rect_width = width * (display_width / img.shape[1])
        rect_height = height * (display_height / img.shape[0])

        # Convert the PIL image to a Tkinter image
        tk_img = ImageTk.PhotoImage(image)

        # Create a Tkinter canvas and add the image to it
        canvas = tk.Canvas(window, width=display_width, height=display_height)
        canvas.pack()
        canvas.create_image(0, 0, anchor='nw', image=tk_img)

        def on_mouse_move(event):
            # Update the preview rectangle whenever the mouse moves
            canvas.delete('all')
            canvas.create_image(0, 0, anchor='nw', image=tk_img)
            x_start = max(0, event.x - rect_width / 2)
            y_start = max(0, event.y - rect_height / 2)
            x_end = min(display_width, event.x + rect_width / 2)
            y_end = min(display_height, event.y + rect_height / 2)
            canvas.create_rectangle(x_start, y_start, x_end, y_end, outline='red')

        # Bind the mouse movement event to the function
        canvas.bind("<Motion>", on_mouse_move)

        def on_mouse_click(event):
            # Adjust the click coordinates to match the original image
            x_ratio = img.shape[1] / display_width
            y_ratio = img.shape[0] / display_height
            x = int(event.x * x_ratio)
            y = int(event.y * y_ratio)

            # Calculate the coordinates of the cut
            x_start = max(0, x - width // 2)
            y_start = max(0, y - height // 2)
            x_end = min(img.shape[1], x + width // 2)
            y_end = min(img.shape[0], y + height // 2)

            # Cut the image
            cropped = img[y_start:y_end, x_start:x_end]

            # Save the cropped image to the same path as the original, replacing it
            cv2.imwrite(img_path, cropped)

            # Close the window
            window.destroy()

            # Process the next image in the queue
            process_next_image()

        # Bind the mouse click event to the function
        canvas.bind("<Button-1>", on_mouse_click)

        # Store the Tkinter image in the window to prevent it from being destroyed prematurely by the garbage collector
        window.tk_img = tk_img
    else:
        root.quit()

# Process the first image
process_next_image()

# Start the main Tkinter loop
root.mainloop()
