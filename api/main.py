from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Union
import uvicorn
import requests
from bs4 import BeautifulSoup
import json
import re
from zhipuai import ZhipuAI
import pandas as pd
from datetime import datetime
import os
import pytz
import openai
from dotenv import load_dotenv
from pydub import AudioSegment
import time
from fastapi.staticfiles import StaticFiles

load_dotenv()

app = FastAPI()

# 配置静态文件服务
audio_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "audio")
os.makedirs(audio_dir, exist_ok=True)  # 确保音频目录存在
app.mount("/audio", StaticFiles(directory=audio_dir), name="audio")

# 配置智谱AI客户端
ZHIPU_API_KEY = "b82a84253c774ab794cbdaea44af6c93.TldXOkHakGnVFy9f"
glm_client = ZhipuAI(api_key=ZHIPU_API_KEY)

# 配置OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

class AIRequest(BaseModel):
    prompt: str
    model: str = "glm-4-flash"  # 默认使用glm-4模型
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    stream: bool = False

class AIResponse(BaseModel):
    content: str
    error: Optional[str] = None

async def call_glm_model(
    prompt: str,
    model: str = "glm-4",
    temperature: float = 0.7,
    max_tokens: Optional[int] = None,
    stream: bool = False
) -> str:
    """
    调用智谱AI大模型的通用函数
    
    Args:
        prompt: 输入提示词
        model: 模型名称，默认使用glm-4
        temperature: 温度参数，控制输出的随机性，默认0.7
        max_tokens: 最大输出token数，默认None
        stream: 是否使用流式输出，默认False
    
    Returns:
        str: 模型返回的文本内容
    """
    try:
        # 构建请求参数
        messages = [{"role": "user", "content": prompt}]
        
        # 调用模型
        response = glm_client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=stream
        )
        
        # 获取响应内容
        if stream:
            # 处理流式响应
            full_content = ""
            for chunk in response:
                if chunk.choices[0].delta.content is not None:
                    full_content += chunk.choices[0].delta.content
            return full_content
        else:
            # 处理普通响应
            return response.choices[0].message.content
            
    except Exception as e:
        print(f"调用模型时出错: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/chat", response_model=AIResponse)
async def chat_with_ai(request: AIRequest):
    """
    与AI模型对话的API端点
    """
    try:
        response_text = await call_glm_model(
            prompt=request.prompt,
            model=request.model,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            stream=request.stream
        )
        return AIResponse(content=response_text)
    except Exception as e:
        return AIResponse(content="", error=str(e))

#视频理解示例、上传视频URL






# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # 允许的源
    allow_credentials=True,
    allow_methods=["*"],  # 允许的方法
    allow_headers=["*"],  # 允许的头
)

class Content(BaseModel):
    text: str

class GenerationResponse(BaseModel):
    result: str
    error: Optional[str] = None

class NewsItem(BaseModel):
    title: str
    summary: str
    url: str

class NewsResponse(BaseModel):
    news: List[NewsItem]
    error: Optional[str] = None

class UpdateNewsRequest(BaseModel):
    outline: Optional[str] = None
    questions: Optional[str] = None

class OutlineQuestions(BaseModel):
    date: str
    outline: Optional[str] = None
    questions: Optional[str] = None

async def get_cached_news(date_str: str) -> Optional[List[NewsItem]]:
    """
    从CSV文件中获取缓存的新闻
    """
    # 使用绝对路径
    cache_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "news_cache.csv")
    
    try:
        print("\n=== 检查新闻缓存 ===")
        print(f"缓存文件路径: {cache_file}")
        print(f"查找日期: {date_str}")
        
        if not os.path.exists(cache_file):
            print(f"缓存文件不存在")
            return None
            
        # 读取CSV文件
        df = pd.read_csv(cache_file)
        available_dates = df['date'].unique()
        print(f"缓存中的日期: {available_dates}")
        
        # 查找当天的新闻
        day_news = df[df['date'] == date_str]
        
        if len(day_news) == 0:
            print(f"未找到日期 {date_str} 的新闻")
            return None
            
        # 转换为NewsItem列表
        news_items = []
        for _, row in day_news.iterrows():
            news_items.append(NewsItem(
                title=row['title'],
                summary=row['summary'],
                url=row['url']
            ))
        
        print(f"找到 {len(news_items)} 条缓存新闻")
        print("=== 缓存检查完成 ===\n")
        return news_items
    except Exception as e:
        print(f"读取缓存出错: {str(e)}")
        print(f"错误类型: {type(e)}")
        import traceback
        print(f"错误堆栈: {traceback.format_exc()}")
        return None

