import pygame
import math
import os

def inicializar_pygame(fullscreen=False, ancho=800, alto=600, resizable=True):
    if not pygame.get_init():
        pygame.init()
    
    if not pygame.mixer.get_init():
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
    
    info_pantalla = pygame.display.Info()
    
    if fullscreen:
        ancho, alto = info_pantalla.current_w, info_pantalla.current_h
        pantalla = pygame.display.set_mode((ancho, alto), pygame.FULLSCREEN)
    else:
        flags = pygame.RESIZABLE if resizable else 0
        pantalla = pygame.display.set_mode((ancho, alto), flags)
    
    pygame.display.set_caption("MusicTech - Piano Virtual")
    
    try:
        if not os.path.exists('assets/fonts'):
            os.makedirs('assets/fonts', exist_ok=True)
            
        if os.path.exists('assets/fonts/font.ttf'):
            fuente = pygame.font.Font('assets/fonts/font.ttf', 28)
        else:
            fuente = pygame.font.Font(None, 28)
    except Exception:
        fuente = pygame.font.Font(None, 28) 

    return pantalla, fuente

def cambiar_modo_pantalla(pantalla_actual, fullscreen):
    info_pantalla = pygame.display.Info()
    
    if fullscreen:
        ancho, alto = info_pantalla.current_w, info_pantalla.current_h
        nueva_pantalla = pygame.display.set_mode((ancho, alto), pygame.FULLSCREEN)
    else:
        ancho_actual, alto_actual = pantalla_actual.get_size()
        nueva_pantalla = pygame.display.set_mode((ancho_actual, alto_actual), pygame.RESIZABLE)
    
    return nueva_pantalla

def manejar_eventos_ventana(evento, pantalla):
    if evento.type == pygame.VIDEORESIZE:
        return pygame.display.set_mode((evento.w, evento.h), pygame.RESIZABLE)
    elif evento.type == pygame.KEYDOWN:
        if evento.key == pygame.K_RETURN and (pygame.key.get_mods() & pygame.KMOD_ALT):
            is_fullscreen = pygame.display.get_surface().get_flags() & pygame.FULLSCREEN
            return cambiar_modo_pantalla(pantalla, not is_fullscreen)
    
    return pantalla

def dibujar_notas(pantalla, notas):
    try:
        for nota in notas:
            color = obtener_color_nota(nota['sonido'])
            
            tamano_nota = 30
            
            pygame.draw.circle(pantalla, color, (nota['x'], int(nota['y'])), tamano_nota)
            pygame.draw.circle(pantalla, (255, 255, 255), (nota['x'], int(nota['y'])), tamano_nota - 5)
            pygame.draw.circle(pantalla, color, (nota['x'], int(nota['y'])), tamano_nota - 10)
    except Exception as e:
        print(f"Error en dibujar_notas: {e}")
        
    return notas

def dibujar_puntuacion(pantalla, fuente, puntuacion, combo):
    try:
        ancho, alto = pantalla.get_size()
        
        panel = pygame.Surface((250, 120), pygame.SRCALPHA)
        panel.fill((0, 0, 0, 180))
        pantalla.blit(panel, (10, 10))
        
        pygame.draw.rect(pantalla, (255, 255, 255), (10, 10, 250, 120), 2)
        
        texto_puntuacion = fuente.render(f"Puntos: {puntuacion}", True, (255, 255, 255))
        pantalla.blit(texto_puntuacion, (20, 20))
        
        color_combo = (255, 255, 255)
        tamano_texto = 1.0 
        
        if combo >= 15:
            color_combo = (255, 0, 255)  
            tamano_texto = 1.2 + 0.05 * math.sin(pygame.time.get_ticks() / 100)
        elif combo >= 10:
            color_combo = (255, 215, 0) 
            tamano_texto = 1.1 + 0.05 * math.sin(pygame.time.get_ticks() / 150)
        elif combo >= 5:
            color_combo = (0, 255, 0) 
            tamano_texto = 1.05
        
        tamano_combo = min(int(28 * tamano_texto), 40)
        fuente_combo = pygame.font.Font(None, tamano_combo)
        texto_combo = fuente_combo.render(f"Combo: {combo}x", True, color_combo)
        x_combo = 20
        y_combo = 60
        
        pantalla.blit(texto_combo, (x_combo, y_combo))
        
        texto_multi = fuente.render(f"Multi: x{1 + combo/10:.1f}", True, (255, 165, 0))
        pantalla.blit(texto_multi, (20, 100))
    except Exception as e:
        print(f"Error en dibujar_puntuacion: {e}")
    
    return puntuacion, combo

def obtener_color_nota(nota):
    colores = {
        'do': (255, 0, 0),     # Rojo
        're': (255, 165, 0),   # Naranja
        'mi': (255, 255, 0),   # Amarillo
        'fa': (0, 255, 0),     # Verde
        'sol': (0, 0, 255),    # Azul
        'la': (75, 0, 130),    # Indigo
        'si': (148, 0, 211)    # Violeta
    }
    return colores.get(nota, (255, 255, 255)) 