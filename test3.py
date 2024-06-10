import re

test = "  Duration: 00:47:52.36, start: 0.118000, bitrate: 0 kb/s"

f = re.findall(r"Duration: (\d{2}:\d{2}:\d{2})", test)

print(f)