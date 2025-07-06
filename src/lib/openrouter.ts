const OPENROUTER_API_KEY = import.meta.env.VITE_OPENROUTER_API_KEY;
const OPENROUTER_BASE_URL = 'https://openrouter.ai/api/v1/chat/completions';

export interface ChatMessage {
  role: 'user' | 'assistant' | 'system';
  content: string;
}

export async function queryDeepSeekAI(messages: ChatMessage[]): Promise<string> {
  try {
    const response = await fetch(OPENROUTER_BASE_URL, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${OPENROUTER_API_KEY}`,
        'Content-Type': 'application/json',
        'HTTP-Referer': window.location.origin,
        'X-Title': 'InsightIQ BI Platform'
      },
      body: JSON.stringify({
        model: 'deepseek/deepseek-r1-0528:free',
        messages: messages,
        temperature: 0.7,
        max_tokens: 4000
      })
    });

    if (!response.ok) {
      throw new Error(`OpenRouter API error: ${response.status}`);
    }

    const data = await response.json();
    return data.choices[0]?.message?.content || 'Unable to process request';
  } catch (error) {
    console.error('DeepSeek AI query error:', error);
    throw new Error('Failed to query AI assistant');
  }
}

export async function analyzeDataWithAI(csvData: string, fileName: string): Promise<{
  dataDictionary: any;
  validationRules: any;
  insights: string;
  recommendations: string;
}> {
  const messages: ChatMessage[] = [
  {
    role: 'system',
    content: `You are InsightIQ, an expert business intelligence analyst. Analyze the provided CSV data and return a JSON response with:
      1. dataDictionary: Object with column names as keys and descriptions as values
      2. validationRules: Object with column names as keys and validation rules as values
      3. insights: String with key insights and patterns found
      4. recommendations: String with recommendations for data quality improvements
      
      Respond only with valid JSON.`
  },
  {
    role: 'user',
    content: `Please analyze this CSV data from file "${fileName}":\n\n${csvData.slice(0, 3000)}...`
  }];


  try {
    const response = await queryDeepSeekAI(messages);

    // Try to extract JSON from response
    const jsonMatch = response.match(/\{[\s\S]*\}/);
    if (jsonMatch) {
      return JSON.parse(jsonMatch[0]);
    }

    // Fallback response
    return {
      dataDictionary: {},
      validationRules: {},
      insights: response,
      recommendations: 'Please review the data quality and consider implementing validation rules.'
    };
  } catch (error) {
    console.error('AI analysis error:', error);
    throw new Error('Failed to analyze data with AI');
  }
}