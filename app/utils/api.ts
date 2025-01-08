import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

export async function getDailyNews() {
  try {
    const response = await axios.get(`${API_BASE_URL}/api/daily-news`);
    // 检查API返回的数据结构
    if (response.data.error) {
      console.error('API返回错误:', response.data.error);
      throw new Error(response.data.error);
    }
    
    // 确保news字段存在且是数组
    if (!response.data.news || !Array.isArray(response.data.news)) {
      console.error('API返回的数据格式不正确:', response.data);
      throw new Error('获取新闻数据失败');
    }
    
    // 将新闻数据转换为格式化的文本
    const newsItems = response.data.news;
    return newsItems.map((item: any) => 
      `${item.title}\n${item.summary}\n\n`
    ).join('');
  } catch (error) {
    console.error('Error fetching daily news:', error);
    throw error;
  }
}

export async function generateOutline(content: string) {
  try {
    const response = await axios.post(`${API_BASE_URL}/api/generate-outline`, {
      text: content
    });
    return response.data.result;
  } catch (error) {
    console.error('Error generating outline:', error);
    throw error;
  }
}

export async function generateQuestions(content: string) {
  try {
    const response = await axios.post(`${API_BASE_URL}/api/generate-questions`, {
      text: content
    });
    return response.data.result;
  } catch (error) {
    console.error('Error generating questions:', error);
    throw error;
  }
}

export async function generateScript(outline: string, questions: string) {
  try {
    const response = await axios.post(`${API_BASE_URL}/api/generate-script`, {
      outline,
      questions
    });
    return response.data.result;
  } catch (error) {
    console.error('Error generating script:', error);
    throw error;
  }
}

export async function generateAudio(text: string): Promise<string> {
  const response = await fetch('http://localhost:8000/api/generate-audio', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ text }),
  })

  if (!response.ok) {
    throw new Error('Failed to generate audio')
  }

  const data = await response.json()
  if (data.error) {
    throw new Error(data.error)
  }

  return data.audio_file  // 返回音频文件名
}

interface UpdateNewsCache {
  outline?: string;
  questions?: string;
}

export async function updateNewsCache(data: UpdateNewsCache) {
  try {
    const response = await axios.post(`${API_BASE_URL}/api/update-news-cache`, data);
    return response.data;
  } catch (error) {
    console.error('Error updating news cache:', error);
    throw error;
  }
} 