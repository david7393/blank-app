import streamlit as st
import os
import json
from llm_helper import get_llm_helper


def parse_news_items(news_text):
    """Parse the news text into structured items with checkboxes."""
    # Try to create structured news items data
    items = []
    
    # For demo purposes, we'll create structured items with mock URLs
    # In a real app, you'd parse the LLM response more carefully
    lines = news_text.split('\n')
    current_item = {}
    item_num = 1
    
    for line in lines:
        if '**標題**' in line:
            if current_item:
                items.append(current_item)
            current_item = {'id': item_num, 'title': line.split('**標題**')[1].strip() if '**標題**' in line else ''}
            item_num += 1
        elif '**媒體/來源**' in line:
            current_item['source'] = line.split('**媒體/來源**')[1].strip() if '**媒體/來源**' in line else ''
        elif '**熱度指數**' in line:
            current_item['heat'] = line.split('**熱度指數**')[1].strip() if '**熱度指數**' in line else ''
        elif '**簡介**' in line:
            current_item['description'] = line.split('**簡介**')[1].strip() if '**簡介**' in line else ''
        elif '**涉及公司/個人/組織**' in line:
            current_item['companies'] = line.split('**涉及公司/個人/組織**')[1].strip() if '**涉及公司/個人/組織**' in line else ''
    
    if current_item:
        items.append(current_item)
    
    # Generate mock URLs for news items
    for item in items:
        # Create a simple mock URL based on title
        title_slug = item.get('title', f'news-{item["id"]}').lower()[:40].replace(' ', '-')
        item['url'] = f"https://news-example.com/article/{item['id']}-{title_slug}"
    
    return items


