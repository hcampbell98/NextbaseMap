import os
import exiftool
import folium
import math

#{'GPSAltitude': '110.2', 'GPSDilutionOfPrecision': '0.81', 'GPSDate/Time': '2024:11:08 12:38:33.900Z', 'GPSLatitude': '53.6068471666667', 'GPSLongitude': '-1.78887966666667', 'GPSSatellites': '14', 'GPSSpeed': '44.751728', 'GPSTrack': '346.14'}
class GPS:
    def __init__(self, GPSLatitude, GPSLongitude, GPSAltitude, GPSSpeed, GPSTrack, GPSDate_Time):
        self.GPSLatitude = GPSLatitude
        self.GPSLongitude = GPSLongitude
        self.GPSAltitude = GPSAltitude
        self.GPSSpeed = GPSSpeed
        self.GPSTrack = GPSTrack
        self.GPSDate_Time = GPSDate_Time
    
    @classmethod
    def from_dict(cls, data, mph=False):
        return cls(
            data['GPSLatitude'],
            data['GPSLongitude'],
            data['GPSAltitude'],
            round(float(data['GPSSpeed']), 2) if not mph else round(float(data['GPSSpeed']) * 0.621371, 2),
            data['GPSTrack'],
            data['GPSDate/Time']
        )


class GPSVideo:
    def __init__(self, path):
        self.path = path
    
    def getGPS(self):
        """
        Extracts GPS data from a video file using ExifTool.

        Returns:
            A list of GPS objects containing the extracted data.
        """

        with exiftool.ExifTool() as et:
            result = et.execute(self.path, '-ee')
            result = result.replace("[QuickTime]     ", "")

        data = result.split('Sample Duration')[1:]
        gps_data = []
        
        for section in data:
            lines = section.split('\n')
            gps = {}
            for line in lines:
                if 'GPS' in line:
                    key, value = line.split(':', 1)

                    key = key.replace(' ', '')
                    gps[key] = value.strip()
            gps_data.append(GPS.from_dict(gps, True))
            self.gps_data = gps_data
    
    def speed_to_hex(self, speed, min_speed=30, max_speed=60):
        """Maps a speed value to a hex color code within a specified range.
    
        Args:
            speed: The speed value to map.
            min_speed: The minimum speed in the range.
            max_speed: The maximum speed in the range.
    
        Returns:
            The hex color code corresponding to the given speed.
        """
    
        # Define color range
        min_color = (0, 255, 0)  # Green
        max_color = (255, 0, 0)  # Red
    
        # Calculate color differences
        red_diff = max_color[0] - min_color[0]
        green_diff = max_color[1] - min_color[1]
        blue_diff = max_color[2] - min_color[2]
    
        # Calculate the proportion of the speed within the range
        proportion = (speed - min_speed) / (max_speed - min_speed)
    
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

    def plot_gps_data(self):
        self.getGPS()

        # Calculate the average latitude and longitude for centering the map
        avg_lat = sum(float(coord.GPSLatitude) for coord in self.gps_data) / len(self.gps_data)
        avg_lon = sum(float(coord.GPSLongitude) for coord in self.gps_data) / len(self.gps_data)

        # Create a map centered around the average coordinates
        m = folium.Map(location=[avg_lat, avg_lon], zoom_start=12)

        # # Create a polyline to show the path
        points = [(float(coord.GPSLatitude), float(coord.GPSLongitude)) for coord in self.gps_data]
        # folium.PolyLine(points, color="red", weight=2.5, opacity=1).add_to(m)

        # Split the points up into overlapping groups of 5 and calculate the average speed for each group.
        # Plot the lines with a gradient of colors based on the speed.
        min_speed = min(float(coord.GPSSpeed) for coord in self.gps_data)
        max_speed = max(float(coord.GPSSpeed) for coord in self.gps_data)

        for i in range(len(points) - 4):
            group = points[i:i+5]
            speed = sum(coord.GPSSpeed for coord in self.gps_data[i:i+5]) / 5
            color = self.speed_to_hex(speed, min_speed, max_speed)
            folium.PolyLine(group, color=color, weight=2.5, opacity=1, tooltip=speed).add_to(m)

        # Also draw a marker every 200th point
        for i in range(0, len(points), 200):
            folium.Circle(points[i], tooltip=f'Time: {self.gps_data[i].GPSDate_Time}', radius=5, color="yellow", fill=True, fill_opacity=1).add_to(m)

        # Fit map to bounds
        m.fit_bounds(points)

        # Save the map to an HTML file
        m.save('gps_map.html')

    def get_gps_data(self):
        return self.gps_data
            


video_path = 'E:\\Desktop\\Programming\\Python\\NextbaseMap\\video.MP4'
video = GPSVideo(video_path)
video.plot_gps_data()