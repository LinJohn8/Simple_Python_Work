import os
from pydub import AudioSegment


# 音频速度调整函数
def change_audio_speed(sound, speed=2.0):
    sound_with_changed_speed = sound._spawn(sound.raw_data, overrides={
        "frame_rate": int(sound.frame_rate * speed)
    })
    return sound_with_changed_speed.set_frame_rate(sound.frame_rate)


# 处理目标文件夹内的所有 mp3 文件，并保存到新的文件夹，文件名保持不变
def process_mp3_files_in_folder(folder_path, output_folder, speed=2.0):
    # 创建输出文件夹（如果不存在）
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith(".mp3"):
                file_path = os.path.join(root, file)
                print(f"Processing file: {file_path}")

                # 读取音频文件
                sound = AudioSegment.from_mp3(file_path)

                # 调整速度
                altered_sound = change_audio_speed(sound, speed)

                # 确定新的文件路径（新文件夹中，但保持原文件名）
                new_file_path = os.path.join(output_folder, file)

                # 保存新文件
                altered_sound.export(new_file_path, format="mp3")
                print(f"Saved sped-up file to: {new_file_path}")


# 设定源文件夹和目标文件夹
folder_path = r"C:\Users\ADMIN\Desktop\2"
output_folder = r"C:\Users\ADMIN\Desktop\3"
process_mp3_files_in_folder(folder_path, output_folder, speed=1.5)
