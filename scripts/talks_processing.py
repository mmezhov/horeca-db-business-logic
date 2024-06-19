"""
Сборка из записанных фрагментов потокового аудио с терминала кафе
цельных разговоров персонала с клиентами;
передача записанных разговоров для процессинга в сервисе речевой аналитики;

"""
import logging
import yaml
import numpy as np
import scipy.fftpack as fftpack
import subprocess
import noisereduce as nr

from pathlib import Path
from pydub import AudioSegment
from pydub.silence import split_on_silence
from pydub import silence
from scipy.io import wavfile


""" CONST """
PWD = Path.cwd()
LOG_LEVEL = logging.DEBUG
MODULE_NAME = "talks_processing"


""" LOGGING """
log = logging.getLogger(MODULE_NAME)
log.setLevel(LOG_LEVEL)
ch = logging.FileHandler(filename=PWD/f'logs/{MODULE_NAME}.log')
ch.setLevel(LOG_LEVEL)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
ch.setFormatter(formatter)
log.addHandler(ch)


try:
    with open(PWD/'talks_processing_config.yaml', 'r') as f:
        config = yaml.safe_load(f)
except:
    log.error("Error with opening talks_processing_config.yaml", exc_info=True)
    raise FileNotFoundError("talks_processing_config.yaml")


def convert_mp3_to_wav_mono(input_mp3_path, output_wav_path):
    command = [
        "ffmpeg",
        "-y",
        "-i", input_mp3_path,
        "-ac", "1",
        output_wav_path
    ]
    subprocess.run(command, check=True)


def filter_frequencies(audio: AudioSegment, low_freq=64, high_freq=2050): 
    # Преобразование в моно (если не моно)
    if audio.channels > 1:
        audio = audio.set_channels(1)
    
    # Извлечение сырых данных и частоты дискретизации
    samples = np.array(audio.get_array_of_samples())
    sample_rate = audio.frame_rate
    
    # Применение быстрого преобразования Фурье (FFT)
    fft_data = fftpack.fft(samples)
    frequencies = fftpack.fftfreq(len(fft_data), 1 / sample_rate)
    
    # Применение фильтрации частот
    fft_data[(frequencies < low_freq)] = 0
    fft_data[(frequencies > high_freq)] = 0
    
    # Обратное преобразование Фурье
    filtered_samples = fftpack.ifft(fft_data).real
    filtered_samples = np.int16(filtered_samples)
    
    # Создание нового AudioSegment из отфильтрованных данных
    return AudioSegment(
        data=filtered_samples.tobytes(),
        sample_width=audio.sample_width,
        frame_rate=sample_rate,
        channels=1
    )


# def process_audio(audio_fragment, min_silence_len: int = 1000, silence_thresh: int = -40):
def process_audio(mp3_file_path):
    """
    min_silence_len: минимальный фрагмент тишины, который будет являться триггером для разбиения аудио фрагмента
    silence_thresh: частота в децебеллах, ниже которой всё будет восприниматься как тишина

    Return:
    -----------
    silence: True, если была тишина на протяжении всего аудио фрагмента
    chunks: список сегментов, выделенных в аудио фрагменте, где была задетектирована не тишина

    """
    wav_file_path = f"{mp3_file_path.parent}/{mp3_file_path.stem}.wav"
    wav_file_reduced_noise_path = f"{mp3_file_path.parent}/{mp3_file_path.stem}_reduced_noise.wav"

    # Добавить громкости исходному файлу
    audio_segment = AudioSegment.from_file(mp3_file_path, channels=1).apply_gain(+10)
    audio_segment.export(wav_file_path, format='wav')

    # Удаление шумов
    rate, data = wavfile.read(wav_file_path)
    reduced_noise = nr.reduce_noise(y=data, sr=rate, n_jobs=-1)
    wavfile.write(wav_file_reduced_noise_path, rate, reduced_noise)

    # Создание AudioSegment
    audio_segment = AudioSegment.from_file(wav_file_reduced_noise_path, channels=1) 

    return audio_segment


def detect_speech(audio_segment: AudioSegment):
    """ Detect non silent segments in audio """
    # Извлечение сегментов с речью
    speech_segments = silence.detect_nonsilent(audio_segment)
    # log.debug(f"{mp3_file_path.stem}: speech_segments len = {len(speech_segments)}")

    is_talk = (
        len(speech_segments) >= 1 and  # более 1 сегмента выделено
        speech_segments[-1][0] != 0 and  # начало крайнего сегмента не равно началу аудио
        speech_segments[-1][-1] != round(audio_segment.duration_seconds * 1000)  # конец крайнего сегмента не равно концу аудио
    ) 

    return (is_talk, speech_segments)


def find_talks():
    # os.system(f"sudo mv {config.get('AUDIO_BATCHES_DIR')}/* {PWD}/audios/raw")
    audios_list = list((PWD/'audios/raw').glob('*.mp3'))
    log.info(f"Len of audios_list: {len(audios_list)} ")
    
    merged_audio = AudioSegment.empty()

    for audio in audios_list:
        try:
            # silence, chunks = contains_only_silence(AudioSegment.from_mp3(audio))
            audio_segment = process_audio(audio)
            is_talk, speech_segments = detect_speech(audio_segment)
            
            if is_talk:
                log.debug(f"{audio.stem} has sounds")
                for start, end in speech_segments:
                    merged_audio += audio_segment[start:end]
            elif (not is_talk and len(merged_audio) > 0):
                log.debug(f"{audio.stem} - silence")
                merged_audio.export(PWD / f'audios/talks/{audio.name}', format='mp3')
                log.debug(f"Talk saved to {PWD / f'audios/talks/{audio.name}'}")
                merged_audio = AudioSegment.empty()
                # send talk to speech recognition server
                # delete talk from disk
            else:
                log.debug(f"{audio.stem} - silence")
        except:
            log.error(f"Error with processing {audio}", exc_info=True)
            continue
        # os.system(f"rm {str(audio)}")


def clean_processed_audios():
    ...


def main():
    """
    Пайплайн:
    - собрать "разговоры" из фрагментов аудио, преобразовать аудио до нужной частоты и конвертировать в моно
    - передать "разговоры" в сервис для речевой аналитики
    - удалить все обработанные фрагменты
    - удалить переданные в обработку "разговоры" с диска
    """
    find_talks()


if __name__ == "__main__":
    main()
