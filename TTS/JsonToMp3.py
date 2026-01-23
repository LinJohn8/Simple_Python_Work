import json
import numpy as np
from scipy.io.wavfile import write
import re


def extract_audio_frames(json_str):
    """从复杂的嵌套JSON中提取音频帧数据"""

    # 方法1: 寻找frame字段
    frame_match = re.search(r'"frame"\s*:\s*\[([^\]]+)\]', json_str)
    if frame_match:
        frame_str = frame_match.group(1)
        print(f"找到frame数据: {frame_str[:100]}...")
        try:
            numbers = []
            for num_str in frame_str.split(","):
                num_str = num_str.strip()
                if num_str and not num_str.startswith('"') and not num_str.startswith("'"):
                    try:
                        if num_str.lstrip('-').isdigit():
                            numbers.append(int(num_str))
                    except ValueError:
                        continue
            print(f"成功解析数字: {len(numbers)}个")
            return numbers
        except Exception as e:
            print(f"正则提取失败: {e}")

    # 方法2: 寻找大量连续数字的模式（可能是直接的音频数组）
    # 匹配类似 [数字,数字,数字...] 的模式，数字可以是负数
    number_array_match = re.search(r'\[(-?\d+(?:\s*,\s*-?\d+){50,})\]', json_str)
    if number_array_match:
        numbers_str = number_array_match.group(1)
        print(f"找到数字数组: {numbers_str[:100]}...")
        try:
            numbers = []
            for num_str in numbers_str.split(","):
                num_str = num_str.strip()
                if num_str.lstrip('-').isdigit():
                    numbers.append(int(num_str))
            print(f"成功解析数字数组: {len(numbers)}个")
            return numbers
        except Exception as e:
            print(f"数字数组提取失败: {e}")

    # 方法3: 更宽泛的数字匹配，寻找任何包含大量数字的区域
    # 这种方法风险较大，但可能是最后的手段
    all_numbers = re.findall(r'-?\d+', json_str)
    if len(all_numbers) > 100:  # 假设音频数据至少有100个样本
        try:
            # 过滤掉明显不是音频数据的数字（如状态码200, ID等）
            audio_numbers = []
            for num_str in all_numbers:
                num = int(num_str)
                # 音频数据通常在 -32768 到 32767 范围内（16位PCM）
                # 或者 -128 to 127 范围内（8位PCM）
                if -32768 <= num <= 32767:
                    audio_numbers.append(num)

            if len(audio_numbers) > 100:
                print(f"通过数字过滤找到可能的音频数据: {len(audio_numbers)}个")
                return audio_numbers
        except Exception as e:
            print(f"数字过滤失败: {e}")

    print("所有方法都未找到音频数据")
    return []


def process_streaming_json(input_txt, output_wav="output.wav", sample_rate=16000):
    """处理包含特殊格式的流式JSON音频数据"""
    all_frames = []
    line_count = 0
    success_count = 0

    try:
        with open(input_txt, 'r', encoding='utf-8') as f:
            print("正在处理音频数据...")

            for line in f:
                line_count += 1
                line = line.strip()
                if not line:
                    continue

                # 处理 data:"..." 格式
                json_str = line
                if line.startswith('data:"') and line.endswith('"'):
                    # 提取引号内的JSON字符串并处理转义
                    json_str = line[6:-1]  # 去掉 'data:"' 和末尾的 '"'
                    json_str = json_str.replace('\\"', '"')  # 处理转义的双引号

                # 提取音频帧
                frames = extract_audio_frames(json_str)
                if frames:
                    all_frames.extend(frames)
                    success_count += 1
                    print(f"行 {line_count}: 成功提取 {len(frames)} 个样本")
                # 移除未找到音频数据的打印，减少输出噪音

        if not all_frames:
            print("错误:未发现有效音频数据")
            return False

        # 转换为numpy数组
        # 假设音频数据是16位PCM格式，范围在-32768到32767之间
        audio_array = np.array(all_frames, dtype=np.int16)

        # 如果数据超出16位范围，进行裁剪
        audio_array = np.clip(audio_array, -32768, 32767)

        # 保存为WAV文件
        write(output_wav, sample_rate, audio_array)

        print(f"\n✅ 转换成功")
        print(f"处理行数: {line_count} (成功 {success_count})")
        print(f"总样本数: {len(all_frames)}")
        print(f"输出文件: {output_wav}")
        print(f"音频时长: {len(all_frames) / sample_rate:.2f}秒")
        print(f"数据范围: {min(all_frames)} 到 {max(all_frames)}")
        return True

    except Exception as e:
        print(f"\n❌ 处理失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def debug_line_content(input_txt, max_lines=5):
    """调试文件内容，查看前几行的实际格式"""
    print("=== 调试文件内容 ===")
    try:
        with open(input_txt, 'r', encoding='utf-8') as f:
            for i, line in enumerate(f):
                if i >= max_lines:
                    break
                line = line.strip()
                if line:
                    print(f"第{i + 1}行长度: {len(line)}")
                    print(f"前100字符: {line[:100]}")
                    print(f"是否以data:开头: {line.startswith('data:')}")
                    if line.startswith('data:"'):
                        extracted = line[6:-1].replace('\\"', '"')
                        print(f"提取后前100字符: {extracted[:100]}")

                        # 检查是否包含frame关键字
                        if '"frame"' in extracted:
                            print("✅ 包含frame关键字")
                            # 尝试提取frame数据
                            frames = extract_audio_frames(extracted)
                            print(f"提取到的frame数量: {len(frames)}")
                            if frames:
                                print(f"前5个样本: {frames[:5]}")
                        else:
                            print("❌ 不包含frame关键字")
                            # 显示更多内容来查找frame
                            if len(extracted) > 500:
                                print(f"中间500字符: {extracted[500:1000]}")
                    print("-" * 50)
    except Exception as e:
        print(f"调试失败: {e}")


if __name__ == "__main__":
    # 使用示例
    input_file = "audio_json.txt"  # 替换为您的文件路径
    output_file = "output_audio.wav"

    # 先调试文件内容
    print("=== 调试文件前5行 ===")
    debug_line_content(input_file, 5)

    print("\n=== 处理完整文件 ===")
    if process_streaming_json(input_file, output_file):
        print("处理完成!可以播放输出的WAV文件")
    else:
        print("处理失败,请检查:")
        print("1. 输入文件路径是否正确")
        print("2. 文件是否包含有效的音频帧数据")
        print("3. 尝试用文本编辑器检查文件内容格式")