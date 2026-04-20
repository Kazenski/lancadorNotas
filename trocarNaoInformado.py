from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import StaleElementReferenceException
import time


def ajustar_apenas_seletores():
    # Configuração para conectar ao Chrome já aberto na porta 9222
    chrome_options = Options()
    chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")

    print("Conectando ao navegador...")
    try:
        driver = webdriver.Chrome(options=chrome_options)
    except Exception:
        print("Erro: O Chrome precisa estar aberto com --remote-debugging-port=9222.")
        return

    # Localiza a aba do portal do Estado
    aba_estado = None
    for handle in driver.window_handles:
        driver.switch_to.window(handle)
        if "professoronline" in driver.current_url.lower() or "sed.sc.gov.br" in driver.current_url.lower():
            aba_estado = handle
            break

    if not aba_estado:
        print("ERRO: Aba do Professor Online não encontrada!")
        return

    driver.switch_to.window(aba_estado)
    print("\n--- INICIANDO ALTERAÇÃO DE STATUS ---")

    try:
        # Localiza todas as linhas de alunos na tabela do estado
        linhas = driver.find_elements(
            By.XPATH, "//tr[contains(@id, 'Grid1ContainerRow')]")
        total = len(linhas)
        print(f"Encontrados {total} alunos na lista.")

        alterados = 0

        for i in range(total):
            try:
                # Recarrega a lista para evitar erro de elemento antigo (Stale)
                tabela = driver.find_elements(
                    By.XPATH, "//tr[contains(@id, 'Grid1ContainerRow')]")
                if i >= len(tabela):
                    break

                linha_atual = tabela[i]
                selects = linha_atual.find_elements(By.TAG_NAME, "select")

                if selects:
                    dropdown = selects[0]
                    select_obj = Select(dropdown)

                    # Verifica se o status atual é "Não Informado" para trocar
                    texto_atual = select_obj.first_selected_option.text.strip().lower()

                    if texto_atual == "não informado":
                        select_obj.select_by_visible_text("Informado")
                        alterados += 1
                        print(
                            f"[{i+1}/{total}] Status atualizado para Informado.")
                        # Pausa curta para processamento da página
                        time.sleep(0.1)
                    else:
                        print(
                            f"[{i+1}/{total}] Já estava preenchido. Pulando...")

            except StaleElementReferenceException:
                time.sleep(1)
                continue
            except Exception:
                continue

        print(
            f"\n*** SUCESSO! {alterados} seletores foram atualizados para 'Informado'. ***")

    except Exception as e:
        print(f"Ocorreu um erro: {str(e)}")


if __name__ == "__main__":
    ajustar_apenas_seletores()
