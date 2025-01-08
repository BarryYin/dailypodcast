import requests
import time
from pydub import AudioSegment
import os
import re

def fetch_and_save_audio(reference_id, text, extension="mp3"):
    """从指定的 URL 获取音频并保存为文件"""
    url = "https://direct.api.fish-audio.cn/v1/tts"
    payload = {
        "reference_id": reference_id,
        "text": text
    }
    headers = {
        "Authorization": "Bearer 0eade003864e40fd9a2746bcd776e002",  #ac2c93a945ee4869b76051d5f4419760
        "Content-Type": "application/json"
    }
    #ac2c93a945ee4869b76051d5f4419760
    response = requests.request("POST", url, json=payload, headers=headers)
    
    if response.status_code == 200:  # 检查请求是否成功
        timestamp = int(time.time())  # 获取当前时间戳
        #filename = f"output_audio_{timestamp}.{extension}"  # 动态生成文件名
        filename = extension
        with open(filename, "wb") as audio_file:  # 修改文件名和扩展名根据实际情况
            audio_file.write(response.content)  # 使用 response.content 获取二进制数据
        print(f"音频已保存为 {filename}")
    else:
        print(f"请求失败，状态码: {response.status_code}")

def fetch_and_save_male_audio(text, extension="mp3"):
    """获取男声音频并保存"""
    male_reference_id = "59cb5986671546eaa6ca8ae6f29f6d22"  # 替换为实际的男声 reference_id 59cb5986671546eaa6ca8ae6f29f6d22，1bd64db7e92e426dbf4f54f6f4f1d570
    fetch_and_save_audio(male_reference_id, text, extension)

def fetch_and_save_female_audio(text, extension="mp3"):
    """获取女声音频并保存"""
    female_reference_id = "5c353fdb312f4888836a9a5680099ef0"  # 替换为实际的女声 reference_id 8065c9e04bd44db5b2fb974b5b3fedd6  74a543044a7b445696f6fc77a8aafa8d
    fetch_and_save_audio(female_reference_id, text, extension)


audio_files = []  # 用于存储生成的音频文件名

def generate_audio_from_dialogue(dialogue):
    """根据对话生成音频并记录文件名"""
    for speaker, text in dialogue:
        if speaker == "male":
            filename = f"output_audio_male_{int(time.time())}.mp3"  # 动态生成文件名
            fetch_and_save_male_audio(text, filename)  # 传递文件名
            audio_files.append(filename)  # 将文件名添加到列表
        elif speaker == "female":
            filename = f"output_audio_female_{int(time.time())}.mp3"  # 动态生成文件名
            fetch_and_save_female_audio(text, filename)  # 传递文件名
            audio_files.append(filename)  # 将文件名添加到列表
        time.sleep(1)



def merge_audio_files(audio_files1):
    """合并多个音频文件为一个音频文件"""
    global audio_files
    combined = AudioSegment.empty()
    
    for file in audio_files1:
        audio_segment = AudioSegment.from_file(file)
        combined += audio_segment  # 将音频片段添加到合并的音频中
    
    timestamp = int(time.time())
    output_file = f"merged_audio_{timestamp}.mp3"
    combined.export(output_file, format="mp3")  # 导出合并后的音频文件
    print(f"合并后的音频已保存为 {output_file}")

     # 删除原有音频文件
    for file in audio_files1:
        os.remove(file)
        print(f"已删除原音频文件: {file}")
    
    audio_files = []
    return output_file

# 示例对话
# dialogue = [
#     ("male", "你好，今天的天气怎么样？"),
#     ("female", "今天阳光明媚，非常适合外出。"),
#     ("male", "那我们去公园散步吧。"),
#     ("female", "好主意！")
# ]


raw_dialogue3='''
Andy："我喜欢这个。这不是关于取代人。而是关于给他们更好的工具。那么，他们还在探索其他什么人工智能驱动的创新？还有什么在地平线上？"
Amily："他们也谈到了这个数字图书馆员的想法。是的，这些将是由人工智能驱动的头像，可以与人互动，你知道，像在更个性化的方式。所以你实际上可以与一个数字图书馆员交谈。"
Andy："明白了。你可以索要书籍推荐，研究帮助，甚至只是聊天。对于可能对与真人交谈感到害羞或喜欢自己找信息的人来说，这可能是一个巨大的变化。"
Amily："我的意思是，这很吸引人，我可以看到这将如何吸引那些一直与技术互动长大的年轻一代。"
Andy："绝对。这是关于在用户所在的地方与他们会面，以自然和吸引人的方式为他们提供工具和资源。好的。"
Amily："我完全同意这些数字图书馆员。这听起来非常未来主义。那么阅读推广呢？人工智能如何帮助人们对书籍感到兴奋？"
Andy："这就是超个性化推荐的想法。哦，对。所以这些建议针对你的兴趣和阅读水平量身定制。想象一下，得到如此好的建议，你不得不读这本书。"
Amily："我报名。这绝对是我支持的人工智能用途。而且我知道，个性化可以走得更远，瑞安。它不仅仅是关于推荐书籍。"
Andy："你说得对。人工智能可以个性化整个图书馆体验，你知道，推荐活动，甚至自定义在线图书馆对你的外观。这是关于使体验对每个人来说都容易和有趣。"
Amily："这就像有一个个人导游为你的阅读之旅服务。我喜欢它。完全正确。但所有这些听起来都很棒。是的，我必须询问潜在的负面影响。你知道，我们听说过关于人工智能偏见和算法使事情不公平的故事。云瀚如何确保他们的人工智能以一种对每个人都有益的方式使用？这是一个。"
'''

def convert_to_dialogue(raw_dialogue):
    """将原始对话文本转换为对话列表"""
    dialogue = []
    lines = raw_dialogue.strip().split('\n')
    
    for line in lines:
        # 跳过空行
        if not line.strip():
            continue

        # 使用正则表达式匹配对话
        male_match = re.match(r'Andy："(.*?)"', line)
        female_match = re.match(r'Amily："(.*?)"', line)
        
        if male_match:
            content = male_match.group(1)  # 提取匹配的内容
            dialogue.append(("male", content))
        elif female_match:
            content = female_match.group(1)  # 提取匹配的内容
            dialogue.append(("female", content))
        else:
            print(f"警告: 找不到对话内容: {line}")  # 调试输出
    
    return dialogue

def text_to_tts(dialogue):
    # 调用函数转换对话
    dialogue1 = convert_to_dialogue(dialogue)
    # 调用函数生成音频
    generate_audio_from_dialogue(dialogue1)
    output_files = merge_audio_files(audio_files)
    return output_files


# 运行主函数
if __name__ == "__main__":
    
    #pass

   

# # 调用函数生成音频
    #generate_audio_from_dialogue(raw_dialogue3)
    text_to_tts(raw_dialogue3)


