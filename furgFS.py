import os # Fazer a comunicação com o sistema operacional
import pickle # Biblioteca para serializar e deserializar objetos (estruturas) python

class FURGfs:
    def __init__(self, caminho_fs):
        self.caminho_file_system = caminho_fs
        self.tamanho_do_bloco = 4096  # Tamanho do bloco - 4kb
        self.fat = []  # Tabela de alocação de arquivos
        self.arquivos = {}  # Dicionário para mapear infos de arquivos para entradas na FAT
        self.carregar_fs()

    def carregar_fs(self):
        if os.path.exists(self.caminho_file_system):
            with open(self.caminho_file_system, 'rb') as arquivo_fs:
                dados = pickle.load(arquivo_fs) # Deserializa os dados salvos
                self.fat = dados['fat'] # Atribui o cabeçalho
                self.arquivos = dados['arquivos'] # Atribui os dados dos arquivos

    def salvar_fs(self):
        dados = {
            'fat': self.fat, # Cabeçalho 
            'arquivos': self.arquivos # Dados dos arquivos
        }
        with open(self.caminho_file_system, 'wb') as arquivo_fs:
            pickle.dump(dados, arquivo_fs) # Salvar os arquivos -> serializando dentro do furgfs 
    
    def criar_fs(self, tamanho_do_fs):
        if os.path.exists(self.caminho_file_system): # Checa se o FS existe
            print("Sistema de arquivos já existe!")
        else: # Se não existir, podemos criá-lo
            with open(self.caminho_file_system, 'wb') as arquivo_fs:
                arquivo_fs.truncate(tamanho_do_fs) # Aloca em disco o tamanho informado pelo usuário
                quantidade_de_blocos = tamanho_do_fs // self.tamanho_do_bloco
                self.fat = [-1] * quantidade_de_blocos # Para cada bloco existente, se ele estiver fazio terá valor -1

    def copiar_para_fs(self, caminho_arquivo):
        # Checagens necessárias para que consigamos copiar os arquivos para o nosso FS
        if not os.path.exists(caminho_arquivo):
            print(f"O arquivo '{caminho_arquivo}' não existe.")
            return

        if not self.fat:
            print("O sistema de arquivos FURGfs não foi criado ainda.")
            return
        # ----------------------------------------------------------------

        with open(caminho_arquivo, 'rb') as arquivo_fonte:
            dados_arquivo = arquivo_fonte.read()
            tamanho_arquivo = len(dados_arquivo)
            # Número de blocos que o arquivo ocupará
            qtd_blocos_necessarios = (tamanho_arquivo + self.tamanho_do_bloco - 1) // self.tamanho_do_bloco 

            # Verificação se existe espaço necessário para guardar o arquivo
            blocos_livres = [i for i, bloco in enumerate(self.fat) if bloco == -1] # Lista de índices dos blocos livres 
            if len(blocos_livres) < qtd_blocos_necessarios:
                print("Espaço insuficiente no FURGfs para copiar o arquivo.")
                return

            # Sempre adicionará o final, funciona como um AUTOIMPLEMENT no Postgre, tipo um contador
            index_arquivo = len(self.arquivos) # Tipo uma 'chave primária' para acesso através do dicionário python
            self.arquivos[index_arquivo] = {
                'nome': os.path.basename(caminho_arquivo), # Nome o arquivo com a extensão (ex: .jpeg, .png)
                'tamanho': tamanho_arquivo, # Tamanho em bytes
                'blocos': blocos_livres[:qtd_blocos_necessarios] # Blocos que onde esse arquivo será armazenado
            }

            # Pedaço de código para dizer que aquele bloco será utilizado pelo arquivo X através do índice dele  
            for bloco in self.arquivos[index_arquivo]['blocos']:
                self.fat[bloco] = index_arquivo 

            # Finalmente escrevendo os dados do arquivo no furgfs.fs
            with open(self.caminho_file_system, 'rb+') as arquivo_fs:
                for bloco in self.arquivos[index_arquivo]['blocos']:
                    deslocamento = bloco * self.tamanho_do_bloco # O quanto precisamos deslocar na lista para conseguirmos armazenar o bloco
                    arquivo_fs.seek(deslocamento) # "pula" até o pedaço do arquivo, o tamanho "pulado" (numero de bytes) é determinado pela variável deslocamento 
                    arquivo_fs.write(dados_arquivo[deslocamento : deslocamento + self.tamanho_do_bloco]) # Escrevendo os dados do arquivo nos blocos dentro do FS

    def copiar_do_fs(self, index_arquivo, caminho_destino):
        if index_arquivo not in self.arquivos: #verificando se o arquivo com o índice especificado (index_arquivo) existe no sistema de arquivos
            print(f"O arquivo com o índice {index_arquivo} não existe no FURGfs.")
            return

        dados_arquivo = self.arquivos[index_arquivo] #Se o arquivo com o índice especificado existir, este trecho de código recupera os dados desse arquivo do dicionário self.arquivos

        with open(self.caminho_file_system, 'rb') as arquivo_fs: #abre o arquivo do sistema de arquivos para leitura binária com o caminho dado em self.caminho_file_system.
            with open(caminho_destino, 'wb') as arquivo_destino: #abre um arquivo de destino no caminho especificado para escrita binária. Este é o local onde o arquivo será copiado
                for bloco in dados_arquivo['blocos']: #o loop itera pelos blocos do arquivo que precisam ser copiados.
                    deslocamento = bloco * self.tamanho_do_bloco #o quanto precisamos deslocar na lista para conseguirmos armazenar o bloco
                    arquivo_fs.seek(deslocamento) #"pula" até o pedaço do arquivo, o tamanho "pulado" (numero de bytes) é determinado pela variável deslocamento
                    arquivo_destino.write(arquivo_fs.read(dados_arquivo['tamanho'])) # o código lê os dados do arquivo do sistema, com base no tamanho do arquivo, e escreve esses dados no arquivo de destino

    def renomear_arquivo(self, index_arquivo, novo_nome): 
        if index_arquivo not in self.arquivos: 
            print(f"O arquivo com o índice {index_arquivo} não existe no FURGfs.")
            return

        self.arquivos[index_arquivo]['nome'] = novo_nome # esta linha atualiza o nome do arquivo 'nome' no dicionário self.arquivos para o novo nome especificado em 'novo_nome'

    def remove_arquivo(self, index_arquivo):
        if index_arquivo not in self.arquivos:
            print(f"O arquivo com o índice {index_arquivo} não existe no FURGfs.")
            return

        for bloco in self.arquivos[index_arquivo]['blocos']: #caso o arquivo com o índice especificado existir, este loop itera pelos blocos que compõem o arquivo
            self.fat[bloco] = -1 #libera os blocos do arquivo, tornando-os disponíveis para uso futuro

        del self.arquivos[index_arquivo] #remove o registro do arquivo do dicionário

    def listar_arquivos(self):
        for index, dados_arquivo in self.arquivos.items(): #loop itera pelos itens do dicionário self.arquivos, onde as informações sobre os arquivos estão armazenadas.
            print(f"Índice: {index}, Nome: {dados_arquivo['nome']}, Tamanho: {dados_arquivo['tamanho']} bytes") #para cada arquivo encontrado no sistema de arquivos, esta linha imprime informações sobre o arquivo

    def mostrar_espaço_livre(self):
        blocos_livres = sum(1 for bloco in self.fat if bloco == -1) #calcula o número de blocos livres no sistema de arquivos
        total_blocos = len(self.fat) #calcula o número total de blocos no sistema de arquivos
        porcentagem_espaco_livre = (blocos_livres / total_blocos) * 100 #calcula a porcentagem do espaço livre em relação ao espaço total disponível
        print(f"Espaço livre: {porcentagem_espaco_livre:.2f}%") ##imprime a porcentagem de espaço livre
        print(f"Blocos livres: {blocos_livres}")
        print(f"Quantidade total de blocos: {total_blocos}")