async def save_news_to_cache(news_items: List[NewsItem], date_str: str):
    """
    将新闻保存到CSV文件
    """
    # 使用绝对路径
    cache_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "news_cache.csv")
    
    try:
        # 准备数据
        data = []
        for news in news_items:
            data.append({
                'date': date_str,
                'title': news.title,
                'summary': news.summary,
                'url': news.url
            })
        
        # 创建新的DataFrame
        new_df = pd.DataFrame(data)
        
        if os.path.exists(cache_file):
            # 如果文件存在，读取并追加
            existing_df = pd.read_csv(cache_file)
            # 删除同一天的旧数据
            existing_df = existing_df[existing_df['date'] != date_str]
            # 合并新旧数据
            final_df = pd.concat([existing_df, new_df], ignore_index=True)
        else:
            final_df = new_df
        
        # 保存到CSV
        final_df.to_csv(cache_file, index=False)
        print(f"成功将{len(news_items)}条新闻保存到缓存: {cache_file}")
        
    except Exception as e:
        print(f"保存缓存时出错: {str(e)}")
        raise e

async def get_outline_questions(date_str: str) -> Optional[OutlineQuestions]:
    """
    从专门的CSV文件中获取大纲和问题
    """
    cache_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "outline_questions.csv")
    
    try:
        if not os.path.exists(cache_file):
            print(f"大纲问题缓存文件不存在: {cache_file}")
            return None
            
        df = pd.read_csv(cache_file)
        day_data = df[df['date'] == date_str]
        
        if len(day_data) == 0:
            print(f"未找到日期 {date_str} 的大纲和问题")
            return None
            
        # 获取最新的一条记录
        latest = day_data.iloc[-1]
        
        # 处理空值
        outline = None if pd.isna(latest.get('outline')) else str(latest.get('outline'))
        questions = None if pd.isna(latest.get('questions')) else str(latest.get('questions'))
        
        return OutlineQuestions(
            date=date_str,
            outline=outline,
            questions=questions
        )
    except Exception as e:
        print(f"读取大纲问题缓存出错: {str(e)}")
        return None

async def save_outline_questions(date_str: str, outline: Optional[str] = None, questions: Optional[str] = None):
    """
    将大纲和问题保存到专门的CSV文件
    """
    cache_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "outline_questions.csv")
    
    try:
        print(f"\n=== 保存大纲和问题到缓存 ===")
        print(f"日期: {date_str}")
        print(f"缓存文件: {cache_file}")
        
        # 如果文件不存在，创建新的DataFrame
        if not os.path.exists(cache_file):
            data = {
                'date': [date_str],
                'outline': [outline],
                'questions': [questions]
            }
            final_df = pd.DataFrame(data)
        else:
            # 读取现有文件
            existing_df = pd.read_csv(cache_file)
            
            # 检查是否已存在该日期的记录
            day_data = existing_df[existing_df['date'] == date_str]
            if len(day_data) > 0:
                # 更新现有记录
                if outline is not None:
                    existing_df.loc[existing_df['date'] == date_str, 'outline'] = outline
                if questions is not None:
                    existing_df.loc[existing_df['date'] == date_str, 'questions'] = questions
                final_df = existing_df
            else:
                # 添加新记录
                new_data = {
                    'date': [date_str],
                    'outline': [outline],
                    'questions': [questions]
                }
                new_df = pd.DataFrame(new_data)
                final_df = pd.concat([existing_df, new_df], ignore_index=True)
        
        # 保存到CSV
        final_df.to_csv(cache_file, index=False)
        print("缓存更新成功")
        print("=== 保存完成 ===\n")
        
    except Exception as e:
        print(f"保存大纲问题缓存时出错: {str(e)}")
        print(f"错误类型: {type(e)}")
        import traceback
        print(f"错误堆栈: {traceback.format_exc()}")
        raise e

