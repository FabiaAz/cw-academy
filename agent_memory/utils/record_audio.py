import pyaudio
import wave
import uuid
import keyboard  # pip install keyboard


def record_audio():
    """
    Grava áudio pelo microfone no Windows.
    Aperte ENTER para começar e ENTER de novo para parar a gravação.
    Retorna o nome do arquivo WAV gerado.
    """
    filename = f"audio_{uuid.uuid4().hex}.wav"

    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100
    WAVE_OUTPUT_FILENAME = filename

    p = pyaudio.PyAudio()
    stream = None
    frames = []

    print("👉 Pressione ENTER para começar a gravar...")
    keyboard.wait("enter")

    print("🎤 Gravando... pressione ENTER para parar.")
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    while True:
        data = stream.read(CHUNK)
        frames.append(data)
        if keyboard.is_pressed("enter"):
            break

    print("✅ Gravação finalizada!")

    stream.stop_stream()
    stream.close()
    p.terminate()

    wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

    return filename
