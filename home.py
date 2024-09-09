import streamlit as st
from pytube import YouTube
import os
import time
import random

# Título de la aplicación
st.title("Descargar Video y Audio de YouTube")

# Input para la URL del video de YouTube
url = st.text_input("Ingresa la URL del video de YouTube:")

# Input para el retraso entre descargas
sleep_time_min = st.slider("Tiempo mínimo de retraso (en segundos) entre la descarga del video y el audio:", min_value=0, max_value=60, value=5)
sleep_time_max = st.slider("Tiempo máximo de retraso (en segundos) entre la descarga del video y el audio:", min_value=0, max_value=60, value=10)

# Barra de progreso
progress_bar = None
status_text = None

# Función para manejar el progreso de descarga
def on_progress_callback(stream, chunk, bytes_remaining):
    total_size = stream.filesize
    bytes_downloaded = total_size - bytes_remaining
    percentage_of_completion = bytes_downloaded / total_size * 100

    # Actualizar barra de progreso
    if progress_bar and status_text:
        progress_bar.progress(percentage_of_completion / 100)
        status_text.text(f"Descargando: {int(percentage_of_completion)}%")

# Función para descargar video y audio
def download_video_audio(youtube_url, resolution):
    try:
        yt = YouTube(youtube_url, on_progress_callback=on_progress_callback)
        st.write(f"Título del video: {yt.title}")

        # Descargar video y audio por separado
        st.write("Descargando video y audio por separado...")
        
        # Filtrar el stream de video para la resolución seleccionada
        video_stream = yt.streams.filter(res=resolution, mime_type="video/mp4").first()
        # Filtrar el stream de solo audio
        audio_stream = yt.streams.filter(only_audio=True, mime_type="audio/mp4").first()

        if video_stream and audio_stream:
            # Descargar el video (sin audio)
            st.write("Descargando video...")
            video_filename = f"{yt.title}_video_{resolution}.mp4"
            video_path = video_stream.download(filename=video_filename)
            st.write("Video descargado.")
            
            # Retrasar la descarga de audio para evitar detección de bot
            sleep_time = random.uniform(sleep_time_min, sleep_time_max)
            st.write(f"Esperando {sleep_time:.2f} segundos antes de descargar el audio...")
            time.sleep(sleep_time)

            # Descargar el audio
            st.write("Descargando audio...")
            audio_filename = f"{yt.title}_audio.mp4"
            audio_path = audio_stream.download(filename=audio_filename)
            st.write("Audio descargado.")

            return video_path, audio_path
        else:
            st.error("No se encontraron streams de video o audio adecuados.")
            return None, None

    except Exception as e:
        st.error(f"Error al descargar el video: {e}")
        return None, None

# Mostrar opciones de resolución
resolutions = ['144p', '360p', '480p', '720p', '1080p']
selected_resolution = st.selectbox("Selecciona la resolución de descarga:", resolutions)

# Botón para descargar el video
if st.button("Descargar Video y Audio"):
    if url:
        # Inicializar barra de progreso y texto de estado
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Llamar a la función de descarga
        video_path, audio_path = download_video_audio(url, selected_resolution)
        
        # Mostrar el video y el audio si fueron descargados correctamente
        if video_path:
            st.write("Reproduciendo video:")
            with open(video_path, "rb") as video_file:
                video_bytes = video_file.read()
                st.video(video_bytes)
            
            if audio_path:
                st.write("Reproduciendo audio:")
                with open(audio_path, "rb") as audio_file:
                    audio_bytes = audio_file.read()
                    st.audio(audio_bytes)
            
            # Limpiar los archivos descargados si deseas
            os.remove(video_path)
            if audio_path:
                os.remove(audio_path)
    else:
        st.error("Por favor, ingresa una URL válida.")