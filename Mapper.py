import folium
import folium.plugins

from datetime import datetime

class MissingDataError(Exception):
    pass

class Map:
    """A class used to represent a Map with GPS data plotting capabilities.
    Attributes:
        map (folium.Map): The folium map object.
        all_points (list): A list to store all GPS points.
        all_gps_data (list): A list to store all GPS data.
    Methods:
        __init__():
            Initializes the Map object with a folium map centered at [0, 0] with a zoom level of 12.
        convert_date_format(date_str):
            Converts a date string from one format to another.
        speed_to_hex(speed, min_speed=30, max_speed=60):
            Converts a speed value to a hexadecimal color representation, where the color transitions from green to red based on the speed within a specified range.
        plot_gps_data(gps_data):
        add_vehicle_position():
            Adds vehicle positions to the map using GPS data, creating a series of points representing vehicle positions with animated playback.
        save(filename):
            Saves the map to an HTML file.
    """

    map = None
    all_points = []
    all_gps_data = []

    def __init__(self):
        self.map = folium.Map(location=[0, 0], zoom_start=12)

    def convert_date_format(self, date_str):
        """
        Convert a date string from one format to another.
        Args:
            date_str (str): The date string to be converted, expected in the format "%Y:%m:%d %H:%M:%S.%fZ".
        Returns:
            str: The converted date string in the format "%Y-%m-%dT%H:%M:%S".
        """
        
        # Convert to datetime object
        date_obj = datetime.strptime(date_str, "%Y:%m:%d %H:%M:%S.%fZ")
        
        # Convert to desired format
        formatted_date_str = date_obj.strftime("%Y-%m-%dT%H:%M:%S")
        
        return formatted_date_str

    def speed_to_hex(self, speed, min_speed=30, max_speed=60):
        """
        Converts a speed value to a hexadecimal color representation, where the color
        transitions from green to red based on the speed within a specified range.
        Args:
            speed (float): The speed value to convert.
            min_speed (float, optional): The minimum speed value for the color range. Defaults to 30.
            max_speed (float, optional): The maximum speed value for the color range. Defaults to 60.
        Returns:
            str: The hexadecimal color representation of the speed.
        """
    
        # Define color range
        min_color = (0, 255, 0)  # Green
        max_color = (255, 0, 0)  # Red
    
        # Calculate color differences
        red_diff = max_color[0] - min_color[0]
        green_diff = max_color[1] - min_color[1]
        blue_diff = max_color[2] - min_color[2]
    
        if max_speed != min_speed:
            proportion = (speed - min_speed) / (max_speed - min_speed)
        else:
            proportion = 0  # or any other default value you prefer
    
        # Apply a quadratic transformation to skew towards green
        skewed_proportion = proportion ** 2
    
        # Calculate the color shifts
        red_shift = int(red_diff * skewed_proportion)
        green_shift = int(green_diff * skewed_proportion)
        blue_shift = int(blue_diff * skewed_proportion)
    
        # Calculate the final color
        red = min_color[0] + red_shift
        green = min_color[1] + green_shift
        blue = min_color[2] + blue_shift
    
        # Convert RGB to hex
        hex_color = f"#{red:02x}{green:02x}{blue:02x}"
        return hex_color

    def plot_gps_data(self, gps_data):
        """
        Plots GPS data on a map with a gradient of colors based on speed.
        Args:
            gps_data (list): A list of GPS data objects. Each object should have the attributes:
                - GPSLatitude (float): Latitude of the GPS coordinate.
                - GPSLongitude (float): Longitude of the GPS coordinate.
                - GPSSpeed (float): Speed at the GPS coordinate.
                - GPSDate_Time (str): Timestamp of the GPS coordinate.
        The method performs the following steps:
            1. Creates a polyline to show the path based on the GPS coordinates.
            2. Splits the points into overlapping groups of 5 and calculates the average speed for each group.
            3. Plots the lines with a gradient of colors based on the speed.
            4. Draws a marker every 200th point with a tooltip showing the timestamp.
            5. Adds all points to the list of all points and all GPS data to the list of all GPS data.
            6. Fits the map to the bounds of all points.
        """

        # Check if GPS data is available
        if not gps_data:
            raise MissingDataError("No GPS data to plot.")
        
        # Check if GPS data has the required attributes
        required_attributes = ["GPSLatitude", "GPSLongitude", "GPSSpeed", "GPSDate_Time"]
        if not all(hasattr(coord, attr) for coord in gps_data for attr in required_attributes):
            raise MissingDataError("GPS data is missing required attributes.")

        # # Create a polyline to show the path
        points = [(float(coord.GPSLatitude), float(coord.GPSLongitude)) for coord in gps_data]
        # folium.PolyLine(points, color="red", weight=2.5, opacity=1).add_to(m)

        # Split the points up into overlapping groups of 5 and calculate the average speed for each group.
        # Plot the lines with a gradient of colors based on the speed.
        min_speed = min(float(coord.GPSSpeed) for coord in gps_data)
        max_speed = max(float(coord.GPSSpeed) for coord in gps_data)

        for i in range(len(points) - 4):
            group = points[i:i+5]
            speed = sum(coord.GPSSpeed for coord in gps_data[i:i+5]) / 5
            color = self.speed_to_hex(speed, min_speed, max_speed)
            folium.PolyLine(group, color=color, weight=2.5, opacity=1, tooltip=speed).add_to(self.map)

        # Also draw a marker every 200th point
        for i in range(0, len(points), 200):
            folium.Circle(points[i], tooltip=f'Time: {gps_data[i].GPSDate_Time}', radius=5, color="yellow", fill=True, fill_opacity=1).add_to(self.map)

        # Add all points to the list of all points and all gps data to the list of all gps data
        self.all_points.extend(points)
        self.all_gps_data.extend(gps_data)

        # Fit map to bounds
        self.map.fit_bounds(self.all_points)

    def add_vehicle_position(self):
        """
        Adds vehicle positions to the map using GPS data.
        This method processes GPS data to create a series of points representing vehicle positions.
        Each point includes the date, speed, and coordinates. The points are then added to the map
        as a TimestampedGeoJson layer, which allows for animated playback of the vehicle's movement
        over time.
        Raises:
            MissingDataError: If no GPS data is available to plot.
        Notes:
            - The method ensures that there is one point per second by removing duplicate timestamps.
            - Each point is represented as a GeoJSON feature with a custom icon.
            - The TimestampedGeoJson layer includes settings for playback speed, transition time, and looping.
        """

        if not self.all_gps_data:
            raise MissingDataError("No GPS data to plot. Consider calling plot_gps_data() first.")

        points = [
            {
                "dates": self.convert_date_format(coord.GPSDate_Time),
                "popup": f"Speed: {coord.GPSSpeed} mph",
                "coordinates": [float(coord.GPSLongitude), float(coord.GPSLatitude)],
            } 
            for coord in self.all_gps_data]
        
        # We want one point per second. Remove duplicates.
        points = [point for i, point in enumerate(points) if i == 0 or points[i-1]["dates"] != point["dates"]]
        
        features = [
            {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": point["coordinates"],
                },
                "properties": {
                    "time": point["dates"],
                    "popup": point["popup"],
                    "id": "house",
                    "icon": "marker",
                    "iconstyle": {
                        "iconUrl": "https://cdn.icon-icons.com/icons2/3249/PNG/512/vehicle_car_filled_icon_199629.png",
                        "iconSize": [20, 20],
                    },
                },
            }
            for point in points
        ]

        folium.plugins.TimestampedGeoJson(
            {
                "type": "FeatureCollection",
                "features": features,
            },
            period="PT1S",
            duration="PT0S",
            add_last_point=False,
            min_speed=0.1,
            max_speed=10,
            transition_time=1000,
            time_slider_drag_update=True,
            loop=True,
        ).add_to(self.map)

    def save(self, filename):
        self.map.save(filename)
        print(f"Map saved as {filename}")

    @classmethod
    def from_video(cls, video):
        map = cls()
        map.plot_gps_data(video.get_gps_data())
        map.add_vehicle_position()
        return map
    
    @classmethod
    def from_videos(cls, videos, log=False):
        map = cls()

        if log:
            print(f"Plotting {len(videos)} videos...")

        for video in videos:
            print(f"Plotting video {video.path}...")

            try:
                map.plot_gps_data(video.get_gps_data())
            except MissingDataError as e:
                print(f"Error: {e}")
                continue
            
        map.add_vehicle_position()
        return map
