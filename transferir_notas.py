from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
import time


def integrar_sistemas():
    # --- CONFIGURAÇÃO INICIAL ---
    chrome_options = Options()
    chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")

    print("Conectando ao navegador aberto...")
    try:
        driver = webdriver.Chrome(options=chrome_options)
        wait = WebDriverWait(driver, 10)
    except Exception:
        print("Erro: Não foi possível conectar ao Chrome na porta 9222.")
        return

    # --- ESCOLHA DA NOTA (N1 a N4) ---
    print("\n--- CONFIGURAÇÃO DE TRANSCRIÇÃO ---")
    nota_alvo = input(
        "Qual nota deseja transcrever (n1, n2, n3 ou n4)? ").strip().lower()

    if nota_alvo not in ['n1', 'n2', 'n3', 'n4']:
        print("ERRO: Opção inválida! Escolha entre n1, n2, n3 ou n4.")
        return

    print(f"\n--- INICIANDO INTEGRAÇÃO PARA {nota_alvo.upper()} ---")

    # --- IDENTIFICAÇÃO DAS ABAS ---
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

    # ==========================================
    # 1. LER NOTAS DO SEU SITE (profkazenski.com)
    # ==========================================
    driver.switch_to.window(aba_meu_site)
    print(
        f"\n[1/2] Lendo notas da coluna {nota_alvo.upper()} em profkazenski.com...")
    time.sleep(2)

    dicionario_notas = {}

    try:
        # Busca todas as linhas que possuem o atributo data-uid (padrão do seu site)
        wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, "tr[data-uid]")))
        linhas_meu_site = driver.find_elements(By.CSS_SELECTOR, "tr[data-uid]")

        for linha in linhas_meu_site:
            try:
                # O nome do aluno está na célula com a classe correspondente
                nome_aluno = linha.find_element(
                    By.CSS_SELECTOR, "td.font-bold").text.strip().upper()

                if not nome_aluno:
                    continue

                # CORREÇÃO CRÍTICA: Busca o input em qualquer lugar da linha que tenha o data-field correto
                seletor_nota = f"input[data-field='{nota_alvo}']"
                input_especifico = linha.find_element(
                    By.CSS_SELECTOR, seletor_nota)
                valor_nota = input_especifico.get_attribute("value")

                if valor_nota and valor_nota.strip() != "":
                    print(f"    [+] Lido: {nome_aluno} | Nota: {valor_nota}")
                    nota_formatada = str(valor_nota).replace(".", ",")
                    dicionario_notas[nome_aluno] = nota_formatada
                else:
                    print(
                        f"    [-] Ignorado: {nome_aluno} (Campo {nota_alvo.upper()} vazio)")
            except:
                continue

        print(
            f"\n-> Sucesso! {len(dicionario_notas)} notas de {nota_alvo.upper()} guardadas.")

    except Exception as e:
        print(f"Erro ao ler as notas: {str(e)}")
        return

    if len(dicionario_notas) == 0:
        print(
            "Nenhuma nota encontrada. Verifique se a página Professor Tech está carregada.")
        return

    # ==========================================
    # 2. PREENCHER O PORTAL DO ESTADO
    # ==========================================
    driver.switch_to.window(aba_estado)
    print("\n[2/2] Injetando notas no portal do Estado...")
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

                nome_encontrado = None
                for nome_dict in dicionario_notas.keys():
                    if nome_dict in texto_linha:
                        nome_encontrado = nome_dict
                        break

                if nome_encontrado:
                    nota_alvo_valor = dicionario_notas[nome_encontrado]
                    print(
                        f" -> {nome_encontrado}: Inserindo {nota_alvo_valor}...")

                    inputs_texto = linha_atual.find_elements(
                        By.XPATH, ".//input[@type='text']")
                    if inputs_texto:
                        campo_nota = inputs_texto[0]
                        campo_nota.clear()
                        campo_nota.send_keys(nota_alvo_valor)
                        time.sleep(0.1)

                    selects = linha_atual.find_elements(By.TAG_NAME, "select")
                    if selects:
                        select_obj = Select(selects[0])
                        if select_obj.first_selected_option.text.strip().lower() == "não informado":
                            select_obj.select_by_visible_text("Informado")

                    alunos_atualizados += 1

            except:
                continue

        print(
            f"\n*** CONCLUÍDO! {alunos_atualizados} notas ({nota_alvo.upper()}) integradas. ***")

    except Exception as e:
        print(f"Erro no portal do Estado: {str(e)}")


if __name__ == "__main__":
    integrar_sistemas()
