import numpy as np
import matplotlib.colors as mcolors
import os, sys, subprocess, time
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots



def plotData(data, filename):
    # List containing [H, S, V]
    colors_rgb = mcolors.hsv_to_rgb(data) 
    
    # Get HSV Decomposition
    hue = data[:,0]
    sat = data[:,1]
    val = data[:,2]
    
    # Calculate average HSV Values
    hue_avg = sum(hue) / len(hue)
    sat_avg = sum(sat) / len(sat)
    val_avg = sum(val) / len(val)
    
    
    # Set up plot grid
    fig = make_subplots(
        rows=2, cols=3,
        specs=[
            [{"type": "scene", "colspan": 2, "rowspan": 2}, None, {"type": "xy"}], # Row 1
            [None,                                        None,             None]  # Row 2
        ],
        subplot_titles=("3D HSV Space", "Average HSV Values", "Another Plot")
    )

    fig.update_layout(
        title=f"{filename} - HSV Decomposition",
    )

    # Main Scatterplot
    fig.add_trace(go.Scatter3d(
        name="hsv-scatterplot",
        x=hue, # Hue
        y=sat, # Saturation
        z=val, # Value
        hovertemplate="Hue: %{x}<br>Sat: %{y}<br>Val: %{z}",
        mode='markers',
        marker=dict(
            size=3,
            color=colors_rgb, 
            opacity=1,
            symbol="square",
        )),
        row=1, col=1 # These are like coordinates for the trace's placement
    )
    
    fig.update_scenes(
        xaxis=dict(range=[0, 1], title="Hue"),
        yaxis=dict(range=[0, 1], title="Saturation"),
        zaxis=dict(range=[0, 1], title="Value"),
        row=1, col=1
    )
    
    
    # Averages Colors
    hue_clr = f'hsl({hue_avg*360}, 50%, 50%)'
    sat_clr = f'hsl(360, {sat_avg * 100}%, 50%)'
    val_clr = f'hsl(0, 0%, {val_avg * 100}%)'
    
    # Averages subplot
    fig.add_trace(go.Bar(
        name="avg-bar",
        x=['Hue', 'Saturation', 'Value'],
        y=[hue_avg, sat_avg, val_avg],
        marker=dict(
            color=[hue_clr, sat_clr, val_clr], 
            opacity=1,
        )),
        row=1, col=3
    )
    
    fig.update_yaxes(
        range=[0,1],
        row=1, col=3
    )

    
    fig.show()


# Loading a binary .npy file
if sys.argv[1] == "load":
    print("STATUS | Loading file...")
    
    data_path = sys.argv[2]
    filename = os.path.basename(data_path)
    plot_data = np.load(data_path) # Second argument is path
    
    plotData(plot_data, filename)
    print("STATUS | Successfully loaded file.")
    exit()


start_t = time.time()
video_path = sys.argv[1]
filename = os.path.basename(video_path)  # Returns "video_name.mp4"
video_name = os.path.splitext(filename)[0] # Returns "video_name"
capture_ratio = 1 # 1:1 One frame per Second
plot_num = 10000

# ffprobe Command: Stream width and height of video to stdout
dimension_command = [
    'ffprobe', 
    '-v', 'error', 
    '-select_streams', 'v:0', 
    '-show_entries', 'stream=width,height', 
    '-of', 'csv=s=x:p=0', 
    video_path
]
dimension = subprocess.check_output(dimension_command).decode('utf-8').strip()
dimension = dimension.split('x')[:2]
width, height = map(int, dimension)

print("INFO | Detected dimentions: ",width ," x ", height)
bytes_per_frame = width * height * 3


# ffprobe Command: Get duration of video in seconds
duration_command = [
    'ffprobe', 
    '-v', 'error', 
    '-show_entries', 'format=duration', 
    '-of', 'csv=p=0', 
    video_path
]
duration_s = float(subprocess.check_output(duration_command).decode('utf-8').strip())
duration_s = int(duration_s)
# Matplotlib Scatterplots start to overlap at >10000 plots, so we try to aim for this number
if duration_s / plot_num > 1:
    capture_ratio = int(duration_s/plot_num) # 1 frame per (duration/10000) seconds
print(f"INFO | Detected duration: {duration_s} seconds.")
print(f"INFO | Frames to Seconds Ratio: 1/{capture_ratio}" )
num_frames = int(duration_s/capture_ratio)


# ffmpeg Command: Stream raw rgb24 to stdout
main_command = [
    'ffmpeg',
    '-i', video_path,
    '-vf', f'fps=1/{capture_ratio},format=rgb24', 
    '-f', 'rawvideo',
    '-pix_fmt', 'rgb24',
    '-'
]
process = subprocess.Popen(main_command, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
all_hsv_data = []

try:
    print(f"\nSTATUS | Processing {num_frames} frames...")
    while True:
        # Read one frame
        raw_frame = process.stdout.read(bytes_per_frame)
        
        if not raw_frame or len(raw_frame) != bytes_per_frame:
            break  # End of video
        
        # Convert bytes to NumPy RGB array (0-255)
        frame_rgb = np.frombuffer(raw_frame, dtype=np.uint8).reshape((height, width, 3))
        
        # Normalize to 0.0 - 1.0 for the conversion function
        frame_rgb_norm = frame_rgb / 255.0
        
        # Convert RGB to HSV
        # This returns an array where [x, 0] is Hue, [x, 1] is Sat, [x, 2] is Value
        frame_hsv = mcolors.rgb_to_hsv(frame_rgb_norm)
        
        # To keep the data manageable for a plot, we can take the average of the frame
        avg_hsv = np.mean(frame_hsv, axis=(0, 1))
        all_hsv_data.append(avg_hsv)
finally:
    process.terminate()
    print("STATUS | Process completed.\n")
    
# Convert data into np array
data = np.array(all_hsv_data)

# Display time of execution
elapsed_time_s = round(time.time() - start_t)
print(f"INFO | Processed {num_frames} frames in {elapsed_time_s} seconds.\nINFO | Avg Frames Processed per second: {round(num_frames/elapsed_time_s, ndigits=2)}")

# Save binary data
os.makedirs("data", exist_ok=True)
np.save(f"data/{video_name}.npy", data) #use np.load later 
print(f"INFO | Saved binary data as '{video_name}.npy'")

# Prompt Data Visualization
if input("USER | Show scatterplot? (Y/n): ").lower()[0] == "y":
    plotData(data, filename)