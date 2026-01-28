import matplotlib.pyplot as plt

def gerar_grafico():
    iteracoes = []
    cwnd_valores = []

    try:
        # Abre o arquivo gerado pelo seu cliente durante a transmissão
        with open('dados_vazao.txt', 'r') as f:
            for i, linha in enumerate(f):
                iteracoes.append(i)
                cwnd_valores.append(float(linha.strip()))

        # Configuração do gráfico
        plt.figure(figsize=(10, 6))
        plt.plot(iteracoes, cwnd_valores, label='Janela de Congestionamento (cwnd)', color='red')
        
        # Títulos e legendas para o padrão SBC
        plt.title('Controle de Congestionamento - Protocolo Trabalho Final Redes')
        plt.xlabel('Número da Transmissão (Pacotes)')
        plt.ylabel('Tamanho da Janela (cwnd)')
        plt.grid(True)
        plt.legend()

        # Salva a imagem para o seu relatório
        plt.savefig('grafico_vazao.png')
        print("Gráfico 'grafico_vazao.png' gerado com sucesso!")
        
        # Mostra o gráfico na tela
        plt.show()

    except FileNotFoundError:
        print("Erro: O arquivo 'dados_vazao.txt' não foi encontrado. Rode o client.py primeiro!")

if __name__ == "__main__":
    gerar_grafico()