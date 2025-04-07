import pygame
import os
import numpy as np

sonidos_cache = {}

def cargar_sonidos(notas_musicales):
    for nota in notas_musicales:
        try:
            ruta_sonido = f'assets/notes/{nota}.wav'
            
            if not os.path.exists(ruta_sonido):
                os.makedirs('assets/notes', exist_ok=True)
                buffer = generar_tono(obtener_frecuencia(nota))
                continue
            
            sonido = pygame.mixer.Sound(ruta_sonido)
            sonidos_cache[nota] = sonido
            
        except Exception as e:
            print(f"Error al cargar sonido {nota}: {e}")
            buffer = generar_tono(obtener_frecuencia(nota))
            sonidos_cache[nota] = buffer

def reproducir_sonido(nombre_sonido, solo_cargar=False):
    if nombre_sonido in sonidos_cache:
        sonido = sonidos_cache[nombre_sonido]
        if not solo_cargar:
            sonido.play()
        return sonido
    else:
        try:
            ruta_sonido = f'assets/notes/{nombre_sonido}.wav'
            
            if not os.path.exists(ruta_sonido):
                sonido = generar_tono(obtener_frecuencia(nombre_sonido))
                sonidos_cache[nombre_sonido] = sonido
                if not solo_cargar:
                    sonido.play()
                return sonido
            
            sonido = pygame.mixer.Sound(ruta_sonido)
            sonidos_cache[nombre_sonido] = sonido
            
            if not solo_cargar:
                sonido.play()
            return sonido
            
        except Exception as e:
            print(f"Error al cargar sonido {nombre_sonido}: {e}")
            sonido = generar_tono(obtener_frecuencia(nombre_sonido))
            if not solo_cargar:
                sonido.play()
            return sonido

def generar_tono(frecuencia, duracion=0.3, volumen=0.5):
    try:
        sample_rate = 44100
        
        # onda sinusoidal
        t = np.linspace(0, duracion, int(duracion * sample_rate), False)
        tono = np.sin(frecuencia * t * 2 * np.pi)
        
        ataque = 0.05
        decaimiento = 0.1
        sostenimiento = 0.7
        liberacion = 0.2
        
        n_ataque = int(ataque * sample_rate)
        n_decaimiento = int(decaimiento * sample_rate)
        n_sostenimiento = int((duracion - ataque - decaimiento - liberacion) * sample_rate)
        n_liberacion = int(liberacion * sample_rate)
        
        envolvente = np.concatenate([
            np.linspace(0, 1, n_ataque),
            np.linspace(1, sostenimiento, n_decaimiento),
            np.ones(n_sostenimiento) * sostenimiento,
            np.linspace(sostenimiento, 0, n_liberacion)
        ])
        
        if len(envolvente) > len(tono):
            envolvente = envolvente[:len(tono)]
        else:
            envolvente = np.pad(envolvente, (0, len(tono) - len(envolvente)), 'constant')
        
        tono = (tono * envolvente * volumen)    
        tono = np.clip(tono, -1.0, 1.0).astype(np.float32)
        tono_stereo = np.vstack((tono, tono)).T
        buffer = pygame.sndarray.make_sound(tono_stereo)
        return buffer
        
    except Exception as e:
        print(f"Error al generar tono: {e}")
        dummy_sound = pygame.mixer.Sound(buffer=bytes(10))
        return dummy_sound

def obtener_frecuencia(nota):
    frecuencias = {
        'do': 261.63, 
        're': 293.66, 
        'mi': 329.63, 
        'fa': 349.23, 
        'sol': 392.00, 
        'la': 440.00, 
        'si': 493.88 
    }
    return frecuencias.get(nota, 440.00)