import cv2
import pygame
import mediapipe as mp
import numpy as np
import time
import random
from mediapipe_utils import detectar_dedos, dibujar_puntos_mano
from pygame_utils import inicializar_pygame, dibujar_notas, dibujar_puntuacion
from sound_utils import reproducir_sonido, cargar_sonidos

def main():
    mp_manos = mp.solutions.hands
    manos = mp_manos.Hands(
        static_image_mode=False,
        max_num_hands=2,
        min_detection_confidence=0.7,
        min_tracking_confidence=0.5
    )
    
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: No se pudo abrir la cámara")
        return
    
    fullscreen = True
    pantalla, fuente = inicializar_pygame(fullscreen=fullscreen)
    ancho, alto = pygame.display.get_surface().get_size()
    fuente_grande = pygame.font.Font(None, 60)
    fuente_mediana = pygame.font.Font(None, 40)
    
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, ancho)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, alto)
    
    # Variables del juego
    notas = []
    puntuacion = 0
    combo = 0
    ultimo_tiempo_nota = time.time()
    
    # Frecuencia de generacion de notas y velocidad
    tiempo_entre_notas = 2.5 
    velocidad_notas = 1.5
    
    notas_musicales = ['do', 're', 'mi', 'fa', 'sol', 'la', 'si']
    cargar_sonidos(notas_musicales)
    
    radio_colision = 30
    notas_activadas = set()
    nombres_dedos = ["PULGAR", "ÍNDICE", "MEDIO", "ANULAR", "MEÑIQUE"]
    
    ultima_actualizacion_fps = time.time()
    fps_contador = 0
    fps_actual = 0
    manos_detectadas = False
    tiempo_sin_manos = 0 
    ultima_nota_activada = None
    debug_mode = False 
    pantalla_completa = fullscreen
    min_distancia_notas = ancho * 0.15
    estado_juego = "CUENTA_REGRESIVA"
    tiempo_inicio_cuenta = time.time()
    duracion_cuenta_regresiva = 10 

    ejecutando = True
    clock = pygame.time.Clock()
    
    while ejecutando:
        try:
            tiempo_actual = time.time()
            ret, frame = cap.read()
            if not ret:
                print("Error al capturar frame de la cámara")
                continue 
        
            frame = cv2.flip(frame, 1)
            frame = cv2.resize(frame, (ancho, alto))
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            resultados = manos.process(frame_rgb)
            frame_pygame = pygame.surfarray.make_surface(cv2.resize(frame_rgb, (ancho, alto)).swapaxes(0, 1))
            pantalla.blit(frame_pygame, (0, 0))
            overlay = pygame.Surface((ancho, alto), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 100))
            pantalla.blit(overlay, (0, 0))
            
            if estado_juego == "CUENTA_REGRESIVA":
                tiempo_transcurrido = tiempo_actual - tiempo_inicio_cuenta
                tiempo_restante = max(0, duracion_cuenta_regresiva - tiempo_transcurrido)
                panel_cuenta = pygame.Surface((ancho, alto // 2), pygame.SRCALPHA)
                panel_cuenta.fill((0, 0, 0, 180))
                pantalla.blit(panel_cuenta, (0, alto // 4))
                texto_titulo = fuente_grande.render("¡PREPÁRATE PARA JUGAR!", True, (255, 255, 0))
                rect_titulo = texto_titulo.get_rect(center=(ancho // 2, alto // 2 - 80))
                pantalla.blit(texto_titulo, rect_titulo)              
                segundos_restantes = int(tiempo_restante)
                texto_cuenta = fuente_grande.render(f"{segundos_restantes}", True, (255, 255, 255))
                rect_cuenta = texto_cuenta.get_rect(center=(ancho // 2, alto // 2))
                pantalla.blit(texto_cuenta, rect_cuenta)
                texto_instr1 = fuente_mediana.render("¡Toca las notas con las puntas de tus dedos!", True, (0, 255, 255))
                rect_instr1 = texto_instr1.get_rect(center=(ancho // 2, alto // 2 + 60))
                pantalla.blit(texto_instr1, rect_instr1)         
                texto_instr2 = fuente_mediana.render("ESC: Pausa | F: Pantalla completa | Q (en pausa): Salir", True, (255, 255, 255))
                rect_instr2 = texto_instr2.get_rect(center=(ancho // 2, alto // 2 + 110))
                pantalla.blit(texto_instr2, rect_instr2)
                
                if tiempo_restante <= 0:
                    estado_juego = "JUGANDO"
                    ultimo_tiempo_nota = tiempo_actual
            
            elif estado_juego == "JUGANDO":
                puntas_dedos = detectar_dedos(resultados, frame)
                
                manos_detectadas = resultados.multi_hand_landmarks is not None
                if not manos_detectadas:
                    tiempo_sin_manos += clock.get_time() / 1000 
                    if tiempo_sin_manos > 5:
                        estado_juego = "PAUSA"
                        tiempo_sin_manos = 0
                else:
                    tiempo_sin_manos = 0
                
                if manos_detectadas and tiempo_actual - ultimo_tiempo_nota > tiempo_entre_notas:
                    puede_crear_nota = True
                    nueva_nota = crear_nueva_nota(ancho)
                    
                    for nota in notas:
                        distancia = ((nueva_nota['x'] - nota['x'])**2 + (nueva_nota['y'] - nota['y'])**2)**0.5
                        if distancia < min_distancia_notas:
                            puede_crear_nota = False
                            break
                    
                    if puede_crear_nota and len(notas) < 5:
                        notas.append(nueva_nota)
                        ultimo_tiempo_nota = tiempo_actual
                        
                        # Ajustar dificultad
                        tiempo_entre_notas = max(1.8, tiempo_entre_notas * 0.998)  # Ajuste mas lento
                        velocidad_notas = min(3.0, velocidad_notas * 1.0005)  # Incremento mucho mas lento
            
                notas_activadas.clear()

                notas_para_eliminar = []
                for nota in notas:
                    nota['y'] += velocidad_notas
                    tamano_nota = 25
                    
                    color = obtener_color_nota(nota['sonido'])
                    pygame.draw.circle(pantalla, color, (nota['x'], int(nota['y'])), tamano_nota + 5)
                    pygame.draw.circle(pantalla, (255, 255, 255), (nota['x'], int(nota['y'])), tamano_nota)
                    pygame.draw.circle(pantalla, color, (nota['x'], int(nota['y'])), tamano_nota - 10)
                    texto_dedo = fuente.render(nombres_dedos[nota['indice_dedo']], True, (255, 255, 255))
                    rect_texto = texto_dedo.get_rect(center=(nota['x'], int(nota['y'])))
                    superficie_fondo = pygame.Surface((rect_texto.width + 10, rect_texto.height + 6), pygame.SRCALPHA)
                    superficie_fondo.fill((0, 0, 0, 180))
                    pantalla.blit(superficie_fondo, (rect_texto.x - 5, rect_texto.y - 3))
                    pantalla.blit(texto_dedo, rect_texto)
                    
                    if id(nota) not in notas_activadas and len(puntas_dedos) > 0:
                        indice_dedo = nota['indice_dedo']
                        if indice_dedo < len(puntas_dedos):
                            pos_dedo_x, pos_dedo_y = puntas_dedos[indice_dedo]
                            distancia = ((nota['x'] - pos_dedo_x) ** 2 + (nota['y'] - pos_dedo_y) ** 2) ** 0.5
                            
                            if distancia < radio_colision:
                                reproducir_sonido(nota['sonido'])
                                combo += 1
                                puntuacion += int(10 * (1 + combo/10))
                                notas_activadas.add(id(nota))
                                notas_para_eliminar.append(nota)
                                ultima_nota_activada = {
                                    'nota': nota['sonido'],
                                    'dedo': nombres_dedos[indice_dedo],
                                    'distancia': distancia
                                }
                            
                                for radio in range(40, 10, -10):
                                    pygame.draw.circle(pantalla, (255, 255, 255), 
                                                    (nota['x'], int(nota['y'])), radio, 2)
                    
                    if nota['y'] > alto + 20:
                        combo = 0 
                        notas_para_eliminar.append(nota)
                        texto_perdida = fuente.render("¡Nota perdida!", True, (255, 0, 0))
                        pantalla.blit(texto_perdida, (nota['x'] - 60, alto - 50))
                
                for nota in notas_para_eliminar:
                    if nota in notas:
                        notas.remove(nota)
                
                if resultados.multi_hand_landmarks:
                    for hand_landmarks in resultados.multi_hand_landmarks:
                        dibujar_puntos_mano(pantalla, hand_landmarks, ancho, alto)
                
                # Crear panel para puntuación en la parte superior
                panel_puntuacion = pygame.Surface((ancho, 50), pygame.SRCALPHA)
                panel_puntuacion.fill((0, 0, 0, 200))
                pantalla.blit(panel_puntuacion, (0, 0))
                
                # Mostrar puntuacion en el panel
                texto_puntuacion = fuente_mediana.render(f"Puntuación: {puntuacion}", True, (255, 255, 255))
                pantalla.blit(texto_puntuacion, (20, 10))
                
                # Mostrar combo
                if combo > 1:
                    texto_combo = fuente_mediana.render(f"Combo: x{combo}", True, (255, 215, 0))
                    pantalla.blit(texto_combo, (ancho - 200, 10))
                
                texto_instrucciones = fuente.render("¡Toca las notas con las puntas de tus dedos!", True, (255, 255, 255))
                rect_instrucciones = texto_instrucciones.get_rect(center=(ancho//2, 80))
                pantalla.blit(texto_instrucciones, rect_instrucciones)
                mostrar_leyenda_dedos(pantalla, ancho, alto, nombres_dedos)          
                texto_ayuda = fuente.render("ESC: Pausa | F: Pantalla completa", True, (255, 255, 255))
                pantalla.blit(texto_ayuda, (ancho - 350, alto - 35))
                
                if debug_mode:
                    fps_contador += 1
                    if tiempo_actual - ultima_actualizacion_fps > 1.0:
                        fps_actual = fps_contador
                        fps_contador = 0
                        ultima_actualizacion_fps = tiempo_actual
                        
                    texto_fps = fuente.render(f"FPS: {fps_actual}", True, (0, 255, 0))
                    pantalla.blit(texto_fps, (10, alto - 70))
                    
                    if ultima_nota_activada:
                        info = f"Nota: {ultima_nota_activada['nota']} | Dedo: {ultima_nota_activada['dedo']}"
                        texto_debug = fuente.render(info, True, (255, 255, 0))
                        pantalla.blit(texto_debug, (ancho // 2 - 200, 50))
            
            elif estado_juego == "PAUSA":
                panel_pausa = pygame.Surface((ancho, alto // 2), pygame.SRCALPHA)
                panel_pausa.fill((0, 0, 0, 200))
                pantalla.blit(panel_pausa, (0, alto // 4))
                
                # Mensaje de pausa
                texto_pausa = fuente_grande.render("JUEGO EN PAUSA", True, (255, 255, 255))
                rect_pausa = texto_pausa.get_rect(center=(ancho//2, alto//2 - 50))
                pantalla.blit(texto_pausa, rect_pausa)
                
                # Instrucciones para salir
                texto_regresar = fuente.render("ESC para volver al juego", True, (255, 255, 255))
                rect_regresar = texto_regresar.get_rect(center=(ancho//2, alto//2 + 60))
                pantalla.blit(texto_regresar, rect_regresar)
                
                texto_salir = fuente.render("Q para salir del juego", True, (255, 100, 100))
                rect_salir = texto_salir.get_rect(center=(ancho//2, alto//2 + 100))
                pantalla.blit(texto_salir, rect_salir)
            
                if resultados.multi_hand_landmarks:
                    tiempo_sin_manos = 0
            
            elif estado_juego == "FIN":
                # Superficie para el fondo
                fondo = pygame.Surface((ancho, alto), pygame.SRCALPHA)
                fondo.fill((0, 0, 0, 200))
                pantalla.blit(fondo, (0, 0))
                
                # Titulo
                texto_titulo = fuente_grande.render("¡FIN DEL JUEGO!", True, (255, 255, 255))
                rect_titulo = texto_titulo.get_rect(center=(ancho//2, alto//2 - 100))
                pantalla.blit(texto_titulo, rect_titulo)
                
                # Puntuacion
                texto_puntos = fuente_grande.render(f"Puntuación: {puntuacion}", True, (255, 215, 0))
                rect_puntos = texto_puntos.get_rect(center=(ancho//2, alto//2))
                pantalla.blit(texto_puntos, rect_puntos)
                
                # Instrucciones
                texto_salir = fuente.render("Presiona Q para salir", True, (255, 255, 255))
                rect_salir = texto_salir.get_rect(center=(ancho//2, alto//2 + 100))
                pantalla.blit(texto_salir, rect_salir)
            
            pygame.display.flip()
            
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    ejecutando = False
                elif evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_ESCAPE:
                        if estado_juego == "JUGANDO":
                            estado_juego = "PAUSA"
                        elif estado_juego == "PAUSA":
                            estado_juego = "JUGANDO"
                            ultimo_tiempo_nota = tiempo_actual

                    elif evento.key == pygame.K_q and (estado_juego == "PAUSA" or estado_juego == "FIN"):
                        ejecutando = False

                    elif evento.key == pygame.K_F1:
                        debug_mode = not debug_mode

                    elif evento.key == pygame.K_f:
                        pantalla_completa = not pantalla_completa
                        if pantalla_completa:
                            info = pygame.display.Info()
                            pantalla = pygame.display.set_mode((info.current_w, info.current_h), pygame.FULLSCREEN)
                        else:
                            pantalla = pygame.display.set_mode((800, 600))
                        ancho, alto = pygame.display.get_surface().get_size()
                elif evento.type == pygame.VIDEORESIZE:

                    if not pantalla_completa:
                        ancho, alto = evento.w, evento.h
                        pantalla = pygame.display.set_mode((ancho, alto), pygame.RESIZABLE)
            #FPS
            clock.tick(60)
            
        except Exception as e:
            print(f"Error en el bucle principal: {e}")
            continue
    
    cap.release()
    pygame.quit()
    cv2.destroyAllWindows()

def crear_nueva_nota(ancho):
    notas_musicales = ['do', 're', 'mi', 'fa', 'sol', 'la', 'si']
    margen = int(ancho * 0.20)
    espacio_disponible = ancho - 2 * margen
    num_secciones = 5
    ancho_seccion = espacio_disponible / num_secciones
    indice_dedo = random.randint(0, 4)
    pos_x = margen + indice_dedo * ancho_seccion + random.uniform(0, ancho_seccion)
    
    return {
        'x': int(pos_x),
        'y': 0,
        'sonido': random.choice(notas_musicales),
        'indice_dedo': indice_dedo,
        'tiempo_creacion': time.time()
    }

def obtener_color_nota(nota):
    """Devuelve un color según la nota musical"""
    colores = {
        'do': (255, 0, 0),
        're': (255, 165, 0),
        'mi': (255, 255, 0),
        'fa': (0, 255, 0),
        'sol': (0, 0, 255),
        'la': (75, 0, 130),
        'si': (148, 0, 211)
    }
    return colores.get(nota, (255, 255, 255))

def mostrar_leyenda_dedos(pantalla, ancho, alto, nombres_dedos):
    colores_dedos = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255)]
    fuente_pequena = pygame.font.Font(None, 22)
    panel = pygame.Surface((ancho, 35), pygame.SRCALPHA)
    panel.fill((0, 0, 0, 180))
    pantalla.blit(panel, (0, alto - 35))
    
    ancho_seccion = ancho // 5
    for i, nombre in enumerate(nombres_dedos):
        pygame.draw.circle(pantalla, colores_dedos[i], (i * ancho_seccion + 15, alto - 20), 8)
        texto = fuente_pequena.render(f"{nombre}", True, colores_dedos[i])
        pantalla.blit(texto, (i * ancho_seccion + 30, alto - 28))

if __name__ == "__main__":
    pygame.mixer.pre_init(44100, -16, 2, 512)
    pygame.init()
    main()