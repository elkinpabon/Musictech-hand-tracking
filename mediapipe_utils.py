import mediapipe as mp
import pygame
import numpy as np

mp_dibujo = mp.solutions.drawing_utils
mp_manos = mp.solutions.hands

PUNTAS_DEDOS_INDICES = [4, 8, 12, 16, 20]  # Pulgar, indice, medio, anular, meñique

def detectar_dedos(resultados, frame):
    puntas_dedos = []
    
    if not resultados.multi_hand_landmarks:
        return puntas_dedos
        
    alto, ancho, _ = frame.shape
    hand_landmarks = resultados.multi_hand_landmarks[0]
    
    for punto_indice in PUNTAS_DEDOS_INDICES:
        lm = hand_landmarks.landmark[punto_indice]
        cx, cy = int(lm.x * ancho), int(lm.y * alto)
        puntas_dedos.append((cx, cy))
    
    return puntas_dedos

def dibujar_puntos_mano(pantalla, hand_landmarks, ancho, alto):
    colores_dedos = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255)]
    nombres_dedos = ["PULGAR", "ÍNDICE", "MEDIO", "ANULAR", "MEÑIQUE"]
    
    try:
        for conexion in mp_manos.HAND_CONNECTIONS:
            inicio = hand_landmarks.landmark[conexion[0]]
            fin = hand_landmarks.landmark[conexion[1]]
        
            x1, y1 = int(inicio.x * ancho), int(inicio.y * alto)
            x2, y2 = int(fin.x * ancho), int(fin.y * alto)
            
            pygame.draw.line(pantalla, (255, 255, 255), (x1, y1), (x2, y2), 1)
            pygame.draw.line(pantalla, (0, 200, 0), (x1, y1), (x2, y2), 1)
        
        for i, landmark in enumerate(hand_landmarks.landmark):
            x, y = int(landmark.x * ancho), int(landmark.y * alto)
            
            if 0 <= x < ancho and 0 <= y < alto:
                if i in PUNTAS_DEDOS_INDICES:
                    indice_dedo = PUNTAS_DEDOS_INDICES.index(i)
                    
                    pygame.draw.circle(pantalla, (0, 0, 0), (x, y), 12, 1)  # Borde negro
                    pygame.draw.circle(pantalla, colores_dedos[indice_dedo], (x, y), 10)  # Circulo principal
                    
                    font = pygame.font.Font(None, 22)
                    texto = font.render(nombres_dedos[indice_dedo], True, colores_dedos[indice_dedo])
                    rect_texto = texto.get_rect(center=(x, y - 20))
                    
                    fondo = pygame.Surface((rect_texto.width + 6, rect_texto.height + 6), pygame.SRCALPHA)
                    fondo.fill((0, 0, 0, 200))
                    pantalla.blit(fondo, (rect_texto.x - 3, rect_texto.y - 3))
                    pantalla.blit(texto, rect_texto)
                else:
                    pygame.draw.circle(pantalla, (0, 200, 0), (x, y), 2)
    except Exception as e:
        print(f"Error al dibujar puntos de la mano: {e}")
        pass