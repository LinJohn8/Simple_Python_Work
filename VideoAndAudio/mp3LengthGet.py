import os
from mutagen.mp3 import MP3


def get_mp3_duration(file_path):
    audio = MP3(file_path)
    return audio.info.length


def get_total_duration(directory):
    total_duration = 0
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.mp3'):
                file_path = os.path.join(root, file)
                try:
                    total_duration += get_mp3_duration(file_path)
                except Exception as e:
                    print(f"Error reading {file}: {e}")
    return total_duration


# 将 "your_directory" 替换为包含 MP3 文件的文件夹路径
directory = r"C:\Users\ADMIN\Desktop\2"
total_duration = get_total_duration(directory)
print(f"Total duration: {total_duration:.1f} s")
