import json
import sys

transcript_path = r'C:\Users\luisa\.gemini\antigravity-ide\brain\1c84b87e-0b85-461f-ac27-03f171a4fa61\.system_generated\logs\transcript_full.jsonl'

with open(transcript_path, 'r', encoding='utf-8') as f:
    for line in f:
        try:
            step = json.loads(line)
            if step.get('step_index') == 1663:
                for tool in step.get('tool_calls', []):
                    if tool.get('name') == 'replace_file_content':
                        args = tool.get('args', {})
                        print(f"--- REPLACE IN {args.get('TargetFile')} ---")
                        print(args.get('ReplacementContent')[:500])
                        print("...")
                        
        except Exception:
            pass

