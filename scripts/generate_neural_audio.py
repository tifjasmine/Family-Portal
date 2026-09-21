import asyncio
from pathlib import Path
import subprocess
import tempfile
import edge_tts
import imageio_ffmpeg

ROOT = Path(__file__).resolve().parent.parent
VOICE, RATE, PITCH = "en-US-AnaNeural", "-10%", "+2Hz"
letters = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
vowels = {
    "A":("ay","acorn","aaa","apple and ant"), "E":("ee","eagle","eh","egg and elephant"),
    "I":("eye","ice cream","ih","igloo and insect"), "O":("oh","ocean","ah","octopus and olive"),
    "U":("you","unicorn","uh","umbrella and up"),
}
basic = {
    "B":("buh","ball, bear, and banana"), "C":("kuh","cat, car, and cup"), "D":("duh","dog, duck, and drum"),
    "F":("fff","fish, fox, and flower"), "G":("guh","goat, game, and grapes"), "H":("huh","hat, horse, and house"),
    "J":("juh","jellyfish, jar, and jump"), "K":("kuh","kite, king, and kitten"), "L":("lll","lion, leaf, and lamp"),
    "M":("mmm","moon, mouse, and milk"), "N":("nnn","nest, nose, and night"), "P":("puh","pig, pizza, and penguin"),
    "Q":("kwuh","queen, quilt, and quiet"), "R":("rrr","rainbow, rabbit, and ring"), "S":("sss","sun, sock, and snake"),
    "T":("tuh","turtle, tiger, and tree"), "V":("vuh","violin, van, and volcano"), "W":("wuh","whale, wagon, and window"),
    "X":("ks","fox, box, and six"), "Y":("yuh","yo-yo, yarn, and yellow"), "Z":("zzz","zebra, zipper, and zoo"),
}
words = dict(zip(letters, "apple ball cat dog egg fish goat hat igloo jellyfish kite lion moon nest octopus pig queen rainbow sun turtle umbrella violin whale fox yarn zebra".split()))

def lesson_parts(letter):
    opening = f"Oh, look! Big {letter} and little {letter.lower()}!"
    if letter == "X":
        listening = "Let's listen to the last sound in fox. Fox."
        teaching = "Hear it? Box and six have that sound at the end, too!"
    elif letter == "V":
        listening = "Let's listen to the first sound in van. Van."
        teaching = "Put your top teeth on your lower lip. Feel it buzz! Violin and volcano begin the same way!"
    else:
        examples = {"A":"apple and ant", "E":"egg and elephant", "I":"igloo and insect", "O":"octopus and olive", "U":"umbrella and up"}
        word = words[letter]
        other = examples[letter] if letter in examples else basic[letter][1]
        listening = f"Let's listen to the first sound in {word}. {word}."
        teaching = f"Hear it? You can hear that sound in {other}, too!"
    return [
        (opening, "+8%", "+7Hz"),
        (listening, "-15%", "+1Hz"),
        (teaching, "-3%", "+5Hz"),
        (question(letter), "+2%", "+7Hz"),
    ]

def question(letter):
    prompt = "Which picture has the X sound at the end?" if letter == "X" else f"Which picture starts with {letter}?"
    return f"{prompt}... Tap each picture to hear its name... Then press the check."

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
