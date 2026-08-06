import re
import xml.etree.ElementTree as ET
from html import unescape
from xml.sax.saxutils import escape as _xml_escape


def read_multiline_input(prompt):
    """Read multi-line input from the user until they type 'END' on its own
    line or send EOF (Ctrl+D). Returns the joined text, stripped."""
    print(prompt)
    print(
          "Type 'END' on its own line (or press Ctrl+D / Ctrl+Z on Windows) "
          "when you are done.\n")
    lines = []
    while True:
        try:
            line = input(": ")
        except EOFError:
            break
        if line.strip().upper() == "END":
            break
        lines.append(line)
    return "\n".join(lines).strip()


def _clean_continuation_line(line):
    """Strip list bullets and markdown emphasis from an unattributed line so
    the TTS doesn't read artifacts like "star star" or leading dashes."""
    line = line.strip()
    line = re.sub(r'^\*+', '', line)
    line = re.sub(r'^[\-\u2013\u2014\u00b7\u2022#]+\s+', '', line)
    line = re.sub(r'\*+\s*$', '', line)
    return line.strip()


def build_ssml_from_dialogue(dialogue_text, speaker1, speaker2):
    """Parse raw LLM dialogue into per-speaker SSML turns.

    LLM output rarely uses the exact "Speaker:" prefix, so speaker turns are
    matched leniently: markdown bold ("**Name:**"), leading bullets, extra
    whitespace, and common separators (":", "-", "\u2013", "\u2014", ".") are all
    accepted, case-insensitively. Unattributed lines become a continuation of
    the previous turn; stage directions and filler lines are dropped. All text
    is XML-escaped so the returned document is always well formed.
    """
    # Remove any stage directions or descriptions in parentheses.
    dialogue_text = re.sub(r'\([^)]*\)', '', dialogue_text).strip()

    speaker_names = "|".join(re.escape(name) for name in (speaker1, speaker2))
    speaker_turn_re = re.compile(
        r'^\s*(?:\*{1,2}|-)?\s*(' + speaker_names + r')\s*(?:\*{1,2})?\s*(?::|\uff1a|\u2013|\u2014|-|\.)\s*(.*)$',
        re.IGNORECASE,
    )

    turns = []
    last_speaker = None
    for raw_line in dialogue_text.split("\n"):
        line = raw_line.strip()
        if not line:
            continue
        match = speaker_turn_re.match(line)
        if match:
            # Normalize to the canonical speaker name so the downstream voice
            # lookup works regardless of the case the LLM used.
            speaker = (
                speaker1 if match.group(1).lower() == speaker1.lower() else speaker2
            )
            content = match.group(2).strip().lstrip("*").strip()
            last_speaker = speaker
            if content:
                turns.append((speaker, content))
            continue
        # Drop filler lines and stage directions (e.g. "(laughs)", "[beat]").
        stripped = line.strip("* -\u2013\u2014\u00b7\u2022#")
        if not stripped or not re.search(r"[A-Za-z]", line):
            continue
        if (line.startswith("(") and line.endswith(")")) or (
            line.startswith("[") and line.endswith("]")
        ):
            continue
        # Otherwise treat the line as a continuation of the last speaker's
        # turn, or as an intro line for speaker1 before any turn is seen.
        speaker = last_speaker if last_speaker else speaker1
        turns.append((speaker, _clean_continuation_line(line)))

    ssml_parts = ["<speak>"]
    for speaker, content in turns:
        break_time = "0.5s" if speaker == speaker1 else "0.3s"
        escaped_content = _xml_escape(content, {'"': '&quot;'})
        ssml_parts.append(f'<voice name="{speaker}">')
        ssml_parts.append(f"    {escaped_content}")
        ssml_parts.append(f'    <break time="{break_time}"/>')
        ssml_parts.append("</voice>")
    ssml_parts.append("</speak>")
    return "\n".join(ssml_parts) + "\n"


def parse_ssml(file_path):
    """Parse an SSML file and return a list of (voice_name, text) segments."""
    print(f"Parsing SSML from '{file_path}'...")
    with open(file_path, "r", encoding="utf-8") as file:
        data = file.read()

    def localname(tag):
        return tag.rsplit("}", 1)[-1]

    segments = []
    try:
        root = ET.fromstring(data)
        for elem in root.iter():
            if localname(elem.tag) != "voice":
                continue
            voice_name = elem.get("name")
            if not voice_name:
                continue
            text = "".join(elem.itertext()).strip()
            if text:
                segments.append((voice_name, text))
    except ET.ParseError as exc:
        # Lenient fallback: recover segments even if a stray character (e.g.
        # an unescaped '&') makes the file invalid XML.
        print(f"Strict XML parse failed ({exc}); using lenient fallback.")
        for match in re.finditer(
            r'<voice\s+name="([^"]+)"\s*>(.*?)</voice>', data, re.DOTALL
        ):
            voice_name = match.group(1)
            text = re.sub(r"<break\s+[^>]*/>", "", match.group(2))
            text = unescape(text).strip()
            if text:
                segments.append((voice_name, text))

    if not segments:
        print("Warning: no voice segments were found in the SSML.")
    print("SSML parsing completed.")
    return segments


