# Project Documentation

[](demo.mp4)

## Overview

This project processes GPS data from video files and plots it on an interactive map using the **folium** library. The map displays the vehicle's path with a gradient of colors based on speed and allows for animated playback of the vehicle's movement over time.

## Classes and Methods

### Metadata.py

#### GPS

Represents a GPS data point.

-   **`__init__`(self, GPSLatitude, GPSLongitude, GPSAltitude, GPSSpeed, GPSTrack, GPSDate_Time)**
    -   Initializes a GPS data point.
-   **`from_dict`(cls, data, mph=False)**
    -   Creates a GPS object from a dictionary.

#### GPSVideo

Extracts GPS data from a video file.

-   **`__init__`(self, path)**

    -   Initializes the GPSVideo object with the path to the video file.

-   **`processGPS`(self)**

    -   Extracts GPS data from the video file using ExifTool.

-   **`get_gps_data`(self)**
    -   Returns the extracted GPS data.

### Mapper.py

#### MissingDataError

Custom exception for missing data.

#### Map

Represents a map with GPS data plotting capabilities.

-   **`__init__`(self)**

    -   Initializes the Map object with a folium map centered at [0, 0] with a zoom level of 12.

-   **`convert_date_format`(self, date_str)**

    -   Converts a date string from one format to another.

-   **`speed_to_hex`(self, speed, min_speed=30, max_speed=60)**

    -   Converts a speed value to a hexadecimal color representation.

-   **`plot_gps_data`(self, gps_data)**

    -   Plots GPS data on the map with a gradient of colors based on speed.

-   **`add_vehicle_position`(self)**

    -   Adds vehicle positions to the map using GPS data, creating a series of points representing vehicle positions with animated playback.

-   **`save`(self, filename)**

    -   Saves the map to an HTML file.

-   **`from_video`(cls, video)**

    -   Creates a Map object from a single video.

-   **`from_videos`(cls, videos)**
    -   Creates a Map object from multiple videos.

## Usage

1. Place your video files in the `test_video` directory.
2. Update the `video_paths` list in `app.py` with the paths to your video files.
3. Run the `app.py` script to generate the map:

    ```sh
    python app.py
    ```

4. Open the generated `gps_map.html` file to view the interactive map.

## Example

```python
from Metadata import GPSVideo
from Mapper import Map

video_paths = [
    'test_video\\video1.MP4',
    'test_video\\video2.MP4',
]

map = Map.from_videos([GPSVideo(path) for path in video_paths])
map.save("gps_map.html")
```
