from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
import time

def integrar_sistemas():
    chrome_options = Options()
    chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    
    print("Conectando ao navegador aberto...")
    try:
        driver = webdriver.Chrome(options=chrome_options)
        wait = WebDriverWait(driver, 10)
    except Exception:
        print("Erro: Não foi possível conectar ao Chrome na porta 9222.")
        return

    print("\n--- INICIANDO INTEGRAÇÃO DE NOTAS ---")

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
        print("ERRO: Certifique-se de que a aba do seu site e a aba do Estado estão abertas!")
        return

    # ==========================================
    # 1. LER NOTAS DO SEU SITE (profkazenski.com)
    # ==========================================
    driver.switch_to.window(aba_meu_site)
    print("\n[1/2] Focando na aba profkazenski.com...")
    time.sleep(2) 

    dicionario_notas = {}
    
    try:
        print(" -> Procurando as linhas da tabela...")
        wait.until(EC.presence_of_element_located((By.XPATH, "//tbody/tr")))
        
        linhas_meu_site = driver.find_elements(By.XPATH, "//tbody/tr")
        print(f" -> Raio-X: O robô encontrou {len(linhas_meu_site)} linhas no seu site.")
        
        for i, linha in enumerate(linhas_meu_site):
            tds = linha.find_elements(By.TAG_NAME, "td")
            
            if len(tds) < 4:
                continue
                
            nome_aluno = tds[1].text.strip().upper()
            
            # NOVIDADE: Se não tiver nome de aluno (como os checkboxes "on"), pula direto
            if nome_aluno == "":
                continue
            
            inputs_nota = tds[3].find_elements(By.TAG_NAME, "input")
            
            if inputs_nota:
                valor_nota = inputs_nota[0].get_attribute("value")
                
                if valor_nota and valor_nota.strip() != "":
                    print(f"    [+] Lido: {nome_aluno} | Nota: {valor_nota}")
                    nota_formatada = str(valor_nota).replace(".", ",")
                    dicionario_notas[nome_aluno] = nota_formatada
                else:
                    print(f"    [-] Ignorado: {nome_aluno} (Sem nota)")
                    
        print(f"\n -> Sucesso! {len(dicionario_notas)} notas válidas guardadas na memória do robô.")
        
    except Exception as e:
        print(f"Erro ao ler as notas do seu site: {str(e)}")
        return

    if len(dicionario_notas) == 0:
        print("Nenhuma nota encontrada. Cancelando ida para o portal do Estado.")
        return

    # ==========================================
    # 2. PREENCHER O PORTAL DO ESTADO
    # ==========================================
    driver.switch_to.window(aba_estado)
    print("\n[2/2] Injetando notas no portal do Estado...")
    time.sleep(1.5)

    try:
        # NOVIDADE: Agora ele procura as tags <tr> (linhas) que tenham o ID do estado
        linhas_estado = driver.find_elements(By.XPATH, "//tr[contains(@id, 'Grid1ContainerRow')]")
        alunos_atualizados = 0

        for i in range(len(linhas_estado)):
            try:
                # Recarrega a tabela a cada loop para evitar StaleElementReferenceException
                tabela_atualizada = driver.find_elements(By.XPATH, "//tr[contains(@id, 'Grid1ContainerRow')]")
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
                    nota_alvo = dicionario_notas[nome_encontrado]
                    print(f" -> Preenchendo {nome_encontrado} com a nota {nota_alvo}...")
                    
                    # Preenche a nota
                    inputs_texto = linha_atual.find_elements(By.XPATH, ".//input[@type='text']")
                    if inputs_texto:
                        campo_nota = inputs_texto[0]
                        campo_nota.clear()
                        campo_nota.send_keys(nota_alvo)
                        time.sleep(0.2)
                    
                    # Altera o seletor para "Informado"
                    selects = linha_atual.find_elements(By.TAG_NAME, "select")
                    if selects:
                        dropdown = selects[0]
                        select_obj = Select(dropdown)
                        if select_obj.first_selected_option.text.strip().lower() == "não informado":
                            select_obj.select_by_visible_text("Informado")
                            
                    alunos_atualizados += 1
                    time.sleep(0.3)
                    
            except Exception as e:
                # Se der algum erro bobo na linha, ele engole e vai para o próximo aluno
                continue
                
        print(f"\n*** MAGNÍFICO! Integração concluída. {alunos_atualizados} alunos atualizados. ***")

    except Exception as e:
        print(f"Erro ao preencher o portal do Estado: {str(e)}")

if __name__ == "__main__":
    integrar_sistemas()