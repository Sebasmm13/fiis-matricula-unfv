import json

transcript_path = r'C:\Users\luisa\.gemini\antigravity-ide\brain\1c84b87e-0b85-461f-ac27-03f171a4fa61\.system_generated\logs\transcript_full.jsonl'

print('Analyzing transcript...')
modifications = []

with open(transcript_path, 'r', encoding='utf-8') as f:
    for line in f:
        try:
            step = json.loads(line)
            if step.get('type') == 'PLANNER_RESPONSE':
                for tool in step.get('tool_calls', []):
                    name = tool.get('name')
                    args = tool.get('args', {})
                    if name in ['replace_file_content', 'multi_replace_file_content', 'write_to_file']:
                        target = args.get('TargetFile', '')
                        if 'App.tsx' in target or 'views.py' in target:
                            modifications.append({
                                'step': step.get('step_index'),
                                'tool': name,
                                'file': target,
                                'time': step.get('created_at')
                            })
                    elif name == 'run_command':
                        cmd = args.get('CommandLine', '')
                        if 'App.tsx' in cmd or 'views.py' in cmd:
                            # Might be a python script that overwrote it
                            if 'with open' in cmd and "'w'" in cmd:
                                modifications.append({
                                    'step': step.get('step_index'),
                                    'tool': 'run_command (python overwrite)',
                                    'file': 'App.tsx / views.py',
                                    'time': step.get('created_at')
                                })
        except Exception as e:
            pass

for mod in modifications:
    print(f"Step {mod['step']} at {mod['time']}: {mod['tool']} on {mod['file']}")
