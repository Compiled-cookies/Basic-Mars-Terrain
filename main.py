from PIL import Image
import requests
import numpy as np
from tqdm import tqdm


QUALITY = 1

path_prefix = "https://mw1.google.com/mw-planetary/mars/elevation/"  # Google website where all map blocks are located
gray_map = np.zeros((256 * 2**QUALITY, 256 * 2**QUALITY))


# Create a list to convert colors to heights using the legend of the website
lg = Image.open("legend.png")
width, height = lg.size

convert_to_height = []
for i in range(height - 1, -1, -1):
    convert_to_height.append(lg.getpixel((int(width / 2), i)))


def recursively_select_block(path, depth, startx, starty):
    if depth == QUALITY:
        print(path)
        image = Image.open(requests.get(f"{path_prefix}{path}.jpg", stream=True).raw)
        width, height = image.size

        for x in tqdm(range(256)):
            for y in range(256):
                curr = image.getpixel((x, y))
                
                minn, best_index = 1e9 + 7, 0
                
                for i, color_tuple in enumerate(convert_to_height):
                    dist = (color_tuple[0] - curr[0])**2 + (color_tuple[1] - curr[1])**2 + (color_tuple[2] - curr[2])**2
                    if dist < minn: 
                        minn = dist
                        best_index = i

                gray_map[starty + y, startx + x] = best_index / height * 255

        PIL_image = Image.fromarray(np.uint8(gray_map)).convert('RGB')
        PIL_image.save(f"renders/gray_map_quality_{QUALITY}.png")

    else:
        recursively_select_block(path + 'q', depth + 1, startx, starty)  # Top left corner
        recursively_select_block(path + 'r', depth + 1, startx + 256 * (2**(QUALITY - depth - 1)), starty)  # Top right corner
        recursively_select_block(path + 't', depth + 1, startx, starty + 256 * (2**(QUALITY - depth - 1)))  # Bottom left corner
        recursively_select_block(path + 's', depth + 1, startx + 256 * (2**(QUALITY - depth - 1)), starty + 256 * (2**(QUALITY - depth - 1)))  # Bottom right corner

if __name__ == "__main__":
    recursively_select_block(path="t", depth=0, startx=0, starty=0)

