# furgFS

Especificações:
Trabalho III – Especificação – FURGfs
O FURGfs é um pequeno sistema de arquivos que reside inteiramente dentro de um
outro arquivo a ser armazenado em um sistema de arquivos real. Ele usa conceitos
vistos em aula como FAT (tabela de alocação de arquivos) e operações sobre arquivos.
O FURGfs suporta apenas um diretório (raiz) e um número finito (e > 100) de
arquivos. Não é necessário tratar desfragmentação. Sua tarefa é criar um programa
que implementa o FURGfs. As operações suportadas são:

1. criar um FURGfs no tamanho escolhido pelo usuário (você pode delimitar opções
tamanhos mínimos e máximos, desde que mínimo̸ = máximo)
• está opção resultará na criação de um novo arquivo no sistema de arquivos real (e.g.,
trabalhos/SO/furgfs1.fs)
• este novo arquivo terá o tamanho escolhido para o FURGfs
• i.e., se o usuário escolheu criar um sistema de arquivos de 200MB, o arquivo
furgfs1.fs terá 200MB.
2. copiar um arquivo de um sistema de arquivos real (disco, pendrive, etc) p/ dentro
do FURGfs
3. copiar um arquivo de dentro do FURGfs p/ um sistema de arquivos real (disco,
pendrive, etc)
4. renomear um arquivo armazenado no FURGfs
5. remover um arquivo armazenado no FURGfs
6. listar todos os arquivos armazenados no FURGfs
7. listar o espaço livre em relação ao total do FURGfs
• e.g., 101MB livres de 200MB