def make_podcast():
    import random
    import edge_tts
    import librosa
    import soundfile as sf
    import numpy as np
    import asyncio
    from ollama import Client
    import subprocess

    content = read_multiline_input(
        "Paste the contents of the article you want summarized as a podcast below."
    )
    if not content:
        print("No content provided. Aborting podcast generation.")
        return
    print("Reading input content from 'content.txt'...")
    
    # Save and read content correctly
    with open("content.txt", "w") as file:
        file.write(content)
    
    with open("content.txt", "r") as file:
        text = file.read().strip()

    # Configuration: speaker and language
    speaker1 = "Cleetus" 
    speaker2 = "Jane" 
    lang = "English"  
    num = 10  
    
    prompt_text = f"Provide a name for a podcast based on {text} Do not include anything other than the PLAIN TEXT of the name for the podcast include only one name. "
    command = ["ollama", "run", "llama3.2:1b", "--hidethinking", prompt_text]
    
    # Extract the actual text output from the subprocess
    result = subprocess.run(command, capture_output=True, text=True)
    podcast_name = result.stdout.strip()
    if not podcast_name:
        podcast_name = "Generated_Podcast"

    # Voice mapping
    voice_map = {
        "Cleetus": "en-US-AndrewMultilingualNeural", # Map speaker1 to an edge-tts voice
        "Jane": "en-US-AvaMultilingualNeural"       # Map speaker2 to an edge-tts voice
    }

    def generate_ssml_conversation(text, speaker1="Cleetus", speaker2="Jane"):
        print("Generating SSML conversation...")

        prompt_chosen = random.randint(1, 2)
        if prompt_chosen == 1:
            dialogue_prompt = (
                f"Create a light-hearted (and serious where needed) conversation between two people based on the following text if the text is a query generate a conversation based on the topic itself.: '{text}' . "
                f"The first person is {speaker1}, and the second person is {speaker2}. They should affirm each other "
                f"and include pauses, but do not include stage directions or actions like (smiling) or (pausing). "
                f"Let {speaker1} introduce the podcast and {speaker2} at the start. Text in {lang} and at least {num} turns of every speaker.")
        else:
            dialogue_prompt = (
                f"Create a friendly debate between two people based on the following text if the text is a query generate a conversation based on the topic itsel: '{text}'. "
                f"The first person is {speaker1}, and the second person is {speaker2}. They should not affirm each other it is a debate"
                f"and include pauses, but do not include stage directions or actions like (smiling) or (pausing). "
                f"Let {speaker1} introduce the podcast and {speaker2} at the start. Text in {lang} and at least {num} turns of every speaker.")
        
        client = Client()
        messages = [{'role': 'user', 'content': f"{dialogue_prompt}"}]
        
        raw_output = ''
        for part in client.chat("llama3.2:1b", messages=messages, stream=True):
            raw_output += part.message.content
        
        return build_ssml_from_dialogue(raw_output, speaker1, speaker2)

    # Generate SSML conversation (returns a complete <speak>...</speak> document)
    ssml_conversation = generate_ssml_conversation(text, speaker1, speaker2)

    print("SSML conversation generated successfully.")

    # Save the SSML output to a text file
    print("Saving SSML output to 'SSML.txt'...")
    with open("SSML.txt", "w", encoding="utf-8") as file:
        file.write(ssml_conversation)

    async def synthesize_text(text, voice_name, filename):
        edge_voice = voice_map.get(voice_name)  
        if edge_voice is None:
            raise ValueError(f"Unknown voice name: {voice_name}")
        print(f"Generating audio for voice: {edge_voice}")  
        communicate = edge_tts.Communicate(text, voice=edge_voice, rate="+15%")
        await communicate.save(filename)
        print(f"Audio saved to '{filename}'.")

    async def main_async():
        segments = parse_ssml("SSML.txt")
        print(f"Found {len(segments)} segments to synthesize.")
        
        # Synthesize speech for each segment
        for i, (voice_name, text) in enumerate(segments):
            mp3_filename = f"output_segment_{i + 1}.mp3"
            await synthesize_text(text, voice_name, mp3_filename)

        # Combine the segments into a single file
        print("Combining audio segments...")
        combined_audio = None
        sample_rate = None

        for i in range(len(segments)):
            mp3_filename = f"output_segment_{i + 1}.mp3"
            audio_data, sr = librosa.load(mp3_filename, sr=None)

            if combined_audio is None:
                combined_audio = audio_data
                sample_rate = sr
            else:
                combined_audio = np.concatenate([combined_audio, audio_data])

        if combined_audio is not None:
            output_filename = f"{podcast_name}.wav"
            sf.write(output_filename, combined_audio, sample_rate)
            print(f"Podcast successfully saved as: {output_filename}")
        else:
            print("No audio data generated.")

    # Run the main async loop
    asyncio.run(main_async())
