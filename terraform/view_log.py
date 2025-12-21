
import sys
import re

fname = sys.argv[1]
with open(fname, 'rb') as f:
    content = f.read().decode('utf-8', errors='ignore')

clean_content = re.sub(r'\r', '\n', content)

errors = [line for line in clean_content.split('\n') if "Error" in line or "400" in line]
for line in errors:
    # Split line into 100 char chunks
    for i in range(0, len(line), 100):
        print(line[i:i+100])
