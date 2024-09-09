import streamlit as st
from pytubefix import YouTube
from pytubefix.cli import on_progress
from pytubefix.helpers import safe_filename
import os
import subprocess

# Título de la aplicación
st.title("Descargar Video y Audio de YouTube")

# Input para la URL del video de YouTube
url = st.text_input("Ingresa la URL del video de YouTube:")

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

# Función para combinar video y audio usando FFmpeg
def combine_video_audio(video_path, audio_path, output_path):
    try:
        # Ajustar el comando de FFmpeg
        command = f"ffmpeg -i {video_path} -i {audio_path} -c:v copy -c:a aac -strict experimental {output_path}"
        st.write(f"Comando FFmpeg: {command}")  # Mostrar el comando para depuración
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        
        # Mostrar salida de error si ocurre
        if result.returncode != 0:
            st.error(f"Error al combinar video y audio: {result.stderr}")
        else:
            st.success(f"Video y audio combinados en: {output_path}")
            return output_path
    except Exception as e:
        st.error(f"Error al combinar video y audio: {e}")
        return None

# Función para descargar video y audio por separado
def download_video_audio_separately(youtube_url, resolution):
    try:
        yt = YouTube(youtube_url, on_progress_callback=on_progress_callback)
        st.write(f"Título del video: {yt.title}")
        
        # Convertir la resolución a número (ej. '720p' -> 720)
        resolution_number = int(resolution[:-1])

        # Descargar video y audio por separado
        st.write(f"Descargando video y audio por separado para la resolución {resolution}...")
        
        # Filtrar el stream de video para la resolución seleccionada
        video_stream = yt.streams.filter(res=resolution, mime_type="video/mp4").first()
        # Filtrar el stream de solo audio
        audio_stream = yt.streams.filter(only_audio=True, mime_type="audio/mp4").first()

        if video_stream and audio_stream:
            # Descargar el video (sin audio)
            st.write("Descargando video...")
            video_filename = f"{safe_filename(yt.title)}_video_{resolution}.mp4"
            video_path = video_stream.download(filename=video_filename)
            st.write("Video descargado.")
            
            # Descargar el audio
            st.write("Descargando audio...")
            audio_filename = f"{safe_filename(yt.title)}_audio.mp4"
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

# Botón para descargar video y audio por separado
if st.button("Descargar Video y Audio por Separado"):
    if url:
        # Inicializar barra de progreso y texto de estado
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Descargar video y audio por separado
        video_path, audio_path = download_video_audio_separately(url, selected_resolution)
        
        # Mostrar los archivos descargados si fueron descargados correctamente
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
            
            # Opcional: Limpiar los archivos descargados si se desea
            # os.remove(video_path)
            # if audio_path:
            #     os.remove(audio_path)
    else:
        st.error("Por favor, ingresa una URL válida.")

# Botón para combinar video y audio
if st.button("Descargar y Combinar Video y Audio"):
    if url:
        # Inicializar barra de progreso y texto de estado
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Descargar video y audio por separado
        video_path, audio_path = download_video_audio_separately(url, selected_resolution)
        
        # Combinar video y audio si fueron descargados correctamente
        if video_path and audio_path:
            st.write("Combinando video y audio...")
            output_filename = f"{safe_filename(YouTube(url).title)}_combined_{selected_resolution}.mp4"
            output_path = combine_video_audio(video_path, audio_path, output_filename)
            
            # Mostrar el archivo combinado si fue generado correctamente
            if output_path:
                st.write("Reproduciendo video combinado:")
                with open(output_path, "rb") as combined_file:
                    combined_bytes = combined_file.read()
                    st.video(combined_bytes)

            # Opcional: Limpiar los archivos descargados si se desea
            # os.remove(video_path)
            # os.remove(audio_path)
            # os.remove(output_path)
    else:
        st.error("Por favor, ingresa una URL válida.")