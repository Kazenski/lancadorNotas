from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import StaleElementReferenceException
import time

def alterar_seletores():
    # Conecta ao mesmo Chrome que já está aberto na porta 9222
    chrome_options = Options()
    chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    
    print("Conectando ao navegador aberto...")
    try:
        driver = webdriver.Chrome(options=chrome_options)
    except Exception as e:
        print("Erro ao conectar no Chrome. Ele está aberto com --remote-debugging-port=9222?")
        return

    print("\n--- INICIANDO TROCA DE SELETORES ---")
    
    try:
        # Pega a quantidade inicial de seletores para o loop
        total_seletores = len(driver.find_elements(By.TAG_NAME, "select"))
        print(f"Encontrados {total_seletores} seletores (dropdowns) na página.")
        
        alterados = 0
        
        for i in range(total_seletores):
            try:
                # Recarrega a lista a cada iteração para evitar que o HTML "suma" (Stale Element)
                lista_atualizada = driver.find_elements(By.TAG_NAME, "select")
                
                if i >= len(lista_atualizada):
                    break
                    
                seletor = lista_atualizada[i]
                
                # O Selenium tem uma classe especial 'Select' perfeita para lidar com tags <select>
                select_obj = Select(seletor)
                opcao_atual = select_obj.first_selected_option.text.strip()
                
                # Verifica se está como "Não Informado" (ignorando maiúsculas/minúsculas por segurança)
                if opcao_atual.lower() == "não informado":
                    print(f"[{i+1}/{total_seletores}] Alterando de '{opcao_atual}' para 'Informado'...")
                    select_obj.select_by_visible_text("Informado")
                    alterados += 1
                    
                    # Pausa rápida para dar tempo da página processar (ajuste se for muito rápido)
                    time.sleep(0.3) 
                else:
                    print(f"[{i+1}/{total_seletores}] Já preenchido ou diferente: '{opcao_atual}'. Pulando.")
                    
            except StaleElementReferenceException:
                print(f"[{i+1}/{total_seletores}] A página recarregou durante a troca. Recuperando o fôlego...")
                time.sleep(1)
                # O loop vai continuar e na próxima iteração pega o HTML novo
            except Exception as e:
                # Se o seletor estiver bloqueado ou não tiver a opção, ignora e segue
                print(f"[{i+1}/{total_seletores}] Aviso: Não foi possível alterar este seletor.")

        print(f"\n*** PROCESSO FINALIZADO! {alterados} seletores foram atualizados. ***")

    except Exception as e:
        print(f"Ocorreu um erro inesperado: {str(e)}")

if __name__ == "__main__":
    alterar_seletores()
