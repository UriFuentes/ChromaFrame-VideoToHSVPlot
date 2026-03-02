import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import os, sys, subprocess, time


# Loading a binary .npy file
if sys.argv[1] == "load":
    
    data_path = sys.argv[2]
    filename = os.path.basename(data_path)
    plot_data = np.load(data_path) # Second argument is path
    
    # Extract HSV data
    hues = plot_data[:, 0]
    sats = plot_data[:, 1]
    vals = plot_data[:, 2]

    # Convert back to RGB coloirs to display in plot
    colors_rgb = mcolors.hsv_to_rgb(plot_data)

    fig = plt.figure()
    ax = fig.add_subplot(projection="3d")

    ax.scatter(hues, sats, vals, marker="s", c=colors_rgb, edgecolors='none')

    ax.set_xlabel("Hue")
    ax.set_ylabel("Saturation")
    ax.set_zlabel("Value")
    ax.set_title(f"{filename} HSV Frames Path")

    plt.show()
    
    print("Successfully loaded file.")
    exit()



start_t = time.time()
video_path = sys.argv[1]
filename = os.path.basename(video_path)  # Returns "video_name.mp4"
video_name = os.path.splitext(filename)[0] # Returns "video_name"

# FFmpeg Command: Stream width and height of video to stdout
probe_command = [
    'ffprobe', 
    '-v', 'error', 
    '-select_streams', 'v:0', 
    '-show_entries', 'stream=width,height', 
    '-of', 'csv=s=x:p=0', 
    video_path
]

# Run it and capture the output (e.g., "1920x1080")
result = subprocess.check_output(probe_command).decode('utf-8').strip()
result = result.split('x')[:2]


# Split the result into width and height
width, height = map(int, result)

print("INFO | Detected dimentions: ",width ," x ", height)
bytes_per_frame = width * height * 3

# FFmpeg Command: Stream raw rgb24 to stdout
main_command = [
    'ffmpeg',
    '-i', video_path,
    '-vf', 'fps=1/6,format=rgb24', 
    '-f', 'rawvideo',
    '-pix_fmt', 'rgb24',
    '-'
]

process = subprocess.Popen(main_command, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)

all_hsv_data = []


try:
    print("INFO | Processing frames...")
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
    
# Convert data into np array
plot_data = np.array(all_hsv_data)

# Save binary data
os.makedirs("data", exist_ok=True)
np.save(f"data/{video_name}.npy", plot_data) #use np.load later    

# Display time of execution
elapsed_time_s = round(time.time() - start_t)
print(f"Processed {len(plot_data)} frames in {elapsed_time_s} seconds.\nAvg Frames Processed per second: {len(plot_data)/elapsed_time_s}")

# Extract HSV data
hues = plot_data[:, 0]
sats = plot_data[:, 1]
vals = plot_data[:, 2]

# Convert back to RGB coloirs to display in plot
colors_rgb = mcolors.hsv_to_rgb(plot_data)

# Display Scatterplot
fig = plt.figure()
ax = fig.add_subplot(projection="3d")

ax.scatter(hues, sats, vals, marker="s", c=colors_rgb, edgecolors='none')

ax.set_xlabel("Hue")
ax.set_ylabel("Saturation")
ax.set_zlabel("Value")
ax.set_title(f"{video_name} HSV Frames Path")

plt.show()
