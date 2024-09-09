import streamlit as st
from pytubefix import YouTube
from pytubefix.cli import on_progress
from pytubefix.helpers import safe_filename
import os

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

# Función para descargar video y audio
def download_video_audio(youtube_url, resolution):
    try:
        yt = YouTube(youtube_url, on_progress_callback=on_progress_callback)
        st.write(f"Título del video: {yt.title}")
        
        # Convertir la resolución a número (ej. '720p' -> 720)
        resolution_number = int(resolution[:-1])  

        if resolution_number >= 720:
            # Descargar video y audio por separado
            st.write("Resolución 720p o mayor detectada, descargando video y audio por separado...")
            
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
        
        else:
            # Descargar video con audio combinado (muxed) o video sin audio
            st.write("Resolución menor a 720p detectada, buscando video con audio combinado...")
            
            # Buscar el stream combinado (video + audio)
            combined_stream = yt.streams.filter(res=resolution, mime_type="video/mp4", progressive=True).first()

            if combined_stream:
                # Descargar el video con audio
                st.write("Descargando video con audio...")
                video_filename = f"{safe_filename(yt.title)}_combined_{resolution}.mp4"
                video_path = combined_stream.download(filename=video_filename)
                st.write("Video con audio descargado.")
                
                return video_path, None
            else:
                st.write("No se encontró stream con video y audio combinados. Descargando por separado...")
                
                # Descargar video y audio por separado si no hay combinación
                video_stream = yt.streams.filter(res=resolution, mime_type="video/mp4").first()
                audio_stream = yt.streams.filter(only_audio=True, mime_type="audio/mp4").first()

                if video_stream and audio_stream:
                    st.write("Descargando video sin audio...")
                    video_filename = f"{safe_filename(yt.title)}_video_{resolution}.mp4"
                    video_path = video_stream.download(filename=video_filename)
                    st.write("Descargando audio por separado...")
                    audio_filename = f"{safe_filename(yt.title)}_audio.mp4"
                    audio_path = audio_stream.download(filename=audio_filename)

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