if __name__ == "__main__":
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
        
        choice = input("Digite o número da operação desejada: ") #solicita ao usuário que insira o número correspondente à operação desejada

        if choice == "1": #cria um sistema de arquivos (FURGfs) com o tamanho especificado pelo usuário
            tamanho = int(input("Digite o tamanho desejado para o FURGfs (em bytes): "))
            fs.criar_fs(tamanho)
            print("FURGfs criado com sucesso.")

        elif choice == "2": #permite ao usuário copiar um arquivo para o sistema de arquivos.
            caminho_arquivo = input("Digite o caminho do arquivo que deseja copiar para o FURGfs: ")
            fs.copiar_para_fs(caminho_arquivo)

        elif choice == "3": #permite ao usuário copiar um arquivo do sistema de arquivos para um destino específico.
            index_arquivo = int(input("Digite o índice do arquivo que deseja copiar do FURGfs: "))
            caminho_destino = input("Digite o caminho para onde deseja copiar o arquivo: ")
            fs.copiar_do_fs(index_arquivo, caminho_destino)

        elif choice == "4": #permite ao usuário renomear um arquivo no sistema de arquivos
            index_arquivo = int(input("Digite o índice do arquivo que deseja renomear: "))
            novo_nome = input("Digite o novo nome do arquivo: ")
            fs.renomear_arquivo(index_arquivo, novo_nome)

        elif choice == "5": #permite ao usuário remover um arquivo do sistema de arquivos
            index_arquivo = int(input("Digite o índice do arquivo que deseja remover: "))
            fs.remove_arquivo(index_arquivo)

        elif choice == "6": #lista os arquivos presentes no sistema de arquivos
            fs.listar_arquivos()

        elif choice == "7": #mostra informações sobre o espaço livre no sistema de arquivos
            fs.mostrar_espaço_livre()

        elif choice == "0": #Encerra o programa após salvar as alterações no sistema de arquivos
            fs.salvar_fs()
            break
