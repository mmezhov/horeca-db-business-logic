"""
Сборка из записанных фрагментов потокового аудио с терминала кафе
цельных разговоров персонала с клиентами;
передача записанных разговоров для процессинга в сервисе речевой аналитики;

"""
import logging
import yaml
import os
import librosa
import numpy as np
import io
import subprocess

from pathlib import Path
from pydub import AudioSegment
from pydub.silence import split_on_silence
from pydub import silence


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


def convert_mp3_to_wav_mono_in_memory(mp3_data):
    # Создаем временные байтовые потоки для ввода и вывода
    mp3_stream = io.BytesIO(mp3_data)
    wav_stream = io.BytesIO()

    # Команда FFmpeg для конвертации MP3 в WAV (моно)
    command = [
        "ffmpeg",
        "-i", "pipe:0",
        "-ac", "1",
        "-f", "wav",
        "pipe:1"
    ]

    # Запуск FFmpeg
    process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    wav_data, _ = process.communicate(input=mp3_stream.read())
    wav_stream.write(wav_data)
    wav_stream.seek(0)

    return wav_stream


# def process_audio(audio_fragment, min_silence_len: int = 1000, silence_thresh: int = -40):
def process_audio(mp3_file_path, min_silence_len: int = 1000, silence_thresh: int = -40):
    """
    min_silence_len: минимальный фрагмент тишины, который будет являться триггером для разбиения аудио фрагмента
    silence_thresh: частота в децебеллах, ниже которой всё будет восприниматься как тишина

    Return:
    -----------
    silence: True, если была тишина на протяжении всего аудио фрагмента
    chunks: список сегментов, выделенных в аудио фрагменте, где была задетектирована не тишина

    """
    # chunks = split_on_silence(audio_fragment, min_silence_len=min_silence_len, silence_thresh=silence_thresh)
    # silence = (len(chunks) == 1 and len(chunks[0]) > 0)

     # Чтение MP3 файла в память
    with open(mp3_file_path, "rb") as f:
        mp3_data = f.read()

    # Конвертация MP3 в WAV (моно) в памяти
    wav_stream = convert_mp3_to_wav_mono_in_memory(mp3_data)
    wav_stream.seek(0)

    # Создание AudioSegment из WAV байтового потока
    audio_segment = AudioSegment.from_wav(wav_stream)

    # Извлечение сегментов с речью
    speech_segments = silence.detect_nonsilent(audio_segment, silence_thresh)
    # speech_segments = silence.detect_nonsilent(audio_segment)
    log.debug(f"{mp3_file_path.stem}: speech_segments len = {len(speech_segments)}")

    is_talk = (
        len(speech_segments) >= 1 and  # более 1 сегмента выделено
        speech_segments[-1][0] != 0 and  # начало крайнего сегмента не равно началу аудио
        speech_segments[-1][-1] != round(audio_segment.duration_seconds * 1000)  # конец крайнего сегмента не равно концу аудио
    )  

    return (is_talk, speech_segments, audio_segment)


def find_talks():
    # os.system(f"sudo mv {config.get('AUDIO_BATCHES_DIR')}/* {PWD}/audios/raw")
    audios_list = list((PWD/'audios/raw').glob('*.mp3'))
    log.info(f"Len of audios_list: {len(audios_list)} ")
    
    merged_audio = AudioSegment.empty()

    for audio in audios_list:
        try:
            # silence, chunks = contains_only_silence(AudioSegment.from_mp3(audio))
            is_talk, speech_segments, audio_segment = process_audio(audio)
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
