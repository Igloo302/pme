import os
import sys
import sqlite3
import argparse

def parse_args():
    parser = argparse.ArgumentParser(description="PME-OCR Cleaned Memories AI Q&A Context Retriever")
    parser.add_argument(
        "query",
        type=str,
        help="The search query or question (e.g., 'Aura项目')"
    )
    parser.add_argument(
        "--db",
        default=os.path.expanduser("~/Documents/antigravity/wonderful-nobel/active_window_ocr_demo/pme_cleaned_memories.db"),
        help="Path to the cleaned SQLite database"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=5,
        help="Maximum number of context entries to retrieve"
    )
    parser.add_argument(
        "--ask",
        action="store_true",
        help="Try to call LLM (requires OPENAI_API_KEY, DEEPSEEK_API_KEY, or similar in env)"
    )
    return parser.parse_args()

def retrieve_context(db_path, query, limit):
    if not os.path.exists(db_path):
        print(f"Cleaned database not found at: {db_path}. Please run ocr_cleaner.py first.")
        sys.exit(1)
        
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Perform FTS5 search
    # We select timestamp, app_name, window_title, ocr_text, trigger_reason, and rank
    sql = """
    SELECT 
        m.timestamp, 
        m.app_name, 
        m.window_title, 
        m.ocr_text, 
        m.trigger_reason, 
        m.focused
    FROM cleaned_memories_fts fts
    JOIN cleaned_memories m ON m.id = fts.id
    WHERE cleaned_memories_fts MATCH ?
    ORDER BY rank ASC
    LIMIT ?
    """
    
    # Simple query formatting for FTS5 (escape special chars, join with OR/AND or just pass as-is)
    # FTS5 works well with space-separated keywords
    keywords = " OR ".join([f'"{w}"' for w in query.split() if len(w) > 0])
    
    try:
        cursor.execute(sql, (keywords, limit))
        rows = cursor.fetchall()
    except sqlite3.OperationalError as e:
        # Fallback to simple matching if FTS5 syntax fails
        print(f"FTS5 matching failed, falling back to simple query: {e}")
        fallback_sql = """
        SELECT timestamp, app_name, window_title, ocr_text, trigger_reason, focused
        FROM cleaned_memories
        WHERE ocr_text LIKE ? OR app_name LIKE ?
        ORDER BY timestamp DESC
        LIMIT ?
        """
        cursor.execute(fallback_sql, (f"%{query}%", f"%{query}%", limit))
        rows = cursor.fetchall()
        
    conn.close()
    return rows

def format_context_prompt(query, rows):
    if not rows:
        return None, "未找到相关的历史屏幕记录上下文。"
        
    context_blocks = []
    for i, row in enumerate(rows):
        ts, app, title, text, reason, focused = row
        focus_status = "活动窗口" if focused else "后台窗口"
        # Clean text line breaks for display
        clean_text = "\n  ".join([line.strip() for line in text.split("\n") if line.strip()][:15])
        if len(text.split("\n")) > 15:
            clean_text += "\n  ... [文字已截断]"
            
        block = (
            f"记录 #{i+1}\n"
            f"时间戳: {ts} ({focus_status})\n"
            f"应用名称: {app} | 窗口标题: {title}\n"
            f"触发原因: {reason}\n"
            f"屏幕内容:\n  {clean_text}\n"
            f"--------------------------------------------------"
        )
        context_blocks.append(block)
        
    context_str = "\n".join(context_blocks)
    
    prompt = f"""你是一个数字永生/记忆检索AI助手。你拥有用户在过去几天的电脑屏幕OCR历史记录（以下已为您提取了与问题最相关的上下文）。
请仔细阅读以下屏幕记录，并客观、精炼、准确地回答用户的问题。如果上下文中没有提到相关信息，请如实告知。

【用户的问题】
{query}

【历史屏幕OCR上下文】
--------------------------------------------------
{context_str}

【你的回答】
"""
    return context_str, prompt

def call_llm(prompt):
    try:
        import litellm
    except ImportError:
        print("\n[提示] 未检测到 litellm 库，无法自动调用大模型。")
        print("请在环境变量中设置 API KEY 并运行: pip install litellm")
        return
        
    # Check if there is any API key in environment
    providers = ["OPENAI_API_KEY", "DEEPSEEK_API_KEY", "ZHIPU_AI_KEY", "ANTHROPIC_API_KEY", "GEMINI_API_KEY"]
    has_key = any(k in os.environ for k in providers)
    if not has_key:
        print("\n[提示] 未在环境变量中检测到 API Key (如 OPENAI_API_KEY 或 DEEPSEEK_API_KEY)。")
        print("您也可以手动将下方生成的 Prompt 复制到任意 AI 聊天框中进行问答。")
        return
        
    # We will pick model based on available keys
    model = "gpt-4o-mini" # Default
    if "DEEPSEEK_API_KEY" in os.environ:
        model = "deepseek/deepseek-chat"
    elif "ZHIPU_AI_KEY" in os.environ:
        model = "zhipu/glm-4"
    elif "GEMINI_API_KEY" in os.environ:
        model = "gemini/gemini-pro"
        
    print(f"\n正在使用 {model} 进行 AI 问答推理...")
    try:
        response = litellm.completion(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2
        )
        answer = response.choices[0].message.content
        print("\n" + "="*50)
        print("AI 问答回答：")
        print("="*50)
        print(answer)
        print("="*50 + "\n")
    except Exception as e:
        print(f"大模型调用失败: {e}")

def main():
    args = parse_args()
    
    print(f"检索与 '{args.query}' 相关的上下文记录...")
    rows = retrieve_context(args.db, args.query, args.limit)
    
    context_str, prompt = format_context_prompt(args.query, rows)
    
    print(f"\n成功匹配到 {len(rows)} 条最相关的屏幕快照。")
    print("\n" + "="*50)
    print("提取的上下文概要：")
    print("="*50)
    for i, row in enumerate(rows):
        ts, app, title, _, reason, focused = row
        focus_status = "活动" if focused else "后台"
        print(f"[{ts}] {app} - {title} ({focus_status} | 触发: {reason})")
    print("="*50)
    
    print("\n" + "="*50)
    print("为 AI 生成的 RAG Prompt：")
    print("="*50)
    print(prompt)
    print("="*50)
    
    if args.ask:
        call_llm(prompt)

if __name__ == "__main__":
    main()