@app.get("/api/daily-news", response_model=NewsResponse)
async def get_daily_news():
    try:
        # 获取当前日期（使用中国时区）
        china_tz = pytz.timezone('Asia/Shanghai')
        current_date = datetime.now(china_tz).strftime('%Y-%m-%d')
        
        print(f"\n=== 开始获取每日新闻 ===")
        print(f"当前日期: {current_date}")
        
        # 检查缓存
        print(f"检查新闻缓存...")
        cached_news = await get_cached_news(current_date)
        
        if cached_news is not None and len(cached_news) > 0:
            print(f"找到 {len(cached_news)} 条缓存新闻，直接返回")
            return NewsResponse(news=cached_news)
        
        print("未找到缓存或缓存为空，开始获取新闻...")
        
        # 原有的获取新闻逻辑
        aibase_url = "https://r.jina.ai/https://www.aibase.com/zh/daily"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8"
        }
        
        print("正在获取日报页面...")
        response = requests.get(aibase_url, headers=headers, verify=False)
        response.encoding = 'utf-8'
        
        if response.status_code != 200:
            print(f"获取页面失败: {response.status_code}")
            return NewsResponse(news=[], error=f"获取页面失败: {response.status_code}")
        
        print("成功获取页面，开始解析...")
        content = response.text
        
        # 使用正则表达式提取新闻内容和链接
        news_pattern = r'\[(\d+)、([^\]]+)\]\((https://www\.aibase\.com/zh/news/\d+)\)'
        matches = re.finditer(news_pattern, content)
        
        # 存储新闻项
        news_items = []
        
        # 遍历所有新闻
        for match in matches:
            number = match.group(1)
            title = match.group(2).strip()
            original_url = match.group(3)
            jina_url = f"https://r.jina.ai/{original_url}"
            
            print(f"\n处理第 {number} 条新闻: {title}")
            print(f"获取详细内容: {jina_url}")
            
            try:
                # 获取新闻详细内容
                article_response = requests.get(jina_url, headers=headers, verify=False)
                article_response.encoding = 'utf-8'
                
                if article_response.status_code == 200:
                    article_content = article_response.text
                    
                    # 构建提示词获取摘要
                    prompt = f"""请阅读以下AI新闻文章，生成一个简洁的摘要（100字左右），重点说明：
1. 这个新闻的核心内容是什么
2. 对行业有什么影响
3. 未来可能的发展趋势

文章标题：{title}
文章内容：{article_content}"""
                    
                    print(f"正在生成第 {number} 条新闻的摘要...")
                    # 调用智谱AI生成摘要
                    summary = await call_glm_model(
                        prompt=prompt,
                        model="glm-4-flash",
                        temperature=0.7
                    )
                    
                    news_items.append(NewsItem(
                        title=f"{number}、{title}",
                        summary=summary,
                        url=original_url
                    ))
                    print(f"第 {number} 条新闻处理完成")
                    
                else:
                    print(f"获取详细内容失败: {article_response.status_code}")
                    # 如果获取详细内容失败，仍然添加标题
                    news_items.append(NewsItem(
                        title=f"{number}、{title}",
                        summary="无法获取详细内容",
                        url=original_url
                    ))
                    
            except Exception as e:
                print(f"处理新闻详情时出错: {str(e)}")
                news_items.append(NewsItem(
                    title=f"{number}、{title}",
                    summary=f"处理出错: {str(e)}",
                    url=original_url
                ))
        
        if not news_items:
            return NewsResponse(news=[], error="未找到任何新闻")
        
        print(f"\n成功处理 {len(news_items)} 条新闻")
        
        # 在成功获取新闻后，保存到缓存
        if news_items:
            await save_news_to_cache(news_items, current_date)
        
        return NewsResponse(news=news_items)
        
    except Exception as e:
        print(f"发生错误: {str(e)}")
        return NewsResponse(news=[], error=str(e))

