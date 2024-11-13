from Metadata import GPSVideo
from Mapper import Map

video_paths = [
    'test_video\\video1.MP4',
    'test_video\\video2.MP4',
    # 'video3.MP4',
]

map = Map.from_videos([GPSVideo(path) for path in video_paths])
map.save("gps_map.html")