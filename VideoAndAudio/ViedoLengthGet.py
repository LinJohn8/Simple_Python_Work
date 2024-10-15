import os
import moviepy.editor as mp


def get_total_video_duration(folder_path):
    # 列出文件夹中所有的文件
    files = os.listdir(folder_path)
    total_duration = 0  # 总时长初始化为0

    # 遍历文件，检查是否为mp4格式
    for file in files:
        if file.endswith('.mp4'):
            # 构造完整的文件路径
            file_path = os.path.join(folder_path, file)
            # 使用moviepy获取视频时长
            video = mp.VideoFileClip(file_path)
            total_duration += video.duration

    return total_duration


def convert_seconds_to_hh_mm_ss(total_duration):
    """
    Convert total duration in seconds to hours, minutes, and seconds.
    """
    hours = total_duration // 3600
    minutes = (total_duration % 3600) // 60
    seconds = total_duration % 60
    return f"{int(hours)}小时{int(minutes)}分{int(seconds)}秒"


# 使用示例：
# 将下面的路径替换为你的文件夹路径
folder_path = 'C:\\Users\\ADMIN\\Desktop\\视频剪辑\\最终教程'
total_duration = get_total_video_duration(folder_path)
converted_duration = convert_seconds_to_hh_mm_ss(total_duration)
print(f"总时间: {total_duration} 秒")
print(f"总时间: {converted_duration}")
