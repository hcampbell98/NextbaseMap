import os
import exiftool
import folium
import math
from Mapper import Map

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
    gps_data = []
    def __init__(self, path):
        self.path = path
        self.gps_data = self.processGPS()
    
    def processGPS(self):
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
        return gps_data

    def get_gps_data(self):
        return self.gps_data