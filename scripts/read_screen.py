import json, re, sys

# 用法: python scripts/read_screen.py <output.json文件> [尾部字符数]
path = sys.argv[1]
tail = int(sys.argv[2]) if len(sys.argv) > 2 else 2200
d = json.load(open(path, encoding='utf-8', errors='replace'))
txt = d.get('output', '')
txt = txt.replace('\x1b[?2026l', '').replace('\x1b[?2026h', '')
txt = re.sub(r'\x1b\][^\x07]*?\x07', '', txt)
txt = re.sub(r'\x1b\[[0-9;?]*[A-Za-z]', '', txt)
keep = [ch for ch in txt if (32 <= ord(ch) < 127) or '一' <= ch <= '鿿']
cleaned = ''.join(keep)
sys.stdout.buffer.write(cleaned[-tail:].encode('utf-8'))
