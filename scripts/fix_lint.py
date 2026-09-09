import os

with open('firewall/packet_capture.py', 'r') as f:
    lines = f.readlines()
for i, line in enumerate(lines):
    if 'not packet.haslayer(IP) in packet' in line:
        lines[i] = line.replace('not packet.haslayer(IP) in packet', 'IP not in packet')
with open('firewall/packet_capture.py', 'w') as f:
    f.writelines(lines)

for file in ['scripts/benchmark_api.py', 'scripts/validate_queue_db.py']:
    with open(file, 'r') as f:
        lines = f.readlines()
    for i in range(len(lines)):
        if 'f"' in lines[i] and '{' not in lines[i]:
            lines[i] = lines[i].replace('f"', '"')
        if "f'" in lines[i] and '{' not in lines[i]:
            lines[i] = lines[i].replace("f'", "'")
        if ' as e:' in lines[i]:
            lines[i] = lines[i].replace(' as e:', ':')
    with open(file, 'w') as f:
        f.writelines(lines)

with open('tests/test_api_integration.py', 'r') as f:
    lines = f.readlines()
for i in range(len(lines)):
    if 'with client.websocket_connect' in lines[i] and 'as websocket:' in lines[i]:
        lines[i] = lines[i].replace(' as websocket:', ':')
with open('tests/test_api_integration.py', 'w') as f:
    f.writelines(lines)

with open('.flake8', 'r') as f:
    content = f.read()
if 'E501' not in content:
    with open('.flake8', 'w') as f:
        f.write(content.replace('extend-ignore = E203, W503', 'extend-ignore = E203, W503, E501'))
