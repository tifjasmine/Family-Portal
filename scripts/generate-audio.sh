#!/bin/zsh
set -e
cd "${0:A:h}/.."
mkdir -p audio/lessons audio/questions audio/words audio/feedback /private/tmp/family-portal-audio

voice="Flo (English (US))"
letters=(A B C D E F G H I J K L M N O P Q R S T U V W X Y Z)
sounds=("ay, or ah" buh kuh duh "ee, or eh" fff guh huh "eye, or ih" juh kuh lll mmm nnn "oh, or ah" puh kwuh rrr sss tuh "you, or uh" vvv wuh ks yuh zzz)
words=(apple ball cat dog egg fish goat hat igloo jellyfish kite lion moon nest octopus pig queen rainbow sun turtle umbrella violin whale fox yarn zebra)

make_clip(){
  local output="$1" text="$2" temp="/private/tmp/family-portal-audio/clip.aiff"
  say -v "$voice" -r 155 -o "$temp" "$text"
  afconvert -f WAVE -d LEI16 "$temp" "$output"
}

for i in {1..26}; do
  letter="${letters[$i]}"; lower="${letter:l}"; sound="${sounds[$i]}"; word="${words[$i]}"
  make_clip "audio/lessons/$lower.wav" "Big $letter. [[slnc 500]] Little $lower. [[slnc 650]] The letter $letter says $sound. [[slnc 700]] Like $word! [[slnc 800]] Which picture starts with $letter? [[slnc 450]] Tap each picture to hear its name. [[slnc 500]] Then press submit."
  make_clip "audio/questions/$lower.wav" "Which picture starts with $letter? [[slnc 650]] Tap each picture to hear its name. [[slnc 500]] Then press submit."
  make_clip "audio/words/$lower.wav" "$word."
done

make_clip "audio/feedback/correct.wav" "Yes! [[slnc 450]] You got it! [[slnc 450]] Great listening!"
make_clip "audio/feedback/again.wav" "Almost! [[slnc 500]] Listen to the sound again. [[slnc 550]] Then try another picture."
make_clip "audio/feedback/choose.wav" "Choose a picture first."
rm -rf /private/tmp/family-portal-audio
