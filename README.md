# ChromaFrame-VideoToHSVPlot
Visualization tool used to decompose individual video frames and map their average HSV values on a scatter plot.

# Pre-requisites
- Python 3.7+
  - numpy 1.20+
  - matplotlib 3.4+
  - pandas 1.3+
  - plotly 5.0+
  
- FFmpeg


<br>

# Usage
ChromaFrame allows you to **generate** and **load** .npy files containing averaged HSV data for a given video's frames

## Generating a new plot

```bash
> python .\3d_plot.py <video_path>
```
Note: Make sure the script has write access, else the plot data will not be saved.

## Loading an old plot

```bash
> python .\3d_plot.py load <data_path>
```
<br>

# Acknowledgements

This project's methodology was heavily inspired and based off of [Ahoy](https://www.youtube.com/@XboxAhoy)'s youtube video:

[When Video Games were Brown.](https://www.youtube.com/watch?v=TTjGDkDI49I&t=497s)