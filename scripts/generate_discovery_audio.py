import asyncio
import json
import re
from pathlib import Path

import edge_tts

ROOT = Path(__file__).resolve().parent.parent
html = (ROOT / "index.html").read_text()
match = re.search(r'<script type="application/json" id="fp-discoveries">([\s\S]*?)</script>', html)
if not match:
    raise RuntimeError("Discovery content was not found in index.html")
discoveries = json.loads(match.group(1))

async def create(theme, day, entry, gate):
    async with gate:
        path = ROOT / "audio" / "discoveries" / f"{theme}-{day}.mp3"
        path.parent.mkdir(parents=True, exist_ok=True)
        spoken = f"Wow! Did you know? {entry['fact']} Now, try this! {entry['try']}"
        await edge_tts.Communicate(spoken, "en-US-AnaNeural", rate="-3%", pitch="+6Hz").save(str(path))

async def main():
    gate = asyncio.Semaphore(6)
    await asyncio.gather(*(create(theme["key"], day, entry, gate)
                           for theme in discoveries
                           for day, entry in enumerate(theme["days"])))

if __name__ == "__main__":
    asyncio.run(main())
