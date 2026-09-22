import asyncio
from pathlib import Path
import subprocess
import tempfile
import edge_tts
import imageio_ffmpeg

ROOT = Path(__file__).resolve().parent.parent
VOICE, RATE, PITCH = "en-US-AnaNeural", "-10%", "+2Hz"
letters = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
sound_pairs = dict(zip(letters, [
    ("apple", "ant"), ("ball", "bear"), ("cat", "cup"), ("dog", "duck"),
    ("egg", "elephant"), ("fish", "fox"), ("goat", "grapes"), ("hat", "horse"),
    ("igloo", "insect"), ("jellyfish", "jump"), ("kite", "kitten"), ("lion", "leaf"),
    ("moon", "mouse"), ("nest", "nose"), ("octopus", "olive"), ("pig", "pizza"),
    ("queen", "quilt"), ("rainbow", "rabbit"), ("sun", "sock"), ("turtle", "tiger"),
    ("umbrella", "up"), ("van", "violin"), ("whale", "wagon"), ("fox", "box"),
    ("yo-yo", "yarn"), ("zebra", "zipper"),
]))

def lesson_parts(letter):
    opening = f"Look! Big {letter}, and little {letter.lower()}!"
    if letter == "X":
        listening = "Listen to fox. Fox. Now box. Box."
        teaching = "They end with the same sound. Can you hear it?"
    elif letter == "V":
        listening = "Listen to van. Van."
        teaching = "Put your top teeth on your lower lip, and feel the buzz. Violin starts the same way!"
    else:
        word, other = sound_pairs[letter]
        listening = f"Listen to {word}. {word}. Now {other}. {other}."
        teaching = "They start with the same sound. Can you hear it?"
    return [
        (opening, "+3%", "+6Hz"),
        (listening, "-16%", "+1Hz"),
        (teaching, "-8%", "+4Hz"),
        (question(letter), "-6%", "+5Hz"),
    ]

def question(letter):
    prompt = "Which picture ends like fox?" if letter == "X" else f"Which picture starts like {sound_pairs[letter][0]}?"
    return f"{prompt} Tap each picture to hear its name. Then press the check."

async def create(path, text, gate, rate=RATE, pitch=PITCH):
    async with gate:
        path.parent.mkdir(parents=True, exist_ok=True)
        await edge_tts.Communicate(text, VOICE, rate=rate, pitch=pitch).save(str(path))

async def create_lesson(letter, gate):
    output = ROOT / f"audio/lessons/{letter.lower()}.mp3"
    with tempfile.TemporaryDirectory(prefix="family-lesson-") as temp:
        parts = []
        for index, (text, rate, pitch) in enumerate(lesson_parts(letter)):
            segment = Path(temp) / f"part-{index}.mp3"
            await create(segment, text, gate, rate, pitch)
            parts.append(segment)
        command = [imageio_ffmpeg.get_ffmpeg_exe(), "-hide_banner", "-loglevel", "error", "-y"]
        for part in parts:
            command += ["-i", str(part)]
        command += ["-filter_complex", f"concat=n={len(parts)}:v=0:a=1[out]", "-map", "[out]", "-codec:a", "libmp3lame", "-b:a", "96k", str(output)]
        subprocess.run(command, check=True)

async def main():
    gate, clips = asyncio.Semaphore(6), []
    for letter in letters:
        lower = letter.lower()
        clips += [
            create_lesson(letter, gate),
            create(ROOT / f"audio/questions/{lower}.mp3", question(letter), gate, "+1%", "+6Hz"),
        ]
    clips += [
        create(ROOT / "audio/feedback/correct.mp3", "Yes! You got it! Great listening!", gate, "+5%", "+8Hz"),
        create(ROOT / "audio/feedback/again.mp3", "Almost! Listen to the sound again. Then try another picture.", gate, "-10%", "+2Hz"),
        create(ROOT / "audio/feedback/choose.mp3", "Choose a picture first.", gate, "-5%", "+3Hz"),
    ]
    await asyncio.gather(*clips)

if __name__ == "__main__":
    asyncio.run(main())
