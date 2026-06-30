def make_podcast():
    import random
    import re
    import edge_tts
    import xml.etree.ElementTree as ET
    import librosa
    import soundfile as sf
    import numpy as np
    import asyncio
    from ollama import Client
    import subprocess
    content = input("Paste the contents of the article you want summarized as a podcast below. \n : ")
    print("Reading input content from 'content.txt'...")
    with open("content.txt", "w") as file:
        file.write(content)
        file.close()
        with open("content.txt", "r"):
            text = file.read().strip()

    # Configuration: speaker and language
    speaker1 = "Cleetus" # Change the name here
    speaker2 = "Jane" # Change the name here
    lang = "English"  # Change the language here
    num = 10  # Minimum turns per speaker in dialogue
    podcast_name = ""
    prompt_text = f"Provide a name for a podcast based on {text} Do not include anything other than the PLAIN TEXT of the name for the podcast include only one name. "
    command = ["ollama", "run", "gpt-oss:20b-cloud", "--hidethinking", prompt_text]
    podcast_name = subprocess.run(command, capture_output=True, text=True)
    # Voice mapping
    voice_map = {
        "Ava": "en-US-AvaMultilingualNeural", # Change the edge-tts voice here
        "Andrew": "en-US-AndrewMultilingualNeural" # Change the edge-tts voice here
    }

    def generate_ssml_conversation(text, speaker1="Ava", speaker2="Andrew"):
        print("Generating SSML conversation...")

        prompt_chosen = random.randint(1, 2)
        if prompt_chosen == 1:

            dialogue_prompt = (
                f"Create a light-hearted (and serious where needed) conversation between two people based on the following text: '{text}'. "
                f"The first person is {speaker1}, and the second person is {speaker2}. They should affirm each other "
                f"and include pauses, but do not include stage directions or actions like (smiling) or (pausing). "
                f"Let {speaker1} introduce the podcast and {speaker2} at the start. Text in {lang} and at least {num} turns of every speaker.")
        else:
            dialogue_prompt = (
                f"Create a freindly debate between two people based on the following text: '{text}'. "
                f"The first person is {speaker1}, and the second person is {speaker2}. They should not affirm each other it is a debate"
                f"and include pauses, but do not include stage directions or actions like (smiling) or (pausing). "
                f"Let {speaker1} introduce the podcast and {speaker2} at the start. Text in {lang} and at least {num} turns of every speaker.")
        client = Client()
        messages = [

                {
                    'role': 'user',
                    'content': (
                        f"{dialogue_prompt}"
                    )

                }
            ]
        raw_output = ''
        for part in client.chat("gpt-oss:20b:cloud", messages=messages, stream=True):
            raw_output += part.message.content
            dialogue_text = raw_output


        # Remove any stage directions or descriptions in parentheses
        dialogue_text = re.sub(r'\([^)]*\)', '', dialogue_text).strip()

        # Split the dialogue into parts based on the speaker's name
        ssml_output = '<speak>\n'
        dialogue_lines = dialogue_text.split("\n")

        for line in dialogue_lines:
            line = line.strip()
            if line.startswith(speaker1 + ":"):
                # Use speaker1's voice
                ssml_output += f'<voice name="{speaker1}">\n'
                ssml_output += f'    {line.replace(speaker1 + ":", "").strip()}\n'
                ssml_output += '    <break time="0.5s"/>\n'
                ssml_output += '</voice>\n'
            elif line.startswith(speaker2 + ":"):
                # Use speaker2's voice
                ssml_output += f'<voice name="{speaker2}">\n'
                ssml_output += f'    {line.replace(speaker2 + ":", "").strip()}\n'
                ssml_output += '    <break time="0.3s"/>\n'
                ssml_output += '</voice>\n'

    # Generate SSML conversation
    ssml_conversation = generate_ssml_conversation(text)

    ssml_conversation += '</speak>'

    print("SSML conversation generated successfully.")


    # Check if SSML conversation generation was successful
    if ssml_conversation is None:
        print("Exiting the script due to error in SSML generation.")
        exit(1)  # Exit the script if there was an error

    # Save the SSML output to a text file
    print("Saving SSML output to 'SSML.txt'...")
    with open("SSML.txt", "w") as file:
        file.write(ssml_conversation)

    print("SSML output has been saved to SSML.txt.")

    async def synthesize_text(text, voice_name, filename):
        """Use EdgeTTS to convert text to speech and save it as an MP3 file."""
        edge_voice = voice_map.get(voice_name)  # Get the right voice
        if edge_voice is None:
            raise ValueError(f"Unknown voice name: {voice_name}")
        print(f"Generating audio for voice: {edge_voice}")  # Debug output
        print(f"Text: {text}")  # Debug output
        communicate = edge_tts.Communicate(text, voice=edge_voice, rate="+15%")
        await communicate.save(filename)
        print(f"Audio saved to '{filename}'.")

    def parse_ssml(file_path):
        """Parse the SSML file and extract text and speaker info."""
        print(f"Parsing SSML from '{file_path}'...")
        tree = ET.parse(file_path)
        root = tree.getroot()

        segments = []

        for elem in root:
            if elem.tag == 'voice':
                voice_name = elem.attrib['name']
                text = ''.join(elem.itertext()).strip()
                segments.append((voice_name, text))

        print("SSML parsing completed.")
        return segments

    async def main():
        # Parse the SSML output that was saved earlier
        segments = parse_ssml("SSML.txt")
        print(f"Found {len(segments)} segments to synthesize.",  segments,"...")
        combined_audio = None
        sample_rate = None

        for i in range(len(segments)):
            mp3_filename = f"output_segment_{i + 1}.mp3"
            audio_data, sr = librosa.load(mp3_filename, sr=None)


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

        # Save the final combined audio
        sf.write(f"{podast_name}.wav", combined_audio, sample_rate)


    # Run the main function
    asyncio.run(main())
