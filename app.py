import ffmpeg
import os, re, math
import pytesseract
from PIL import Image
import folium

class VideoAnalyzer:
    def __init__(self, path):
        self.path = path
        self.frames = []
        self.gps_data = []

    def split_video_into_frames(self, w, h, x_crop, y_crop):
        output_folder = 'output'
        if os.path.exists(output_folder):
            os.system('rm -rf output')
        os.mkdir(output_folder)

        try:
            ffmpeg.input(self.path).filter('crop', w,h, x=x_crop, y=y_crop).filter('fps', fps=1).output(f'{output_folder}/frame%d.png').run()
        except ffmpeg.Error as e:
            print(f'An error occurred: {e}')
            return

        def sort_key(file):
            match = re.search(r'(\d+)', file)
            return int(match.group(1)) if match else -1


        for file in sorted(os.listdir(output_folder), key=sort_key):
            if file.endswith('.png'):
                self.frames.append(file)

    def text_to_gps(self, text):
        # Text format: N53.57322 W1.78285 11:26:46 29/10/2024
        # Sometimes there's eroneous data in the text, so we need to handle that
        chars = set('0123456789:/NW. ')
        text = ''.join(filter(chars.__contains__, text))
        try:
            gps_data = text.split(' ')
            lat = gps_data[0].replace('N', '').replace('E', '-').replace(':', '.')
            lon = gps_data[1].replace('W', '-').replace('S', '').replace(':', '.')
            time = gps_data[2]
            date = gps_data[3]

            print(f'Latitude: {lat}, Longitude: {lon}, Time: {time}, Date: {date}')

            return {
                'lat': lat,
                'lon': lon,
                'time': time,
                'date': date
            }
        except Exception as e:
            print(f'An error occurred during text to GPS conversion: {e}')
            return None

    def ocr_frame(self, frame):
            try:
                img = Image.open(frame)

                # Apply a threshold to the image to make it easier for Tesseract to detect text
                img = img.point(lambda p: p > 128 and 255)

                text = pytesseract.image_to_string(img)
                return text
            except Exception as e:
                print(f'An error occurred during OCR: {e}')
                return None

    def ocr_frames(self):
        for x,frame in enumerate(self.frames):
            text = self.ocr_frame(f'output/{frame}')
            if text:
                gps_data = self.text_to_gps(text)
                if gps_data:
                    gps_data['index'] = x
                    self.gps_data.append(gps_data)     

    def plot_gps_data(self):
        if not self.gps_data:
            print("No GPS data to plot.")
            return

        # Calculate the average latitude and longitude for centering the map
        avg_lat = sum(float(coord['lat']) for coord in self.gps_data) / len(self.gps_data)
        avg_lon = sum(float(coord['lon']) for coord in self.gps_data) / len(self.gps_data)

        # Create a map centered around the average coordinates
        m = folium.Map(location=[avg_lat, avg_lon], zoom_start=12)

        # # Create a polyline to show the path
        points = [(float(coord['lat']), float(coord['lon'])) for coord in self.gps_data]
        # folium.PolyLine(points, color="red", weight=2.5, opacity=1).add_to(m)

                # Split the points up into overlapping groups of 5 and calculate the average speed for each group.
        # Plot the lines with different colors based on the speed.
        
        for i in range(len(points) - 4):
            group = points[i:i+5]
            speed = 0
            for j in range(1, len(group)):
                lat1, lon1 = group[j-1]
                lat2, lon2 = group[j]
                # Calculate the distance between two points using the haversine formula
                # https://en.wikipedia.org/wiki/Haversine_formula
                R = 6371
                dlat = lat2 - lat1
                dlon = lon2 - lon1
                a = (dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * (dlon/2)**2
                c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
                distance = R * c
                speed += distance / 5
        
            print(speed)
            color = 'green' if speed < 10 else 'yellow' if speed < 20 else 'red'
            folium.PolyLine(group, color=color, weight=2.5, opacity=1).add_to(m)
        

        # Fit map to bounds
        m.fit_bounds(points)

        # Save the map to an HTML file
        m.save('gps_map.html')

# Ensure the video file path is correct
video_path = os.path.join(os.getcwd(), 'video2.MP4')

v = VideoAnalyzer(video_path)
v.split_video_into_frames(800, 45, 1188, 1373)
v.ocr_frames()
print(v.gps_data)

# Plot the GPS data on a map
v.plot_gps_data()
