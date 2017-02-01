# Melodia

Programa para compor e reproduzir músicas simples. Ele permite capturar sons de um microfone e tentar dizer qual a nota e escala do som.
É útil para quando você consegue assobiar a melodia da música, mas não sabe quais notas a compõem. ;)

*O código é um tanto velho. Tirei um pouco do "pó", mas ainda está bem ruinzinho...
**Use com Python 2**. Acho que só precisa mudar o "raw_input" para funcionar no Python3, mas o PyGTK2 não estava funcionando no Python3, então não testei.*


# Uso

Abra o programa (`python melodia.py` (sem interface gráfica) ou `python meloGui.py` (como interface gráfica)).

**Instruções para a versão com interface gráfica:**

(requer pygtk)

Escreva uma música como a do exemplo abaixo. Para tocar, selecione as notas que deseja (ou não selecione nada, para tocar tudo) e clique em "Reproduzir".

Exemplo arquivo de música:

do5/5 re5/5 re#5 o
re#5/5 fa5/5 sol5 o
sol5/5 la#5/5 fa5 sol5/6 fa5/6 re#5/5 re5/5 do5 o
do5/5 re5/5 re#5 o
re#5/5 fa5/5 sol5 o
sol5/5 la#5/5 do6 la#5/5 re6/5 do6 o
do6/5 re6/5 re#6 re6 do6 la#5 sol#5 sol5 fa5/3
re#5 re5 do5/3

- O primeiro número depois da nota é a escala.
- O número depois da barra é o tempo da nota. (Quanto menor, mais a nota dura)
- O "o" (letra ó) é um tempo sem som. Também é possível difinir a duração do tempo (ex.: o/3)

Gravar:

Existem duas formas de analisar sons externos para descobrir as notas:

- O botão "Gravar" na parte superior deve ir gravando cada som a cada 0.1s, converter para a nota e escrever como texto na posição do cursor.
- O botão "Gravar" na parte inferior grava o som, converte para nota e mostra do lado, sem adicionar no texto. Adicione a nota mostrada no texto apertando o botão "Sim".
