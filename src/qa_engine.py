import os
import sqlite3
from src.config_loader import get_config

class PMEQueryEngine:
    def __init__(self):
        self.config = get_config()
        self.db_cfg = self.config.get("database", {})
        self.llm_cfg = self.config.get("llm", {})
        
        self.cleaned_db = self.db_cfg.get("cleaned_db")
        self.provider = self.llm_cfg.get("provider", "openai")
        self.model = self.llm_cfg.get("model", "gpt-4o-mini")
        self.temperature = self.llm_cfg.get("temperature", 0.2)

    def retrieve_context(self, query, limit=5):
        if not os.path.exists(self.cleaned_db):
            raise FileNotFoundError(f"Cleaned memory database not found at {self.cleaned_db}. Please run cleaner first.")
            
        conn = sqlite3.connect(self.cleaned_db)
        cursor = conn.cursor()

        cursor.execute("PRAGMA table_info(cleaned_memories)")
        columns = {row[1] for row in cursor.fetchall()}
        has_enriched_columns = {"cleaned_text", "ocr_quality_score", "content_kind"}.issubset(columns)
        
        if has_enriched_columns:
            sql = """
            SELECT
                m.timestamp,
                m.app_name,
                m.window_title,
                m.ocr_text,
                m.cleaned_text,
                m.ocr_quality_score,
                m.content_kind,
                m.trigger_reason,
                m.focused
            FROM cleaned_memories_fts fts
            JOIN cleaned_memories m ON m.id = fts.id
            WHERE cleaned_memories_fts MATCH ?
            ORDER BY rank ASC
            LIMIT ?
            """
        else:
            sql = """
            SELECT
                m.timestamp,
                m.app_name,
                m.window_title,
                m.ocr_text,
                m.ocr_text AS cleaned_text,
                NULL AS ocr_quality_score,
                NULL AS content_kind,
                m.trigger_reason,
                m.focused
            FROM cleaned_memories_fts fts
            JOIN cleaned_memories m ON m.id = fts.id
            WHERE cleaned_memories_fts MATCH ?
            ORDER BY rank ASC
            LIMIT ?
            """
        
        # Simple FTS5 query parser
        keywords = " OR ".join([f'"{w}"' for w in query.split() if w.strip()])
        if not keywords:
            conn.close()
            return []
            
        try:
            cursor.execute(sql, (keywords, limit))
            rows = cursor.fetchall()
        except sqlite3.OperationalError:
            # Fallback to simple LIKE query
            fallback_sql = """
            SELECT timestamp, app_name, window_title, ocr_text,
                   COALESCE(cleaned_text, ocr_text) AS cleaned_text,
                   ocr_quality_score, content_kind, trigger_reason, focused
            FROM cleaned_memories
            WHERE ocr_text LIKE ? OR COALESCE(cleaned_text, '') LIKE ? OR app_name LIKE ? OR window_title LIKE ?
            ORDER BY timestamp DESC
            LIMIT ?
            """
            pattern = f"%{query}%"
            if has_enriched_columns:
                cursor.execute(fallback_sql, (pattern, pattern, pattern, pattern, limit))
            else:
                fallback_sql = """
                SELECT timestamp, app_name, window_title, ocr_text,
                       ocr_text AS cleaned_text, NULL AS ocr_quality_score, NULL AS content_kind,
                       trigger_reason, focused
                FROM cleaned_memories
                WHERE ocr_text LIKE ? OR app_name LIKE ? OR window_title LIKE ?
                ORDER BY timestamp DESC
                LIMIT ?
                """
                cursor.execute(fallback_sql, (pattern, pattern, pattern, limit))
            rows = cursor.fetchall()
            
        conn.close()
        return rows

    def format_prompt(self, query, rows):
        if not rows:
            return None, "未找到任何与该查询相关的屏幕 OCR 历史上下文。"
            
        blocks = []
        for i, row in enumerate(rows):
            ts, app, title, raw_text, cleaned_text, quality, kind, reason, focused = row
            status = "活动窗口" if focused else "后台窗口"
            # Format text snippet
            text_for_prompt = cleaned_text or raw_text or ""
            lines = [line.strip() for line in text_for_prompt.split("\n") if line.strip()]
            clean_text = "\n  ".join(lines[:15])
            if len(lines) > 15:
                clean_text += "\n  ... [其余内容已被截断]"
            meta = []
            if kind:
                meta.append(f"内容类型: {kind}")
            if quality is not None:
                meta.append(f"OCR质量: {quality}")
                
            block = (
                f"快照记录 #{i+1}\n"
                f"时间: {ts} ({status})\n"
                f"软件: {app} | 窗口: {title}\n"
                f"触发: {reason}\n"
                f"{' | '.join(meta)}\n"
                f"内容:\n  {clean_text}\n"
                f"--------------------------------------------------"
            )
            blocks.append(block)
            
        context_str = "\n".join(blocks)
        
        prompt = f"""你是一个个人数字助理。你的记忆库中包含用户在过去几天的电脑屏幕 OCR 清洗记录。
请根据以下为您召回的【历史屏幕OCR上下文】来客观、真实地回答用户的问题。如果上下文中找不到对应内容，请坦率地告知，严禁胡乱捏造事实。

【用户的问题】
{query}

【历史屏幕OCR上下文】
--------------------------------------------------
{context_str}

【你的回答】
"""
        return context_str, prompt

    def ask(self, query, limit=5, ask_llm=False):
        rows = self.retrieve_context(query, limit)
        context_str, prompt = self.format_prompt(query, rows)
        
        result = {
            "rows": rows,
            "prompt": prompt,
            "answer": None
        }
        
        if ask_llm and rows:
            # Load litellm
            try:
                import litellm
            except ImportError:
                print("\n[提示] 未检测到 litellm 依赖包，请先运行 setup.sh 进行环境初始化。")
                return result
                
            # Deduce model provider
            llm_model = self.model
            providers = ["OPENAI_API_KEY", "DEEPSEEK_API_KEY", "ZHIPU_AI_KEY", "ANTHROPIC_API_KEY", "GEMINI_API_KEY"]
            has_key = any(k in os.environ for k in providers)
            
            if not has_key:
                print("\n[提示] 环境变量中未检测到 LLM API Key (如 OPENAI_API_KEY 或 DEEPSEEK_API_KEY)。")
                print("已为您跳过大模型调用。您可以直接复制 CLI 打印的 Prompt 去任意聊天框进行问答。")
                return result
                
            if "DEEPSEEK_API_KEY" in os.environ and "deepseek" not in llm_model:
                llm_model = "deepseek/deepseek-chat"
            elif "ZHIPU_AI_KEY" in os.environ and "zhipu" not in llm_model:
                llm_model = "zhipu/glm-4"
            elif "GEMINI_API_KEY" in os.environ and "gemini" not in llm_model:
                llm_model = "gemini/gemini-pro"
                
            print(f"正在通过 litellm 调用 {llm_model} 模型进行问答推理...")
            try:
                response = litellm.completion(
                    model=llm_model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=self.temperature
                )
                answer = response.choices[0].message.content
                result["answer"] = answer
            except Exception as e:
                print(f"大模型调用失败: {e}")
                
        return result
