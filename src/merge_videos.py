import cv2
import sys
import numpy as np

def merge_videos_sequential(video1_path, video2_path, output_path):
    # 1. Открываем оба видеофайла
    cap1 = cv2.VideoCapture(video1_path)
    cap2 = cv2.VideoCapture(video2_path)
    
    if not cap1.isOpened() or not cap2.isOpened():
        print("Ошибка: Не удалось открыть один из файлов.")
        return

    # 2. Получаем параметры из ПЕРВОГО видео (разрешение и FPS)
    fps = cap1.get(cv2.CAP_PROP_FPS)
    width = int(cap1.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap1.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    # 3. Настраиваем объект для записи итогового видео
    fourcc = cv2.VideoWriter_fourcc(*'mp4v') # Кодек для MP4
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    num_animation_frames = 120
    cur_frame = 0

    first_video_frames = int(cap1.get(cv2.CAP_PROP_FRAME_COUNT))


    # 4. Читаем и записываем кадры из первого видео
    while cap1.isOpened():
        ret, frame = cap1.read()
        if not ret:
            break

        print(cur_frame)
        if cur_frame < first_video_frames - num_animation_frames:
            out.write(frame)
            cur_frame += 1
        else:
            _, frame2 = cap2.read()
            alpha = (first_video_frames - cur_frame) / num_animation_frames
            res = cv2.addWeighted(frame, alpha, frame2, 1-alpha, 0)
            out.write(res)
            cur_frame += 1
    cap1.release()

    cur_frame = 0
    # 5. Читаем и записываем кадры из второго видео
    while cap2.isOpened():
        ret, frame = cap2.read()
        if not ret:
            break
        
        out.write(frame)
        cur_frame += 1
        print(cur_frame)
    cap2.release()

    # 6. Закрываем итоговый файл
    out.release()
    print(f"Видео успешно сохранено в: {output_path}")

# Пример запуска:
merge_videos_sequential("result7.mp4", "..\\videos\\outer_planets.mp4", "result8.mp4")
