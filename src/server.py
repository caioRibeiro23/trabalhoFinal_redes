import socket
import random
from protocolo import desmontar_pacote # Importa a lógica de desmontar pacotes do protocolo

# Configurações do servidor
IP = "127.0.0.1"
PORTA = 5005
CHAVE_CRIPTO = 42 # Mesma chave que o cliente deve usar
TAXA_PERDA = 0.1  # 10% de chance de perder o pacote (Item 6.2)

# Cria o socket UDP
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((IP, PORTA))

print(f"Servidor rodando em {IP}:{PORTA}...")

buffer_recepcao = {} # Dicionário para guardar pacotes fora de ordem
proximo_esperado = 0 # O primeiro seq que esperamos é o 0

while True:
    # Recebe os bytes brutos da rede
    dados_brutos, addr = sock.recvfrom(2048)

    # Simulação de Perda (Requisito 6.2) 
    if random.random() < TAXA_PERDA:
        print(f"DEBUG: Pacote ignorado para simular perda de rede.")
        continue # Simplesmente ignora e não envia ACK

    # Processamento do Protocolo
    try:
        seq, ack, flags, window, payload = desmontar_pacote(dados_brutos, chave=CHAVE_CRIPTO)

        if seq == proximo_esperado:
            # Pacote na ordem correta
            print(f"  Entregando para aplicação: {payload}")
            proximo_esperado += 1
            
            # Verifica se o próximo já está no buffer (pacotes que chegaram adiantados)
            while proximo_esperado in buffer_recepcao:
                conteudo = buffer_recepcao.pop(proximo_esperado) # Remove do buffer
                print(f"  Entregando do buffer: {conteudo}")
                proximo_esperado += 1 # Incrementa o próximo esperado
        elif seq > proximo_esperado: # Pacote fora de ordem
            print(f"  Pacote {seq} fora de ordem. Guardando no buffer.")
            buffer_recepcao[seq] = payload # Guarda no buffer
        
        print(f"Recebido de {addr}:")
        print(f"  Seq: {seq} | ACK: {ack} | Flags: {flags} | Janela: {window}")
        print(f"  Mensagem Decifrada: {payload}")

        # Lógica de Resposta (ACK)
        # Preparação do ACK. O 'ack_num' é o 'seq' que acabou de ser recebido.
        # A janela (window) diz ao cliente nosso limite de buffer (ex: 10 pacotes)
        janela_disponivel = 10 
        
        # Importação do criar_pacote aqui para evitar importação circular
        from protocolo import criar_pacote
        
        pacote_ack = criar_pacote(
            seq=0,               # Seq do ACK é 0 (não usado aqui)
            ack=seq,             # Confirmando o seq recebido
            flags=2,             # Flag 2 = ACK (valor arbitrário para ACK)
            window=janela_disponivel,
            payload="ACK"        # Payload simples indicando ACK
        )

        # Envia o ACK de volta ao cliente
        sock.sendto(pacote_ack, addr)
        print(f"  ACK {seq} enviado com sucesso!")
    except Exception as e:
        print(f"Erro ao processar o pacote: {e}")