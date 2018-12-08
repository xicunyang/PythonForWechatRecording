from pydub import AudioSegment

def mp3_to_wav(fileName):
    song = AudioSegment.from_mp3(fileName + ".mp3")
    song.export(fileName + ".wav", format="wav")


if __name__ == '__main__':
    pass
