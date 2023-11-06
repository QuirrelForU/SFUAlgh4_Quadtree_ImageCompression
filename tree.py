"""
Module with quadtree implementation.
"""
import threading
from PIL import Image, ImageDraw


class Quadrant:
    """
    Represents a quadrant in the QuadTree

    Attributes:
        bbox (tuple): The bounding box of the quadrant
        depth (int): The depth in the quadtree
        children (list): The child quadrants if any
        leaf (bool): True if leaf quadrant, else False
        detail (float): The detail intensity of the quadrant
        color (tuple): The average color in RGB format
    """

    def __init__(self, image: Image.Image, bbox: tuple, depth: int):
        """
        Initialize a Quadrant

        Args:
            image (PIL.Image.Image): The input image
            bbox (tuple): The bounding box of the quadrant
            depth (int): The depth in the quadtree
        """
        self.bbox = bbox
        self.depth = depth
        self.children = None
        self.leaf = False

        image = image.crop(bbox)

        histogram = image.histogram()

        self.detail = get_luma_y(histogram)
        self.color = average_color(image)

    def split(self, image: Image.Image):
        """
        Split the quadrant into four new quadrants.

        Args:
            image (PIL.Image.Image): The input image.
        """
        left, upper, width, height = self.bbox

        middle_x = left + (width - left) / 2
        middle_y = upper + (height - upper) / 2

        # left upper right lower
        upper_left = Quadrant(image, (left, upper, middle_x, middle_y), self.depth + 1)
        upper_right = Quadrant(image, (middle_x, upper, width, middle_y), self.depth + 1)
        bottom_left = Quadrant(image, (left, middle_y, middle_x, height), self.depth + 1)
        bottom_right = Quadrant(image, (middle_x, middle_y, width, height), self.depth + 1)

        self.children = [upper_left, upper_right, bottom_left, bottom_right]


def average_color(image: Image.Image) -> tuple:
    """
    Calculate the average color of an image

    Args:
        image (PIL.Image.Image): The input image

    Returns:
        tuple: A tuple representing the average color in RGB format
    """
    image = image.convert("RGB")

    pixel_data = list(image.getdata())

    total_r, total_g, total_b = 0, 0, 0

    for pixel in pixel_data:
        r, g, b = pixel
        total_r += r
        total_g += g
        total_b += b

    num_pixels = len(pixel_data)
    avg_r = total_r // num_pixels
    avg_g = total_g // num_pixels
    avg_b = total_b // num_pixels

    return avg_r, avg_g, avg_b


def get_luma_y(hist: list) -> float:
    """
    Calculate the Y component for YUV color model

    Args:
        hist (list): Histogram data

    Returns:
        float: Y component
    """
    red_deviation = standard_deviation(hist[:256])
    green_deviation = standard_deviation(hist[256:512])
    blue_deviation = standard_deviation(hist[512:768])
    # 0.299 | 0.587 | 0.114 BT.601 recommended values for Kr Kg Kb
    luma_y = red_deviation * 0.299 + green_deviation * 0.587 + blue_deviation * 0.114

    return luma_y


def standard_deviation(hist: list) -> float:
    """
    Calculate the standard deviation of image histogram

    Args:
        hist (list): Histogram data

    Returns:
        float: Standard deviation value
    """
    total = sum(hist)
    value, deviation_number = 0, 0

    if total > 0:
        value = sum(i * x for i, x in enumerate(hist)) / total
        # Corrected standard deviation formula
        deviation_number = (sum(x * (value - i) ** 2 for i, x in enumerate(hist)) / total) ** 0.5

    return deviation_number


