# QuadTree Image Compression

A command-line interface (CLI) module for image compression using quad-trees.\
Max quad-trees depth = 8.\
Lower depth means stronger compression.

## Features

- Image compression using the QuadTree data structure.
- Customizable depth for recursive search in the QuadTree.
- Option to show or hide lines in the output image.
- Creation of GIF animations to visualize the compression process at different depths.

## Examples of Usage:

### Example 1:



```
python main.py data\pupsik.jpg --depth 4  --show_lines
```


![pupsik_](/data/pupsik.jpg)
![pupsik_compress](/data_output/compressed_pupsik.jpg)
![pupsik_gif](/data_output/compressed_pupsik.gif)


### Example 2:


```
python main.py data\jaba.jpg --depth 3333  --show_lines  
```
![jaba_](/data/jaba.jpg)
![jaba_compress](/data_output/compressed_jaba.jpg)
![jaba_gif](/data_output/compressed_jaba.gif)



### Example 3:


```
python main.py data\catdespair.jpg  --depth 2   
```

![despair_](/data/catdespair.jpg)
![despair_compress](/data_output/compressed_catdespair.jpg)
![despair_gif](/data_output/compressed_catdespair.gif)
