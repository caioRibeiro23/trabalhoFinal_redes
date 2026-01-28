import socket
import time
from protocolo import criar_pacote, desmontar_pacote

# Configurações do Cliente
SERVER_ADDR = ("127.0.0.1", 5005) #IP e Porta do Servidor
CHAVE = 42 # Mesma chave que o servidor usa
TIMEOUT = 0.5 # Segundos para esperar o ACK

historico_cwnd = [] # Para guardar o histórico de cwnd para análise posterior

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # Cria o socket UDP
sock.settimeout(0.1) # Não trava o código se não receber nada

# Variáveis de Congestionamento (Item 4)
cwnd = 1
ssthresh = 64
proximo_seq = 0
base = 0
pacotes = ["Dado " + str(i) for i in range(10000)] # Simula os 10.000 pacotes

print("Iniciando transferência...")

import random

# Handshake para definir a chave de criptografia (Item 5)
print("Realizando Handshake e definindo chave...")
chave_proposta = random.randint(1, 255) # Número aleatório para ser a chave XOR

# Envio do SYN com a chave proposta
pdu_syn = criar_pacote(0, 0, 1, 1024, str(chave_proposta), chave=None) 
sock.sendto(pdu_syn, SERVER_ADDR) # Envia o SYN para o servidor

try:
    dados_ack, _ = sock.recvfrom(1024)
    _, ack_recebido, flags_ack, _, _ = desmontar_pacote(dados_ack, chave=None)
    
    if flags_ack == 2: # Esperamos um ACK (Flag 2)
        CHAVE = chave_proposta
        print(f"Handshake OK! Chave acordada: {CHAVE}")
except socket.timeout: # Timeout esperando o ACK - falha no handshake
    print("Erro no Handshake. O servidor está rodando?")
    exit()

window_receptor = 1024 # Inicialmente assume uma janela grande

while base < len(pacotes):
    janela_efetiva = min(cwnd, window_receptor if 'window_receptor' in locals() else 1024) #define a janela efetiva (mínimo entre cwnd e janela do receptor)
    # Envia pacotes dentro da janela (cwnd)
    while proximo_seq < base + janela_efetiva and proximo_seq < len(pacotes): # Enquanto há pacotes para enviar na janela
        pdu = criar_pacote(proximo_seq, 0, 0, 1024, pacotes[proximo_seq], CHAVE) # Cria o pacote
        sock.sendto(pdu, SERVER_ADDR) # Envia para o servidor
        print(f"Enviado: {proximo_seq} | cwnd: {cwnd}")
        proximo_seq += 1 # Incrementa o próximo seq a enviar

    # Espera pelos ACKs
    try:
        dados_ack, _ = sock.recvfrom(1024) # Espera o ACK do servidor
        _, ack_recebido, _, window_receptor, _ = desmontar_pacote(dados_ack, CHAVE) # Desmonta o pacote ACK
        print(f"Recebido ACK: {ack_recebido} | Janela Receptor: {window_receptor}")
        
        if ack_recebido >= base: # Se o ACK é novo
            # Move a janela para frente
            base = ack_recebido + 1
            # Lógica Slow Start (Item 4.2)
            if cwnd < ssthresh: # Mudança de fase para Congestion Avoidance
                cwnd *= 2 # Crescimento exponencial
            else:
                cwnd += 1 # Crescimento linear
            historico_cwnd.append(cwnd) # Guarda o histórico de cwnd
    except socket.timeout:
        # Timeout = Perda detectada
        print("TIMEOUT! Reduzindo fluxo...")
        ssthresh = max(cwnd // 2, 2) 
        cwnd = 1
        proximo_seq = base # Volta para o último confirmado (Go-Back-N simplificado)

print("Transferência concluída!")

with open("dados_vazao.txt", "w") as f: # Salva o histórico de cwnd em um arquivo
    for c in historico_cwnd:
        f.write(f"{c}\n")