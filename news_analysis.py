import streamlit as st
import os
from llm_helper import get_llm_helper


def main():
    st.title('📣 News & Social Listening (Chinese Analysis)')
    st.write('Enter a topic keyword or paste a news/video/article URL. The app will fetch (via LLM) a summary, key companies mentioned, and potential financial impact.')

    query = st.text_input('Topic / URL / Keyword', value='春晚 机器 人 Unitree 病毒 视频')
    top_n = st.slider('How many items to analyse (approx.)', 1, 5, 3)

    if st.button('🔎 Analyse'):
        if not query.strip():
            st.error('Please enter a query or URL')
            return

        with st.spinner('Contacting LLM for analysis...'):
            try:
                api_key = os.environ.get('OPENROUTER_API_KEY') or os.environ.get('DEEPSEEK_API_KEY')
                llm = get_llm_helper(api_key)

                prompt = f"""
你是一位能閱讀最新熱點、擅長中文評論與財經風險分析的助理。
請根據以下關鍵字或連結: "{query}" ，列出大約 {top_n} 個最相關的熱門文章/影片/直播標題（假設目前網路熱度高），
對每一條給出：
1) 中文摘要（簡短2-3句）
2) 涉及的公司或組織（以短句列出）
3) 對相關公司股價或金融產品的潛在影響評估（簡短：正面/中性/負面，並說明原因）
4) 若要追蹤此事件，建議監控哪些關鍵詞或指標（最多3項）

請用中文回覆，條列清晰，保持簡潔（每項不超過 5 行）。
"""

                response = llm.client.chat.completions.create(
                    extra_headers={"HTTP-Referer": "http://localhost:8501", "X-Title": "News Analysis"},
                    model=llm.model,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=800,
                    temperature=0.2,
                )

                text = response.choices[0].message.content.strip()
                st.markdown('---')
                st.subheader('分析結果（中文）')
                st.code(text, language='text')

            except Exception as e:
                st.error(f'分析失敗：{e}')


if __name__ == '__main__':
    main()
