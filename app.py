import streamlit as st
import threading
import time
import sys
from io import StringIO

# Cria uma área no Streamlit para mostrar logs
log_area = st.empty()

# Cria um buffer para armazenar os logs
log_buffer = StringIO()


# Função para redirecionar os prints/logs
class StreamToLogger:
    def __init__(self, buffer):
        self.buffer = buffer

    def write(self, message):
        if message.strip() != "":
            self.buffer.write(message)
            self.buffer.flush()

    def flush(self):
        pass


# Redireciona stdout
sys.stdout = StreamToLogger(log_buffer)


# Função que simula logs acontecendo
def gerar_logs():
    for i in range(1, 21):
        print(f"Log número {i}")
        time.sleep(1)


# Thread para não travar o Streamlit
thread = threading.Thread(target=gerar_logs)
thread.start()

# Atualiza a área de logs em tempo real
while thread.is_alive():
    log_area.text(log_buffer.getvalue())
    time.sleep(0.5)

# Mostra logs finais
log_area.text(log_buffer.getvalue())
