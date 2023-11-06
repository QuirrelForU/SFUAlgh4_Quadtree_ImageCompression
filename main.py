"""
Module for implementing image compression using quad trees


"""
import os
import argparse

from PIL import Image
from tree import QuadTree

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Create a quadtree image")
    parser.add_argument("image_path", type=str, help="Path to the input image file")
    parser.add_argument("--depth", type=int, default=1, help="Depth of the recursive search in quadtree")
    parser.add_argument("--show_lines", action="store_true", help="Show lines in the output image")

    args = parser.parse_args()

    image = Image.open(args.image_path)

    filename = os.path.splitext(os.path.basename(args.image_path))[0]

    quadtree = QuadTree(image)

    depth = args.depth

    output_image = quadtree.create_image(depth, show_lines=args.show_lines)

    quadtree.create_gif(f"compressed_{filename}.gif", show_lines=args.show_lines)

    output_image.save(f"compressed_{filename}.jpg")

    print("Completed")