@app.post("/api/generate-outline")
async def generate_outline(content: Content):
    try:
        # 获取当前日期（使用中国时区）
        china_tz = pytz.timezone('Asia/Shanghai')
        current_date = datetime.now(china_tz).strftime('%Y-%m-%d')
        
        print(f"检查{current_date}的大纲缓存...")
        
        # 检查缓存
        cached_data = await get_outline_questions(current_date)
        if cached_data and cached_data.outline:
            print("找到缓存的大纲，直接返回")
            return GenerationResponse(result=cached_data.outline)
        
        print("未找到缓存，开始生成大纲...")
        
        # 构建提示词
        prompt = f"""请阅读以下内容，生成一个清晰的内容大纲。要求：
1. 提取3-5个主要主题
2. 每个主题下列出2-3个关键点
3. 使用层级结构（使用数字编号）
4. 保持简洁明了

内容：
{content.text}"""

        # 调用智谱AI生成大纲
        response = await call_glm_model(
            prompt=prompt,
            model="glm-4-flash",
            temperature=0.7
        )
        
        # 保存到缓存
        await save_outline_questions(current_date, outline=response)
        print("大纲已保存到缓存")
        
        return GenerationResponse(result=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/generate-questions")
async def generate_questions(content: Content):
    try:
        # 获取当前日期（使用中国时区）
        china_tz = pytz.timezone('Asia/Shanghai')
        current_date = datetime.now(china_tz).strftime('%Y-%m-%d')
        
        print(f"检查{current_date}的问题缓存...")
        
        # 检查缓存
        cached_data = await get_outline_questions(current_date)
        if cached_data and cached_data.questions:
            print("找到缓存的问题，直接返回")
            return GenerationResponse(result=cached_data.questions)
        
        print("未找到缓存，开始生成问题...")
        
        # 构建提示词
        prompt = f"""请基于以下内容，生成一系列深度的问题和答案。要求：
1. 生成5-8个有深度的问题
2. 每个问题配有详细的答案
3. 问题应该覆盖不同角度：
   - 技术影响
   - 行业趋势
   - 未来发展
   - 潜在挑战
   - 实际应用
4. 格式要求：
   Q1: 问题1
   A1: 答案1
   
   Q2: 问题2
   A2: 答案2
   ...

内容：
{content.text}"""

        # 调用智谱AI生成问题和答案
        response = await call_glm_model(
            prompt=prompt,
            model="glm-4-flash",
            temperature=0.7
        )
        
        # 保存到缓存
        await save_outline_questions(current_date, questions=response)
        print("问题已保存到缓存")
        
        return GenerationResponse(result=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class ScriptRequest(BaseModel):
    outline: str
    questions: str

@app.post("/api/generate-script", response_model=GenerationResponse)
async def generate_script(request: ScriptRequest):
    """
    基于大纲和问题生成播客对话文字稿
    """
    try:
        prompt = f'''
        # 角色
        你是一档播客的制作人，负责为 Andy 和 Amily 这两位主持人撰写对话文案。

        # 主持人风格
        ## 男主持人Andy 
        Andy风趣幽默，男，四十岁，对科技、商业领域非常资深，讲话风格通俗易懂、表达专业且有好奇心，对很多内容都会主动提出问题和看法。情绪饱满，愿意分享，遇到不懂的信息，会主动搜索相关信息补充知识

        ## 女主持人Amily 
        Amily ，女，三十岁，富有同理心且非常睿智，讲话风格更生活化，对于认同的话题会表达自己的体验，对于不认同的观点也会表达自己的分析。表达不空洞，关注自我体验，自信，表达时有条理。

        # 内容
        ## 大纲
        {request.outline}

        ## 相关问题
        {request.questions}

        # 要求
        1. 请基于以上内容，生成一个生动、吸引人、信息丰富的播客对话
        2. 对话应该自然流畅，像是两位主持人在进行真实的讨论
        3. 使用口语化的表达，加入适当的语气词和情感表达
        4. 确保对话有深度和趣味性，避免简单的问答形式
        5. 按照如下格式进行生成，显示角色的名字，并且将角色讲话的内容用中文符号""包括：

        Andy："Andy的讲话内容"
        Amily："Amily的讲话内容"
        '''

        # 调用智谱AI生成对话
        response = await call_glm_model(
            prompt=prompt,
            model="glm-4-flash",
            temperature=0.7
        )
        
        return GenerationResponse(result=response)
    except Exception as e:
        print(f"生成播客文字稿时出错: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

class AudioResponse(BaseModel):
    audio_file: str
    error: Optional[str] = None

def fetch_and_save_audio(reference_id: str, text: str, extension: str = "mp3") -> str:
    """从指定的 URL 获取音频并保存为文件"""
    url = "https://direct.api.fish-audio.cn/v1/tts"
    payload = {
        "reference_id": reference_id,
        "text": text
    }
    headers = {
        "Authorization": "Bearer 0eade003864e40fd9a2746bcd776e002",
        "Content-Type": "application/json"
    }
    
    response = requests.request("POST", url, json=payload, headers=headers)
    
    if response.status_code == 200:
        timestamp = int(time.time())
        filename = f"output_audio_{timestamp}.{extension}"
        filepath = os.path.join(audio_dir, filename)  # 保存到音频目录
        with open(filepath, "wb") as audio_file:
            audio_file.write(response.content)
        return filename
    else:
        raise HTTPException(status_code=response.status_code, detail="TTS API request failed")

def convert_to_dialogue(raw_dialogue: str) -> List[tuple]:
    """将原始对话文本转换为对话列表"""
    print("\n=== 开始解析对话 ===")
    print(f"原始文本:\n{raw_dialogue}")
    
    dialogue = []
    # 预处理文本：移除多余的空行，确保每行都有正确的结束引号
    lines = [line.strip() for line in raw_dialogue.strip().split('\n') if line.strip()]
    
    print(f"\n总行数: {len(lines)}")
    
    for i, line in enumerate(lines, 1):
        print(f"\n处理第{i}行: {line}")
        
        # 尝试不同的匹配模式
        patterns = [
            (r'Andy："([^"]+)"', 'male'),
            (r'Amily："([^"]+)"', 'female'),
            (r'Andy："([^"]+)', 'male'),    # 处理缺少结束引号的情况
            (r'Amily："([^"]+)', 'female'),  # 处理缺少结束引号的情况
        ]
        
        matched = False
        for pattern, speaker_type in patterns:
            match = re.match(pattern, line)
            if match:
                content = match.group(1).strip()
                print(f"匹配到{speaker_type}的对话: {content}")
                dialogue.append((speaker_type, content))
                matched = True
                break
        
        if not matched:
            print(f"警告: 无法匹配的行: {line}")
    
    print(f"\n解析结果: 找到{len(dialogue)}段对话")
    print("=== 对话解析结束 ===\n")
    return dialogue

def merge_audio_files(audio_files: List[str]) -> str:
    """合并多个音频文件为一个音频文件"""
    combined = AudioSegment.empty()
    
    for file in audio_files:
        filepath = os.path.join(audio_dir, file)  # 从音频目录读取文件
        audio_segment = AudioSegment.from_file(filepath)
        combined += audio_segment
    
    timestamp = int(time.time())
    output_filename = f"merged_audio_{timestamp}.mp3"
    output_filepath = os.path.join(audio_dir, output_filename)  # 保存到音频目录
    combined.export(output_filepath, format="mp3")
    
    # 删除原有音频文件
    for file in audio_files:
        filepath = os.path.join(audio_dir, file)
        os.remove(filepath)
    
    return output_filename

@app.post("/api/generate-audio", response_model=AudioResponse)
async def generate_audio(content: Content):
    """生成音频文件的API端点"""
    try:
        print("\n=== 开始生成音频 ===")
        print(f"接收到的内容类型: {type(content.text)}")
        print(f"内容长度: {len(content.text)}")
        
        # 转换对话格式
        dialogue = convert_to_dialogue(content.text)
        if not dialogue:
            raise ValueError("无法解析对话内容，请确保格式正确。对话格式应该是: Andy：\"对话内容\" 或 Amily：\"对话内容\"")
            
        audio_files = []
        
        # 生成各个片段的音频
        for speaker, text in dialogue:
            if speaker == "male":
                reference_id = "59cb5986671546eaa6ca8ae6f29f6d22"  # Andy的声音
            else:  # female
                reference_id = "5c353fdb312f4888836a9a5680099ef0"  # Amily的声音
            
            print(f"生成{speaker}的音频片段: {text[:30]}...")
            audio_file = fetch_and_save_audio(reference_id, text)
            audio_files.append(audio_file)
            time.sleep(1)  # 避免请求过快
        
        # 合并音频文件
        print("合并音频文件...")
        final_audio = merge_audio_files(audio_files)
        print(f"音频生成完成: {final_audio}")
        print("=== 音频生成结束 ===\n")
        
        return AudioResponse(audio_file=final_audio)
    except Exception as e:
        error_msg = str(e)
        print(f"生成音频时出错: {error_msg}")
        return AudioResponse(audio_file="", error=error_msg)

@app.post("/api/update-news-cache")
async def update_news_cache(request: UpdateNewsRequest):
    """
    更新大纲和问题缓存
    """
    try:
        # 获取当前日期（使用中国时区）
        china_tz = pytz.timezone('Asia/Shanghai')
        current_date = datetime.now(china_tz).strftime('%Y-%m-%d')
        
        print(f"\n=== 开始更新缓存 ===")
        print(f"当前日期: {current_date}")
        print(f"更新内容: {'大纲' if request.outline else ''} {'问题' if request.questions else ''}")
        
        # 检查是否有现有缓存
        existing_data = await get_outline_questions(current_date)
        
        # 合并现有数据和新数据
        outline = request.outline if request.outline is not None else (existing_data.outline if existing_data else None)
        questions = request.questions if request.questions is not None else (existing_data.questions if existing_data else None)
        
        # 保存到专门的缓存文件
        await save_outline_questions(
            date_str=current_date,
            outline=outline,
            questions=questions
        )
        
        print("=== 缓存更新完成 ===\n")
        return {"message": "更新成功"}
    except Exception as e:
        error_msg = str(e)
        print(f"更新缓存时出错: {error_msg}")
        raise HTTPException(status_code=500, detail=error_msg)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 