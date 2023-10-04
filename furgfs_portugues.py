import os
import struct
class FURGfs:
    def __init__(self, caminho_fs):
        self.caminho_file_system = caminho_fs
        self.tamanho_do_bloco = 4096  # Tamanho do bloco - 4kb
        self.fat = []  # Tabela de alocação de arquivos
        self.arquivos = {}  # Dicionário para mapear nomes de arquivos para entradas na FAT

    def load_fs(self):
        if os.path.exists(self.caminho_file_system):
            with open(self.caminho_file_system, 'rb') as arquivo_fs:
                # Lê a tabela FAT e os dados dos arquivos
                dados = arquivo_fs.read()
                tamanho_cabecalho = struct.calctamanho('I')
                qtd_blocos = len(dados) // self.block_tamanho
                self.fat = struct.unpack(f'{qtd_blocos}I', dados[:tamanho_cabecalho])
                informacoes_dos_arquivos = dados[tamanho_cabecalho:]
                while informacoes_dos_arquivos:
                    tamanho_nome = struct.unpack('I', informacoes_dos_arquivos[:4])[0]
                    nome = struct.unpack(f'{tamanho_nome}s', informacoes_dos_arquivos[4:4 + tamanho_nome])[0].decode('utf-8')
                    tamanho, contagem_de_blocos = struct.unpack('II', informacoes_dos_arquivos[4 + tamanho_nome:8 + tamanho_nome])
                    blocos_dos_arquivos = struct.unpack(f'{contagem_de_blocos}I', informacoes_dos_arquivos[8 + tamanho_nome:8 + tamanho_nome + contagem_de_blocos * 4])
                    self.arquivos[len(self.arquivos)] = {
                        'nome': nome,
                        'tamanho': tamanho,
                        'blocos': list(blocos_dos_arquivos)
                    }
                    informacoes_dos_arquivos = informacoes_dos_arquivos[8 + tamanho_nome + contagem_de_blocos * 4:]

    def save_fs(self):
        with open(self.fs_path, 'wb') as arquivo_fs:
            # Salva a tabela FAT
            dados_tabela_fat = struct.pack(f'{len(self.fat)}I', *self.fat)
            arquivo_fs.write(dados_tabela_fat)

            # Salva os dados dos arquivos
            for informacoes_arquivo in self.arquivos.values():
                nome = informacoes_arquivo['nome'].encode('utf-8')
                tamanho_nome = len(nome)
                tamanho = informacoes_arquivo['tamanho']
                contagem_de_blocos = len(informacoes_arquivo['blocos'])
                blocos_dos_arquivos = struct.pack(f'{contagem_de_blocos}I', *informacoes_arquivo['blocos'])
                informacoes_dos_arquivos = struct.pack(f'I{tamanho_nome}sII', tamanho_nome, nome, tamanho, contagem_de_blocos) + blocos_dos_arquivos
                arquivo_fs.write(informacoes_dos_arquivos)
    
    def criar_fs(self, tamanho_do_fs):
        with open(self.caminho_file_system, 'wb') as arquivo_fs:
            arquivo_fs.truncate(tamanho_do_fs)
            quantidade_de_blocos = tamanho_do_fs // self.tamanho_do_bloco
            self.fat = [-1] * quantidade_de_blocos

    def copiar_para_fs(self, caminho_arquivo):
        if not os.path.exists(caminho_arquivo):
            print(f"O arquivo '{caminho_arquivo}' não existe.")
            return

        if not self.fat:
            print("O sistema de arquivos FURGfs não foi criado ainda.")
            return

        with open(caminho_arquivo, 'rb') as arquivo_fonte:
            dados_arquivo = arquivo_fonte.read()
            tamanho_arquivo = len(dados_arquivo)
            qtd_blocos_necessarios = (tamanho_arquivo + self.tamanho_do_bloco - 1) // self.tamanho_do_bloco

            blocos_livres = [i for i, bloco in enumerate(self.fat) if bloco == -1]
            if len(blocos_livres) < qtd_blocos_necessarios:
                print("Espaço insuficiente no FURGfs para copiar o arquivo.")
                return

            index_arquivo = len(self.arquivos)
            self.arquivos[index_arquivo] = {
                'nome': os.path.basenome(caminho_arquivo),
                'tamanho': tamanho_arquivo,
                'blocos': blocos_livres[:qtd_blocos_necessarios]
            }

            for bloco in self.arquivos[index_arquivo]['blocos']:
                self.fat[bloco] = index_arquivo

            with open(self.caminho_file_system, 'rb+') as arquivo_fs:
                for bloco in self.arquivos[index_arquivo]['blocos']:
                    deslocamento = bloco * self.tamanho_do_bloco
                    arquivo_fs.seek(deslocamento)
                    arquivo_fs.write(dados_arquivo[deslocamento : deslocamento + self.tamanho_do_bloco])

    def copiar_do_fs(self, index_arquivo, caminho_destino):
        if index_arquivo not in self.arquivos:
            print(f"O arquivo com o índice {index_arquivo} não existe no FURGfs.")
            return

        dados_arquivo = self.arquivos[index_arquivo]

        with open(self.caminho_file_system, 'rb') as arquivo_fs:
            with open(caminho_destino, 'wb') as arquivo_destino:
                for bloco in dados_arquivo['blocos']:
                    deslocamento = bloco * self.tamanho_do_bloco
                    arquivo_fs.seek(deslocamento)
                    arquivo_destino.write(arquivo_fs.read(dados_arquivo['tamanho']))

    def renomear_arquivo(self, index_arquivo, novo_nome):
        if index_arquivo not in self.arquivos:
            print(f"O arquivo com o índice {index_arquivo} não existe no FURGfs.")
            return

        self.arquivos[index_arquivo]['nome'] = novo_nome

    def remove_arquivo(self, index_arquivo):
        if index_arquivo not in self.arquivos:
            print(f"O arquivo com o índice {index_arquivo} não existe no FURGfs.")
            return

        for bloco in self.arquivos[index_arquivo]['blocos']:
            self.fat[bloco] = -1

        del self.arquivos[index_arquivo]

    def listar_arquivos(self):
        for index, dados_arquivo in self.arquivos.items():
            print(f"Índice: {index}, Nome: {dados_arquivo['nome']}, Tamanho: {dados_arquivo['tamanho']} bytes")

    def mostrar_espaço_livre(self):
        blocos_livres = sum(1 for bloco in self.fat if bloco == -1)
        total_blocos = len(self.fat)
        porcentagem_espaco_livre = (blocos_livres / total_blocos) * 100
        print(f"Espaço livre: {porcentagem_espaco_livre:.2f}%")
        print(f"Blocos livres: {blocos_livres}%")
        print(f"Quantidade total de blocos: {total_blocos}%")