class QuadTree:
    """
       Represents a QuadTree for image compression

       Attributes:
           width (int): The width of the input image
           height (int): The height of the input image
           max_depth (int): The maximum depth of the quadtree
           root (Quadrant): The root quadrant of the quadtree

       Methods:
           start(self, image: Image.Image): Initialize the quadtree and start build process
           build(self, root: Quadrant, image: Image.Image): Recursively build the quadtree
           create_image(self, custom_depth: int, show_lines: bool = False): Create an image based on a given depth
           get_leaves(self, depth: int): Get leaf quadrants up to a specified depth
           search(self, tree, quadrant, max_depth, append_leaf): Recursively search for leaves in quadtree

           create_gif(self, file_name: str, duration: int = 1000, loop: int = 0, show_lines: bool = False):
           Create a GIF representation of the quadtree at different depths

       Args:
           image (PIL.Image.Image): The input image for quadtree

       """

    def __init__(self, image: Image.Image):
        """
        Initialize a QuadTree

        Args:
            image (PIL.Image.Image): The input image
        """
        self.width, self.height = image.size

        self.max_depth = 0

        self.root = None

        self.start(image)

    def start(self, image: Image.Image):
        """
        Start the quadtree compression

        Args:
            image (PIL.Image.Image): The input image
        """
        self.root = Quadrant(image, image.getbbox(), 0)

        self.build(self.root, image)

    def build(self, root: Quadrant, image: Image.Image):
        """
        Recursively build the quadtree

        Args:
            root (Quadrant): The root quadrant
            image (PIL.Image.Image): The input image
        """
        # 10 is experimental number for optimal detail
        # 8 is max depth of quad tree
        if root.depth >= 8 or root.detail <= 10:
            if root.depth > self.max_depth:
                self.max_depth = root.depth

            root.leaf = True
            return
        root.split(image)

        if root.depth == 0:
            threads = []
            for child in root.children:
                thread = threading.Thread(target=self.build, args=(child, image))
                threads.append(thread)
                thread.start()
            for thread in threads:
                thread.join()
        else:
            for children in root.children:
                self.build(children, image)
        # for children in root.children:
        #     self.build(children, image)

    def create_image(self, custom_depth: int, show_lines: bool = False) -> Image.Image:
        """
        Create an image based on quadtree compression

        Args:
            custom_depth (int): The depth of the recursive search
            show_lines (bool): Show lines in the output image

        Returns:
            PIL.Image.Image: The output image
        """
        # create blank image canvas
        image = Image.new('RGB', (self.width, self.height))
        draw = ImageDraw.Draw(image)

        leaf_quadrants = self.get_leaves(custom_depth)

        # draw rectangle size of quadrant for each leaf quadrant
        for quadrant in leaf_quadrants:
            if show_lines:
                draw.rectangle(quadrant.bbox, quadrant.color, outline=(0, 0, 0))
            else:
                draw.rectangle(quadrant.bbox, quadrant.color)

        return image

    def get_leaves(self, depth: int) -> list:
        """
        Get a list of tree leaves

        Args:
            depth (int): The depth in the quadtree

        Returns:
            list: A list of leaves
        """
        if depth > self.max_depth:
            depth = self.max_depth

        quadrants = []

        self.search(self.root, depth, quadrants.append)

        return quadrants

    def search(self, quadrant: Quadrant, max_depth: int, append_leaf):
        """
        Recursively search the quadtree for leaves or max depth quadrants

        Args:
            quadrant: The current quadrant
            max_depth: The maximum depth
            append_leaf: The function to append a leaf quadrant
            to quadrants list in get_leaves
        """
        if quadrant.leaf or quadrant.depth == max_depth:
            append_leaf(quadrant)
        elif quadrant.children is not None:
            for child in quadrant.children:
                self.search(child, max_depth, append_leaf)

    def create_gif(self, file_name: str, duration: int = 1000, loop: int = 0, show_lines: bool = False):
        """
        Create a GIF animation of the quadtree compression

        Args:
            file_name (str): The output GIF file name
            duration (int): The duration of each frame in milliseconds.
            loop (int): Number of loops
            show_lines (bool): Show lines in the output image
        """
        gif = []

        for i in range(self.max_depth):
            image = self.create_image(i, show_lines=show_lines)
            gif.append(image)
        if len(gif) > 0:
            gif.reverse()
            gif[0].save(
                file_name,
                save_all=True,
                append_images=gif[1:],
                duration=duration, loop=loop)
        else:
            print('Cannot create gif, image incompressible')
