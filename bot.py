"""
WARNING:

Please make sure you install the bot with `pip install -e .` in order to get all the dependencies
on your Python environment.

Also, if you are using PyCharm or another IDE, make sure that you use the SAME Python interpreter
as your IDE.

If you get an error like:
```
ModuleNotFoundError: No module named 'botcity'
```

This means that you are likely using a different Python interpreter than the one used to install the bot.
To fix this, you can either:
- Use the same interpreter as your IDE and install your bot with `pip install --upgrade -r requirements.txt`
- Use the same interpreter as the one used to install the bot (`pip install --upgrade -r requirements.txt`)

Please refer to the documentation for more information at https://documentation.botcity.dev/
"""


# Import for the Web Bot
from botcity.web import WebBot, Browser, By

# Import for integration with BotCity Maestro SDK
from botcity.web.util import element_as_select
from botcity.web.parsers import table_to_dict
from botcity.maestro import *
from botcity.plugins.excel import BotExcelPlugin

# Disable errors if we are not connected to Maestro
BotMaestroSDK.RAISE_NOT_CONNECTED = False

excel = BotExcelPlugin()
excel.add_row(["CIDADE","POPULACAO"])

def main():
    # Runner passes the server url, the id of the task being executed,
    # the access token and the parameters that this task receives (when applicable).
    maestro = BotMaestroSDK.from_sys_args()
    ## Fetch the BotExecution with details from the task, including parameters
    execution = maestro.get_execution()

    #maestro.login(server="https://developers.botcity.dev/",login="d5107e28-7d3d-431a-9c29-fd69a8b58c13", key="D51_IAH2WF7VEGFD71SXH3RY")

    print(f"Task ID is: {execution.task_id}")
    print(f"Task Parameters are: {execution.parameters}")

    bot = WebBot()

    # Configure whether or not to run on headless mode
    bot.headless = False

    # Uncomment to change the default Browser to Firefox
    bot.browser = Browser.CHROME

    # Uncomment to set the WebDriver path
    #bot.driver_path = r"C:\Users\shica\Documents\Robos\chromedriver-win64\chromedriver-win64\chromedriver.exe"
    bot.driver_path = r"C:\Users\JoaoRosa\Documents\Robos\chromedriver-win64\chromedriver.exe"
    # Opens the BotCity website.
    bot.browse("https://buscacepinter.correios.com.br/app/faixa_cep_uf_localidade/index.php")

    # Implement here your logic...
    drop_uf = element_as_select(bot.find_element("//select[@id='uf']", By.XPATH))
    drop_uf.select_by_value("SP")

    btn_pesquisar = bot.find_element("//button[@id='btn_pesquisar']", By.XPATH)
    btn_pesquisar.click()

    bot.wait(3000)

    table_dados = bot.find_element("//table[@id='resultado-DNEC']", By.XPATH)
    table_dados = table_to_dict(table=table_dados)

    bot.navigate_to("https://cidades.ibge.gov.br/brasil/sp/panorama")

    int_contador = 1
    str_CidadeAnterior =""

    for cidade in table_dados:
        str_cidade = cidade["localidade"]
        if str_CidadeAnterior == str_cidade:
            continue
        if int_contador<=5:        
            campo_pesquisa = bot.find_element("//input[@placeholder='O que você procura?']", By.XPATH)
            campo_pesquisa.send_keys(str_cidade)
            bot.wait(2000)
            opcao_cidade = bot.find_element(f"//a[span[contains(text(),'{str_cidade}')] and span[contains(text(),'SP')]]", By.XPATH)
            opcao_cidade.click()
            bot.wait(2000)
            populacao = bot.find_element("//div[@class='indicador__valor']", By.XPATH)
            str_populacao = populacao.text
            excel.add_row([str_cidade,str_populacao])
            maestro.new_log_entry(activity_label="CIDADES",values={"CIDADE":f"{str_cidade}","POPULACAO":f"{str_populacao}"})
            int_contador = int_contador +1
            str_CidadeAnterior = str_cidade
        else:
            print("Numero maximo de cidades atingido")
            break
    excel.write(r"C:\Users\JoaoRosa\Documents\Robos\Projetos\IntensivoRPABotCityT2C\Infos_Cidades.xlsx")
    # Wait 3 seconds before closing
    bot.wait(5000)

    # Finish and clean up the Web Browser
    # You MUST invoke the stop_browser to avoid
    # leaving instances of the webdriver open
    bot.stop_browser()

    # Uncomment to mark this task as finished on BotMaestro
    maestro.finish_task(
        task_id=execution.task_id,
        status=AutomationTaskFinishStatus.SUCCESS,
        message="Task Finished OK."
    )


def not_found(label):
    print(f"Element not found: {label}")


if __name__ == '__main__':
    main()
