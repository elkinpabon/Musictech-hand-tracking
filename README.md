# 🎵 MusicTech

**MusicTech** es un juego musical interactivo que utiliza el seguimiento y detección de manos mediante cámara para reproducir notas musicales con gestos.

---

## 🧠 Tecnologías utilizadas

- **Python**: Sistema de puntuacion, interfaz y logica general del juego.
- **OpenCV**: Captura de video.
- **MediaPipe**: Seguimiento de manos.
- **Pygame**: Reproducción de sonidos.
- **NumPy**: Generación de tonos personalizados.

---

## 🚀 ¿Cómo funciona?

El programa detecta la mano del usuario y calcula la distancia entre el pulgar y otros dedos. Cuando esa distancia es menor a un umbral, se interpreta como una pulsación y se reproduce una nota musical correspondiente.
El sistema detecta los aciertos, maneja un sistema de puntuacion por combos y penalizaciones si la nota no es tocada al momento de pasar por pantalla.

---

## 🎮 Controles por gestos

- Pulgar + Índice → Nota: `do`
- Pulgar + Medio → Nota: `re`
- Pulgar + Anular → Nota: `mi`
- Pulgar + Meñique → Nota: `fa`

Cada combinación genera un sonido en tiempo real basado en archivos `.wav` o en tonos generados dinámicamente si el archivo no existe.

---

## 📁 Estructura del proyecto

```
MusicTech/
│
├── musictech.py          # Archivo principal del juego
├── mediapipe_utils.py    # Funciones auxiliares de detección de manos
├── sound_utils.py        # Funciones de carga, reproducción y generación de sonidos
└── assets/
    └── notes/            # Carpeta con sonidos .wav para cada nota
```

---

## ▶️ Requisitos

Antes de ejecutar el proyecto, asegúrate de tener instaladas las siguientes dependencias:

```bash
pip install opencv-python mediapipe pygame numpy
```

---

## 🧹 Ejecución

Desde la raíz del proyecto, corre el archivo principal:

```bash
python musictech.py
```

---

## 📌 Notas adicionales

- Si no se encuentran archivos `.wav`, se generará un tono personalizado con envolvente ADSR.
- Puedes expandir el repertorio de notas agregando más sonidos a `assets/notes/`.

---

## 📜 Licencia

Este proyecto está bajo la licencia MIT. Puedes usarlo, modificarlo y distribuirlo libremente.

---

Desarrollado con ❤️ por Elkin Pabon / Elkinext Solutions.

