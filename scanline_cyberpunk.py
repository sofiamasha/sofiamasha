"""
scanline_cyberpunk.py

Cria uma animação em que uma foto é revelada linha por linha,
como se uma máquina/laser estivesse "escaneando" e desenhando a imagem.

Saídas:
  - foto_scanline.mp4
  - foto_scanline.gif

Instalação:
  pip install opencv-python pillow numpy

Uso:
  python scanline_cyberpunk.py

Coloque a foto na mesma pasta do script e altere INPUT_IMAGE abaixo.
"""

import cv2
import numpy as np
from PIL import Image
from pathlib import Path

# ============================================================
# CONFIGURAÇÃO
# ============================================================

# Nome da sua foto.
# Se estiver usando o arquivo que você colocou no projeto do GitHub:
INPUT_IMAGE = "fotosofia.jpeg"

# Nome dos arquivos de saída
OUTPUT_MP4 = "foto_scanline.mp4"
OUTPUT_GIF = "foto_scanline.gif"

# Tamanho máximo da animação.
# 720 deixa o arquivo relativamente leve para GitHub/redes sociais.
MAX_WIDTH = 720

# Quadros por segundo
FPS = 30

# Quantidade de segundos da animação
DURATION = 7

# Cor do laser em BGR (OpenCV):
# vermelho brilhante
LASER_COLOR = (30, 30, 255)

# Fundo:
BACKGROUND = (3, 3, 8)


# ============================================================
# FUNÇÕES AUXILIARES
# ============================================================

def resize_image(img, max_width):
    """Redimensiona mantendo a proporção."""
    h, w = img.shape[:2]

    if w <= max_width:
        return img

    new_h = int(h * max_width / w)
    return cv2.resize(img, (max_width, new_h), interpolation=cv2.INTER_AREA)


def add_scanline_effect(img, current_y):
    """
    Cria um frame da animação.

    Tudo abaixo da linha de escaneamento permanece preto.
    Tudo acima já foi revelado.
    Uma linha vermelha brilhante marca o ponto atual.
    """

    h, w = img.shape[:2]

    # Fundo preto/azulado
    frame = np.full_like(img, BACKGROUND, dtype=np.uint8)

    # --------------------------------------------------------
    # 1. Revela a imagem até current_y
    # --------------------------------------------------------
    if current_y > 0:
        frame[:current_y] = img[:current_y]

    # --------------------------------------------------------
    # 2. Pequeno "glow" nas linhas próximas ao laser
    # --------------------------------------------------------
    glow_height = 16

    y1 = max(0, current_y - glow_height)
    y2 = min(h, current_y + 1)

    if y2 > y1:
        # Quanto mais perto da linha, mais forte o brilho.
        for y in range(y1, y2):
            distance = abs(current_y - y)
            strength = max(0, 1 - distance / glow_height)

            overlay = np.zeros_like(frame[y:y+1])
            overlay[:, :, :] = LASER_COLOR

            alpha = 0.10 + 0.30 * strength
            frame[y:y+1] = cv2.addWeighted(
                frame[y:y+1],
                1 - alpha,
                overlay,
                alpha,
                0
            )

    # --------------------------------------------------------
    # 3. Linha principal do laser
    # --------------------------------------------------------
    if 0 <= current_y < h:
        cv2.line(
            frame,
            (0, current_y),
            (w, current_y),
            LASER_COLOR,
            2
        )

        # Segunda linha fina branca/vermelha para dar aparência
        # de scanner/HUD.
        cv2.line(
            frame,
            (0, max(0, current_y - 2)),
            (w, max(0, current_y - 2)),
            (255, 255, 255),
            1
        )

    # --------------------------------------------------------
    # 4. HUD cyberpunk
    # --------------------------------------------------------
    progress = int((current_y / max(1, h - 1)) * 100)

    font = cv2.FONT_HERSHEY_SIMPLEX

    # Caixa discreta no canto superior esquerdo
    cv2.rectangle(
        frame,
        (15, 15),
        (235, 72),
        (15, 15, 25),
        -1
    )

    cv2.rectangle(
        frame,
        (15, 15),
        (235, 72),
        LASER_COLOR,
        1
    )

    cv2.putText(
        frame,
        "IMAGE SCANNER",
        (27, 38),
        font,
        0.55,
        (255, 255, 255),
        1,
        cv2.LINE_AA
    )

    cv2.putText(
        frame,
        f"SCAN {progress:03d}%",
        (27, 60),
        font,
        0.48,
        LASER_COLOR,
        1,
        cv2.LINE_AA
    )

    # --------------------------------------------------------
    # 5. Marcadores laterais da área escaneada
    # --------------------------------------------------------
    marker_x = 10

    if 0 < current_y < h:
        cv2.line(
            frame,
            (marker_x, current_y - 12),
            (marker_x, current_y + 12),
            LASER_COLOR,
            2
        )

        cv2.line(
            frame,
            (w - marker_x, current_y - 12),
            (w - marker_x, current_y + 12),
            LASER_COLOR,
            2
        )

    # --------------------------------------------------------
    # 6. Pequenas linhas decorativas de HUD
    # --------------------------------------------------------
    cv2.line(frame, (w - 150, 25), (w - 25, 25), LASER_COLOR, 1)
    cv2.line(frame, (w - 120, 32), (w - 25, 32), LASER_COLOR, 1)

    cv2.putText(
        frame,
        "RENDERING...",
        (w - 155, 55),
        font,
        0.38,
        (180, 180, 180),
        1,
        cv2.LINE_AA
    )

    return frame


