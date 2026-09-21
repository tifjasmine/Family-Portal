import asyncio
from pathlib import Path
import edge_tts

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

def lesson(letter):
    opening = f"Big {letter}... Little {letter.lower()}..."
    if letter == "X":
        teaching = "Listen to the last sound in fox... fox... You can hear it in box and six, too."
    elif letter == "V":
        teaching = "Listen to the first sound in van... van... Put your top teeth on your lower lip... Feel it buzz! Violin and volcano begin that way, too."
    else:
        examples = {"A":"apple and ant", "E":"egg and elephant", "I":"igloo and insect", "O":"octopus and olive", "U":"umbrella and up"}
        word = words[letter]
        other = examples[letter] if letter in examples else basic[letter][1]
        teaching = f"Listen to the first sound in {word}... {word}... You can hear it in {other}, too."
    return f"{opening} {teaching}... {question(letter)}"

def question(letter):
    prompt = "Which picture has the X sound at the end?" if letter == "X" else f"Which picture starts with {letter}?"
    return f"{prompt}... Tap each picture to hear its name... Then press the check."

async def create(path, text, gate):
    async with gate:
        path.parent.mkdir(parents=True, exist_ok=True)
        await edge_tts.Communicate(text, VOICE, rate=RATE, pitch=PITCH).save(str(path))

async def main():
    gate, clips = asyncio.Semaphore(6), []
    for letter in letters:
        lower = letter.lower()
        clips += [
            create(ROOT / f"audio/lessons/{lower}.mp3", lesson(letter), gate),
            create(ROOT / f"audio/questions/{lower}.mp3", question(letter), gate),
            create(ROOT / f"audio/words/{lower}.mp3", words[letter] + ".", gate),
        ]
    clips += [
        create(ROOT / "audio/feedback/correct.mp3", "Yes!... You got it!... Great listening!", gate),
        create(ROOT / "audio/feedback/again.mp3", "Almost!... Listen to the sound again... Then try another picture.", gate),
        create(ROOT / "audio/feedback/choose.mp3", "Choose a picture first.", gate),
    ]
    await asyncio.gather(*clips)

if __name__ == "__main__":
    asyncio.run(main())
