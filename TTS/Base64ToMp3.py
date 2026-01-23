import base64
from io import BytesIO
from pydub import AudioSegment
import os


def save_audio_from_base64(input_file, output_file, output_format="wav"):
    """
    从包含Base64编码的文本文件中读取数据，解码并保存为音频文件（WAV/MP3）

    参数:
        input_file (str): 包含Base64编码的文本文件路径
        output_file (str): 输出音频文件路径
        output_format (str): 输出格式（"wav" 或 "mp3"）
    """
    # 读取Base64数据
    with open(input_file, 'r') as file:
        audio_data = file.read().strip()  # 去除首尾空白字符

    # 处理可能的DataURL前缀（如 "data:audio/wav;base64,"）
    if 'base64,' in audio_data:
        audio_base64 = audio_data.split('base64,')[1]
    else:
        audio_base64 = audio_data

    # Base64解码
    try:
        decoded_data = base64.b64decode(audio_base64)
    except Exception as e:
        raise ValueError(f"Base64解码失败: {e}")

    # 通过pydub加载音频数据
    try:
        # 使用BytesIO创建文件对象
        audio = AudioSegment.from_file(BytesIO(decoded_data))

        # 根据格式保存文件
        if output_format.lower() == "wav":
            audio.export(output_file, format="wav")
        elif output_format.lower() == "mp3":
            audio.export(output_file, format="mp3", bitrate="192k")
        else:
            raise ValueError("不支持的输出格式，请选择 'wav' 或 'mp3'")

        print(f"✅ 音频已保存为 {output_file} ({output_format.upper()})")
        return True

    except Exception as e:
        raise RuntimeError(f"音频处理失败: {e}")


# 示例用法
if __name__ == "__main__":
    # 输入文件（包含Base64编码的音频数据）
    input_file = "audio_base64.txt"

    # 输出配置
    output_file = "output_audio"  # 扩展名会根据格式自动添加
    output_format = "wav"  # 可选 "wav" 或 "mp3"

    # 确保输入文件存在
    if not os.path.exists(input_file):
        print(f"❌ 错误: 输入文件 {input_file} 不存在")
    else:
        try:
            save_audio_from_base64(
                input_file,
                f"{output_file}.{output_format}",
                output_format
            )
        except Exception as e:
            print(f"❌ 发生错误: {e}")