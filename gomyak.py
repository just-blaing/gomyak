import os
import sys
import tkinter as tk
from PIL import Image, ImageTk
import pygame
import cv2
from ffpyplayer.player import MediaPlayer
import random
import threading
import time

image_path = "photo.jpg"
sound_path = "sound.mp3"
videos = ["video1.mp4", "video2.mp4", "video3.mp4", "video4.mp4"]
image_size = (720, 547)
accept_zone = (354, 463, 422, 544)
decline_zone = (290, 466, 346, 544)
video_playing = False


def in_zone(x, y, zone):
    x1, y1, x2, y2 = zone
    return x1 <= x <= x2 and y1 <= y <= y2


def play_sound():
    pygame.mixer.init()
    pygame.mixer.music.load(sound_path)
    pygame.mixer.music.play(loops=-1)


def play_video():
    global video_playing
    video_playing = True
    path = random.choice(videos)
    cap = cv2.VideoCapture(path)
    audio = MediaPlayer(path)
    pygame.display.init()
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    clock = pygame.time.Clock()
    fps = cap.get(cv2.CAP_PROP_FPS) or 30

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = cv2.resize(frame, screen.get_size())
        surf = pygame.surfarray.make_surface(frame.swapaxes(0, 1))
        screen.blit(surf, (0, 0))
        pygame.display.flip()
        audio.get_frame()
        pygame.event.get()
        clock.tick(fps)

    cap.release()
    pygame.display.quit()
    video_playing = False


def close_and_play(window):
    pygame.mixer.music.stop()
    window.destroy()
    threading.Thread(target=play_video, daemon=True).start()


def create_popup():
    time.sleep(random.randint(1, 10))
    if video_playing:
        return

    window = tk.Tk()
    window.attributes("-topmost", True)
    window.overrideredirect(True)
    sw = window.winfo_screenwidth()
    sh = window.winfo_screenheight()
    x = (sw - image_size[0]) // 2
    y = (sh - image_size[1]) // 2
    window.geometry(f"{image_size[0]}x{image_size[1]}+{x}+{y}")
    img = Image.open(image_path).resize(image_size, Image.Resampling.LANCZOS)
    img_tk = ImageTk.PhotoImage(img)
    label = tk.Label(window, image=img_tk)
    label.pack()
    drag = {"x": 0, "y": 0, "moved": False}

    def on_press(e):
        drag["x"] = e.x
        drag["y"] = e.y
        drag["moved"] = False

    def on_drag(e):
        dx = e.x - drag["x"]
        dy = e.y - drag["y"]
        if abs(dx) > 4 or abs(dy) > 4:
            drag["moved"] = True
        window.geometry(f"+{window.winfo_x() + dx}+{window.winfo_y() + dy}")
        drag["x"] = e.x
        drag["y"] = e.y

    def on_release(e):
        if drag["moved"]:
            return
        if in_zone(e.x, e.y, accept_zone):
            close_and_play(window)
        elif in_zone(e.x, e.y, decline_zone):
            pygame.mixer.music.stop()
            window.destroy()

    window.bind("<ButtonPress-1>", on_press)
    window.bind("<B1-Motion>", on_drag)
    window.bind("<ButtonRelease-1>", on_release)
    play_sound()
    window.mainloop()


def start_loop():
    while True:
        create_popup()


threading.Thread(target=start_loop).start()
