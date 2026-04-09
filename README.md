# 📝 automatizateSeletores (Integração de Notas)

Um bot em Python desenvolvido para acabar com o trabalho manual de digitação de notas! Ele faz a ponte entre o seu sistema pessoal de notas e o portal oficial do Estado (Professor On-line), transferindo as notas automaticamente e atualizando os seletores de status.

---

## 🗂️ Estrutura do Projeto

O código foi pensado para ser simples e direto ao ponto:

```text
📦 automatizateSeletores
 ┣ 🐍 transferir_notas.py      # O código em Python (Lógica de extração e injeção)
 ┣ 🐍 trocar_seletores.py      # O código em Python simples de troca de seletor
 ┣ 📋 requirements.txt         # Arquivo com as bibliotecas necessárias
 ┗ 📖 README.md                # Documentação do projeto
```

---

## 🚀 Como funciona?

O script se conecta a uma janela do Google Chrome onde você já está logado. O robô faz o seguinte:
1. Navega até a aba do seu site pessoal (`profkazenski.com`).
2. Varre a sua tabela de alunos e guarda na memória o Nome e a Nota (já convertendo pontos para vírgulas).
3. Muda automaticamente para a aba do portal do Estado.
4. Procura o nome do aluno na tabela oficial, digita a nota extraída e altera o seletor de "Não Informado" para "Informado".

---

## 🛠️ Tecnologias

* **Python 3**
* **Selenium WebDriver**

---

## ⚙️ Como instalar e configurar (Do Zero Absoluto)

Se você nunca programou ou não tem as ferramentas instaladas, siga este passo a passo.

### 1. Preparando o Terreno (Instalações base)
* **Python:** Baixe e instale o [Python 3](https://www.python.org/downloads/). **⚠️ MUITO IMPORTANTE:** Na primeira tela do instalador, marque a caixinha **"Add python.exe to PATH"** antes de clicar em *Install Now*.
* **Editor de Código:** Recomendamos baixar e instalar o [Visual Studio Code (VS Code)](https://code.visualstudio.com/) para rodar o script facilmente.
* **Git (Opcional):** Para clonar o repositório via terminal, instale o [Git](https://git-scm.com/downloads). (Se preferir, você pode apenas clicar em *Code > Download ZIP* aqui no GitHub e extrair a pasta).

### 2. Baixe o projeto
Abra o seu terminal (ou o terminal dentro do VS Code) e rode:
```bash
git clone [https://github.com/Kazenski/automatizateSeletores.git](https://github.com/Kazenski/automatizateSeletores.git)
cd automatizateSeletores
```

### 3. Instale a biblioteca do Robô
Com o terminal aberto na pasta do projeto, instale o Selenium rodando o comando:
```bash
pip install -r requirements.txt
```

### 4. Inicie o Google Chrome em Modo Especial (Depuração)
Para que o bot consiga acessar suas abas sem pedir login ou ser bloqueado, abra o Chrome com uma "porta de comunicação" aberta.

Pressione `Windows + R` no seu teclado e cole o comando abaixo:
```cmd
"C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="C:\ChromeBotProfile"
```

### 5. Prepare a Tela para o Robô
Nesta nova janela do Chrome que se abriu, você precisa ter **duas abas** abertas:
1. **Aba 1:** O seu site pessoal (`profkazenski.com`) com as notas lançadas e a tabela visível na tela.
2. **Aba 2:** O portal do Professor On-line do Estado, logado e na página de lançamento da turma.

### 6. Execute a Mágica!
Com as duas abas abertas, volte ao VS Code, abra o arquivo `transferir_notas.py` e rode o script:
```bash
python transferir_notas.py
```

Acompanhe o terminal: ele vai te narrar exatamente quais notas está lendo e quais alunos está preenchendo no sistema do governo!

---

✍️ **Autor:** Professor Eduardo Kazenski  
Sinta-se livre para dar um ⭐ *Star*, fazer um *Fork* e contribuir com o projeto!