def main():
    st.title('📣 News & Social Listening (Chinese Analysis)')
    
    # Create two tabs: one for trending news, one for custom analysis
    tab1, tab2 = st.tabs(["📈 Trending (Last 7 Days)", "🔍 Custom Analysis"])
    
    # -------  TAB 1: Trending News -------
    with tab1:
        st.subheader("🔥 Top 10 Most Popular News/Articles/Videos (Last 7 Days)")
        
        if st.button('📰 Fetch Top 10 Trending Items', key='fetch_trending'):
            with st.spinner('Fetching trending items...'):
                try:
                    api_key = os.environ.get('OPENROUTER_API_KEY') or os.environ.get('DEEPSEEK_API_KEY')
                    llm = get_llm_helper(api_key)
                    
                    prompt = """你是一位掌握最新熱點新聞、社交媒體趨勢與網路輿論的專家助理。
請根據過去7天（包括今天）的全球與中文媒體、社交媒體趨勢，列出大約10個最受關注與最熱門的新聞/文章/影片/話題。

對每一項請提供以下信息（用標準化格式，每項之間用---分隔）：

1. **標題**: [新聞/文章/影片標題]
2. **媒體/來源**: [媒體名稱或社交平台]
3. **熱度指數**: [1-10 分，代表受關注程度]
4. **簡介**: [2-3句的簡短摘要，說明發生什麼事]
5. **涉及公司/個人/組織**: [列出相關的主要方]

---"""
                    
                    response = llm.client.chat.completions.create(
                        extra_headers={"HTTP-Referer": "http://localhost:8501", "X-Title": "News Analysis"},
                        model=llm.model,
                        messages=[{"role": "user", "content": prompt}],
                        max_tokens=2000,
                        temperature=0.3,
                    )
                    
                    trending_text = response.choices[0].message.content.strip()
                    
                    # Parse into structured items
                    news_items = parse_news_items(trending_text)
                    
                    # Store in session state for later use
                    st.session_state.trending_news = trending_text
                    st.session_state.news_items = news_items
                    st.session_state.selected_news_ids = {}
                    
                except Exception as e:
                    st.error(f'獲取熱門話題失敗：{e}')
        
        # Show stored trending news with checkboxes if available
        if "news_items" in st.session_state:
            st.markdown("### 📋 熱門話題清單 - 點擊標題開啟原始連結")
            
            # Initialize selection state if not exists
            if "selected_news_ids" not in st.session_state:
                st.session_state.selected_news_ids = {}
            
            # Display news items with checkboxes and clickable URLs
            for item in st.session_state.news_items:
                col1, col2, col3 = st.columns([0.5, 2, 0.5])
                
                with col1:
                    # Checkbox for selection
                    is_selected = st.checkbox(
                        f"選擇 #{item['id']}", 
                        key=f"news_select_{item['id']}",
                        value=st.session_state.selected_news_ids.get(item['id'], False)
                    )
                    st.session_state.selected_news_ids[item['id']] = is_selected
                
                with col2:
                    # News item content with clickable link
                    title = item.get('title', f'News #{item["id"]}')
                    url = item.get('url', '#')
                    source = item.get('source', 'Unknown')
                    heat = item.get('heat', 'N/A')
                    
                    st.markdown(f"**[🔗 {title}]({url})**")
                    st.caption(f"📰 {source} | 🔥 {heat}")
                    st.write(item.get('description', ''))
                    st.write(f"**相關方**: {item.get('companies', '無')}")
                
                st.divider()
            
            # Show analysis section if any news is selected
            selected_items = [item for item in st.session_state.news_items 
                            if st.session_state.selected_news_ids.get(item['id'], False)]
            
            if selected_items:
                st.markdown("---")
                st.markdown("### 📊 查看選定新聞對金融的影響")
                
                selected_news_text = "\n\n".join([
                    f"**{item['title']}** ({item['source']})\n{item['description']}\n相關方: {item['companies']}"
                    for item in selected_items
                ])
                
                if st.button('💹 分析財經影響', key='analyze_impact'):
                    with st.spinner('分析財經影響中...'):
                        try:
                            api_key = os.environ.get('OPENROUTER_API_KEY') or os.environ.get('DEEPSEEK_API_KEY')
                            llm = get_llm_helper(api_key)
                            
                            prompt = f"""你是一位資深的金融分析專家，擅長評估新聞事件對各類金融產品的潛在影響。

請根據以下 {len(selected_items)} 個新聞內容分析對金融市場的影響：

【新聞內容】
{selected_news_text}

請從以下角度進行分析：

1. **對列舉公司股價的潛在影響**:
   - 直接受益或受害的公司（列出2-5家）
   - 對每家公司的影響評估（正面/中性/負面）
   - 簡短說明原因（1-2句）

2. **對主要金融產品的影響**:
   - 貴金屬（黃金/白銀）: 影響評估 + 原因
   - 主要指數（恆生指數/滬深300/納斯達克等）: 影響評估 + 原因
   - 能源商品（石油/天然氣）: 影響評估 + 原因
   - 匯率走勢: 影響評估 + 原因

3. **風險評估**:
   - 事件發展的幾種可能情境及其金融影響
   - 關鍵監控指標（3-5項）

用清晰的中文回覆，保持簡潔（總共不超過 1000 字）。"""
                            
                            response = llm.client.chat.completions.create(
                                extra_headers={"HTTP-Referer": "http://localhost:8501", "X-Title": "Financial Impact Analysis"},
                                model=llm.model,
                                messages=[{"role": "user", "content": prompt}],
                                max_tokens=1500,
                                temperature=0.2,
                            )
                            
                            impact_analysis = response.choices[0].message.content.strip()
                            
                            st.markdown("---")
                            st.markdown("### 💰 財經影響分析結果")
                            st.markdown(impact_analysis)
                            
                        except Exception as e:
                            st.error(f'財經影響分析失敗：{e}')
    
    # ------- TAB 2: Custom Analysis -------
    with tab2:
        st.subheader("🔎 自訂新聞/話題分析")
        st.write('輸入一個話題關鍵字或貼上新聞/影片/文章URL，AI 將為您進行分析和財經影響評估。')
        
        query = st.text_input('話題 / URL / 關鍵字 / 新聞標題', value='')
        top_n = st.slider('分析相關項目數量（約）', 1, 5, 3)

        if st.button('🔎 開始分析', key='custom_analyze'):
            if not query.strip():
                st.error('請輸入查詢內容')
                return

            with st.spinner('正在聯繫 LLM 進行分析...'):
                try:
                    api_key = os.environ.get('OPENROUTER_API_KEY') or os.environ.get('DEEPSEEK_API_KEY')
                    llm = get_llm_helper(api_key)

                    prompt = f"""你是一位能閱讀最新熱點、擅長中文評論與財經風險分析的助理。
請根據以下關鍵字或連結: "{query}" ，列出大約 {top_n} 個最相關的熱門文章/影片/直播標題（假設目前網路熱度高），
對每一條給出：
1) 中文摘要（簡短2-3句）
2) 涉及的公司或組織（以短句列出）
3) 對相關公司股價或金融產品的潛在影響評估（簡短：正面/中性/負面，並說明原因）
4) 若要追蹤此事件，建議監控哪些關鍵詞或指標（最多3項）

請用中文回覆，條列清晰，保持簡潔（每項不超過 5 行）。"""

                    response = llm.client.chat.completions.create(
                        extra_headers={"HTTP-Referer": "http://localhost:8501", "X-Title": "News Analysis"},
                        model=llm.model,
                        messages=[{"role": "user", "content": prompt}],
                        max_tokens=1000,
                        temperature=0.2,
                    )

                    text = response.choices[0].message.content.strip()
                    st.markdown('---')
                    st.subheader('📊 分析結果（中文）')
                    st.markdown(text)

                except Exception as e:
                    st.error(f'分析失敗：{e}')


if __name__ == '__main__':
    main()
