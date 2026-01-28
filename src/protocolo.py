import struct

# Cabeçalho: Seq(I), Ack(I), Flags(B), Janela(H) -> Total 11 bytes
HEADER_FORMAT = "!IIBH"

def cifrar(data, chave):
    #lógica simples de XOR para cifrar os dados
    resultado = ""
    for char in data:
        # Aplica XOR entre o caractere e a chave
        resultado += chr(ord(char) ^ chave)
    return resultado

def criar_pacote(seq, ack, flags, window, payload, chave=None):
    # Criptografa o payload antes de transformar em bytes
    if chave and payload:
        payload = cifrar(payload, chave)
    
    header = struct.pack(HEADER_FORMAT, seq, ack, flags, window)
    return header + payload.encode('utf-8')

def desmontar_pacote(pacote_bruto, chave=None): # Desmonta o pacote bruto em seus componentes para o servidor ler os dados
    # Calcula o tamanho do cabeçalho
    header_size = struct.calcsize(HEADER_FORMAT)
    header_bin = pacote_bruto[:header_size]
    payload_bin = pacote_bruto[header_size:]
    
    # Desempacota o cabeçalho
    seq, ack, flags, window = struct.unpack(HEADER_FORMAT, header_bin)
    
    # Transforma o payload de volta em string
    payload = payload_bin.decode('utf-8', errors='ignore')
    
    # Se houver chave, decifra (XOR de novo desfaz a cifra)
    if chave and payload:
        payload = cifrar(payload, chave)
        
    return seq, ack, flags, window, payload