def add_finish_effect(img, frames_count):
    """
    Adiciona alguns frames finais para a imagem ficar totalmente
    visível antes de terminar.
    """

    frames = []

    h, w = img.shape[:2]

    # Linhas finais do HUD
    for i in range(frames_count):
        frame = img.copy()

        alpha = i / max(1, frames_count - 1)

        # Texto final
        cv2.putText(
            frame,
            "SCAN COMPLETE",
            (25, h - 25),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (30, 30, 255),
            1,
            cv2.LINE_AA
        )

        # Flash sutil do laser no primeiro frame
        if i == 0:
            overlay = frame.copy()
            cv2.line(
                overlay,
                (0, h - 1),
                (w, h - 1),
                LASER_COLOR,
                3
            )
            frame = cv2.addWeighted(frame, 0.65, overlay, 0.35, 0)

        frames.append(frame)

    return frames


# ============================================================
# PROGRAMA PRINCIPAL
# ============================================================

def main():
    input_path = Path(INPUT_IMAGE)

    if not input_path.exists():
        raise FileNotFoundError(
            f'Não encontrei "{INPUT_IMAGE}". '
            "Coloque a foto na mesma pasta do script."
        )

    # Lê a foto
    image = cv2.imread(str(input_path), cv2.IMREAD_COLOR)

    if image is None:
        raise ValueError("Não foi possível abrir a imagem.")

    # Redimensiona para manter o arquivo mais leve
    image = resize_image(image, MAX_WIDTH)

    height, width = image.shape[:2]

    total_scan_frames = int(FPS * DURATION)

    print(f"Imagem: {width}x{height}")
    print(f"FPS: {FPS}")
    print(f"Duração: {DURATION}s")
    print(f"Frames de scan: {total_scan_frames}")

    # --------------------------------------------------------
    # Configura o MP4
    # --------------------------------------------------------
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")

    video = cv2.VideoWriter(
        OUTPUT_MP4,
        fourcc,
        FPS,
        (width, height)
    )

    if not video.isOpened():
        raise RuntimeError(
            "Não foi possível criar o MP4. "
            "Tente instalar/atualizar o OpenCV."
        )

    # Frames para o GIF
    gif_frames = []

    # --------------------------------------------------------
    # Gera o scanline
    # --------------------------------------------------------
    for frame_index in range(total_scan_frames):

        # Vai de -1 até height
        current_y = int(
            ((frame_index + 1) / total_scan_frames) * height
        )

        frame = add_scanline_effect(image, current_y)

        # Salva no MP4
        video.write(frame)

        # OpenCV usa BGR; PIL usa RGB
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        gif_frames.append(Image.fromarray(rgb))

        if frame_index % FPS == 0:
            percent = int((frame_index / total_scan_frames) * 100)
            print(f"Renderizando: {percent}%")

    # --------------------------------------------------------
    # Frames finais
    # --------------------------------------------------------
    final_frames = add_finish_effect(image, max(1, FPS // 2))

    for frame in final_frames:
        video.write(frame)

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        gif_frames.append(Image.fromarray(rgb))

    video.release()

    # --------------------------------------------------------
    # Salva GIF
    #
    # O GIF usa uma redução de cores automática.
    # Para não criar um arquivo gigantesco, reduzimos o tamanho
    # para no máximo 480 px de largura.
    # --------------------------------------------------------
    gif_width = min(480, width)
    gif_height = int(height * gif_width / width)

    gif_frames_small = []

    for frame in gif_frames:
        frame = frame.resize(
            (gif_width, gif_height),
            Image.Resampling.LANCZOS
        )
        gif_frames_small.append(frame.convert("P", palette=Image.Palette.ADAPTIVE))

    gif_frames_small[0].save(
        OUTPUT_GIF,
        save_all=True,
        append_images=gif_frames_small[1:],
        duration=int(1000 / FPS),
        loop=0,
        optimize=True
    )

    print()
    print("======================================")
    print("ANIMAÇÃO CONCLUÍDA!")
    print("======================================")
    print(f"MP4: {OUTPUT_MP4}")
    print(f"GIF: {OUTPUT_GIF}")
    print()
    print("Para o GitHub, você pode colocar o GIF em:")
    print("assets/foto-scan.gif")
    print()
    print("E no README usar:")
    print('<p align="center">')
    print('  <img src="./assets/foto-scan.gif" width="500"/>')
    print('</p>')


if __name__ == "__main__":
    main()
