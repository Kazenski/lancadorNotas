from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
import time


def integrar_sistemas():
    # Pergunta qual nota o usuário deseja lançar antes de iniciar o robô
    print("\n" + "="*40)
    escolha_nota = input(
        "Qual nota deseja lançar? (N1, N2, N3 ou N4): ").strip().upper()

    # Mapeamento da coluna baseado no seu site:
    # Geralmente: N1 está no input 0, N2 no 1, N3 no 2, N4 no 3 dentro da célula de notas
    mapa_colunas = {
        "N1": 0,
        "N2": 1,
        "N3": 2,
        "N4": 3
    }

    if escolha_nota not in mapa_colunas:
        print(
            f"ERRO: '{escolha_nota}' não é uma opção válida. Use N1, N2, N3 ou N4.")
        return

    indice_nota = mapa_colunas[escolha_nota]

    chrome_options = Options()
    chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")

    print("\nConectando ao navegador aberto...")
    try:
        driver = webdriver.Chrome(options=chrome_options)
        wait = WebDriverWait(driver, 10)
    except Exception:
        print("Erro: Não foi possível conectar ao Chrome na porta 9222.")
        return

    print(f"\n--- INICIANDO INTEGRAÇÃO DE NOTAS: {escolha_nota} ---")

    aba_estado = None
    aba_meu_site = None

    for handle in driver.window_handles:
        driver.switch_to.window(handle)
        url_atual = driver.current_url.lower()

        if "profkazenski.com" in url_atual:
            aba_meu_site = handle
        elif "professoronline" in url_atual or "sed.sc.gov.br" in url_atual:
            aba_estado = handle

    if not aba_estado or not aba_meu_site:
        print(
            "ERRO: Certifique-se de que a aba do seu site e a aba do Estado estão abertas!")
        return

    # 1. LER NOTAS DO SEU SITE
    driver.switch_to.window(aba_meu_site)
    print(f"\n[1/2] Extraindo {escolha_nota} do site profkazenski.com...")
    time.sleep(2)

    dicionario_notas = {}

    try:
        wait.until(EC.presence_of_element_located((By.XPATH, "//tbody/tr")))
        linhas_meu_site = driver.find_elements(By.XPATH, "//tbody/tr")

        for linha in linhas_meu_site:
            tds = linha.find_elements(By.TAG_NAME, "td")

            if len(tds) < 4:
                continue

            nome_aluno = tds[1].text.strip().upper()
            if nome_aluno == "":
                continue

            # Localiza todos os inputs de nota na célula correspondente
            inputs_nota = tds[3].find_elements(By.TAG_NAME, "input")

            # Verifica se o índice solicitado existe na linha (ex: N1=0, N2=1...)
            if len(inputs_nota) > indice_nota:
                valor_nota = inputs_nota[indice_nota].get_attribute("value")

                if valor_nota and valor_nota.strip() != "":
                    print(
                        f"    [+] Lido: {nome_aluno} | {escolha_nota}: {valor_nota}")
                    nota_formatada = str(valor_nota).replace(".", ",")
                    dicionario_notas[nome_aluno] = nota_formatada
                else:
                    print(
                        f"    [-] Ignorado: {nome_aluno} (Sem {escolha_nota})")

        print(
            f"\n-> Sucesso! {len(dicionario_notas)} notas de {escolha_nota} guardadas.")

    except Exception as e:
        print(f"Erro ao ler as notas: {str(e)}")
        return

    if len(dicionario_notas) == 0:
        print("Nenhuma nota encontrada. Cancelando.")
        return

    # 2. PREENCHER O PORTAL DO ESTADO
    driver.switch_to.window(aba_estado)
    print(f"\n[2/2] Injetando {escolha_nota} no portal do Estado...")
    time.sleep(1.5)

    try:
        linhas_estado = driver.find_elements(
            By.XPATH, "//tr[contains(@id, 'Grid1ContainerRow')]")
        alunos_atualizados = 0

        for i in range(len(linhas_estado)):
            try:
                tabela_atualizada = driver.find_elements(
                    By.XPATH, "//tr[contains(@id, 'Grid1ContainerRow')]")
                if i >= len(tabela_atualizada):
                    break

                linha_atual = tabela_atualizada[i]
                texto_linha = linha_atual.text.upper()

                nome_encontrado = next(
                    (n for n in dicionario_notas.keys() if n in texto_linha), None)

                if nome_encontrado:
                    nota_alvo = dicionario_notas[nome_encontrado]
                    print(f" -> Preenchendo {nome_encontrado}: {nota_alvo}")

                    inputs_texto = linha_atual.find_elements(
                        By.XPATH, ".//input[@type='text']")
                    if inputs_texto:
                        campo_nota = inputs_texto[0]
                        campo_nota.clear()
                        campo_nota.send_keys(nota_alvo)
                        time.sleep(0.2)

                    # Altera o seletor para "Informado"
                    selects = linha_atual.find_elements(By.TAG_NAME, "select")
                    if selects:
                        select_obj = Select(selects[0])
                        if select_obj.first_selected_option.text.strip().lower() == "não informado":
                            select_obj.select_by_visible_text("Informado")

                    alunos_atualizados += 1
                    time.sleep(0.3)
            except:
                continue

        print(
            f"\n*** CONCLUÍDO! {alunos_atualizados} notas de {escolha_nota} lançadas. ***")

    except Exception as e:
        print(f"Erro no portal do Estado: {str(e)}")


if __name__ == "__main__":
    integrar_sistemas()