if __nome__ == "__main__":
    fs = FURGfs("furgfs.fs")
    print("\nOperações disponíveis:")
    print("1. Criar FURGfs")
    print("2. Copiar arquivo para o FURGfs")
    print("3. Copiar arquivo do FURGfs")
    print("4. Renomear arquivo")
    print("5. Remover arquivo")
    print("6. Listar arquivos")
    print("7. Espaço livre")
    print("0. Sair")
    while True:
        
        choice = input("Digite o número da operação desejada: ")

        if choice == "1":
            tamanho = int(input("Digite o tamanho desejado para o FURGfs (em bytes): "))
            fs.criar_fs(tamanho)
            print("FURGfs criado com sucesso.")

        elif choice == "2":
            caminho_arquivo = input("Digite o caminho do arquivo que deseja copiar para o FURGfs: ")
            fs.copiar_para_fs(caminho_arquivo)

        elif choice == "3":
            index_arquivo = int(input("Digite o índice do arquivo que deseja copiar do FURGfs: "))
            caminho_destino = input("Digite o caminho para onde deseja copiar o arquivo: ")
            fs.copiar_do_fs(index_arquivo, caminho_destino)

        elif choice == "4":
            index_arquivo = int(input("Digite o índice do arquivo que deseja renomear: "))
            novo_nome = input("Digite o novo nome do arquivo: ")
            fs.renomear_arquivo(index_arquivo, novo_nome)

        elif choice == "5":
            index_arquivo = int(input("Digite o índice do arquivo que deseja remover: "))
            fs.remove_arquivo(index_arquivo)

        elif choice == "6":
            fs.listar_arquivos()

        elif choice == "7":
            fs.mostrar_espaço_livre()

        elif choice == "0":
            fs.save_fs()
            break
