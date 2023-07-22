
from PIL import Image, ImageTk


def resize_icon_image(image_path, width, height):
    # Open the image using PIL
    image = Image.open(image_path)
    # Resize the image to fit the button size
    resized_image = image.resize((width, height), Image.LANCZOS)
    # Create a PhotoImage object from the resized image
    return ImageTk.PhotoImage(resized_image)