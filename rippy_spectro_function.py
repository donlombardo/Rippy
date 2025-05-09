from rippy_help_functions import *
from PIL import Image
import os
import math

def spectro_function(rippy_class):
    spaced_print("Creating spectrograms.\n\n")

    list_images = []

    # Convert PNGs to JPGs
    for i in sorted(os.listdir()):
        if i.endswith(".png"):
            image = Image.open(i).convert("RGB")
            new_filename = i.replace(".png", ".jpg")
            image.save(new_filename)
            list_images.append(new_filename)
            os.remove(i)

    remove_images = list(list_images)
    vertical = []

    # Process images in groups of 4
    num_rows = math.ceil(len(list_images) / 4)
    for row_num in range(1, num_rows + 1):
        current = []
        img_count = 0

        for i in range(4):
            img_count += 1
            if list_images:
                current.append(list_images.pop(0))
            else:
                black_img_name = f"black_{img_count}.jpg"
                black_img = Image.new('RGB', (944, 613))
                black_img.save(black_img_name)
                current.append(black_img_name)
                remove_images.append(black_img_name)

        # Concatenate images horizontally
        images = [Image.open(x) for x in current]
        widths, heights = zip(*(img.size for img in images))
        total_width = sum(widths)
        max_height = max(heights)
        
        new_img = Image.new('RGB', (total_width, max_height))
        x_offset = 0
        for img in images:
            new_img.paste(img, (x_offset, 0))
            x_offset += img.width
        
        line_image = f"line{row_num}.jpg"
        new_img.save(line_image)
        vertical.append(line_image)
        remove_images.append(line_image)

    # Combine all horizontal strips into a single vertical image
    imgs = [Image.open(i) for i in vertical]
    widths, heights = zip(*(img.size for img in imgs))
    max_width = max(widths)
    total_height = sum(heights)
    
    final_image = Image.new('RGB', (max_width, total_height))
    y_offset = 0
    for img in imgs:
        final_image.paste(img, (0, y_offset))
        y_offset += img.height
    
    final_filename = f"{rippy_class.FOLDER_STR} spectrograms.jpg"
    final_image.save(final_filename)

    # Cleanup temporary images
    for image in remove_images:
        os.remove(image)

