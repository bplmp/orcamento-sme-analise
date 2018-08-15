import pandas as pd
import requests
import json
import glob
import datetime
import os
from multiprocessing import Process
from termcolor import colored

TOKEN = '198f959a5f39a1c441c7c863423264'
base_url = "https://gatewayapi.prodam.sp.gov.br:443/financas/orcamento/sof/v2.1.0"
headers = {'Authorization' : str('Bearer ' + TOKEN)}

json_files = glob.glob("wget-contratos/2017/*")
frames = []
for f in json_files:
    e = json.load(open(f))
    e_df = pd.DataFrame(e['lstContratos'])
    frames.append(e_df)

contratos_df = pd.concat(frames)

print(f"total contratos length {len(list(contratos_df['codContrato']))}")

url_empenho = '{base_url}/consultaEmpenhos?anoEmpenho=2017&mesEmpenho=12&codOrgao=16'.format(base_url=base_url)
num_contrato = '&codContrato={CONTRATO}'
empenhos_join_contratos = []

downloaded_files = [f.replace('.json', '') for f in os.listdir('dados/empenhos-contratos/')]
contratos_to_download = contratos_df[~contratos_df['codContrato'].isin(downloaded_files)]
codigos_list = list(contratos_to_download['codContrato'])
remaining_contratos_len = len(codigos_list)
print(f"remaining contratos {remaining_contratos_len}")

def scrape(codContratoList, color):
    for codContrato in codContratoList:
        req_url = url_empenho + num_contrato.format(CONTRATO=codContrato)
        start_time = datetime.datetime.now()
        print(colored(f"requesting contrato {codContrato} at {start_time}", color))
        r = requests.get(req_url, headers=headers, verify=True)
        elapsed_time = datetime.datetime.now() - start_time
        print(colored(f"got response for {codContrato} at {elapsed_time} later", color))
        if r.status_code == 200:
            try:
                data = r.json()
                empenhos = data['lstEmpenhos']
                if len(empenhos) == 0:
                    with open(f"dados/empenhos-contratos/{codContrato}.json", "w") as file:
                        print(json.dumps([]), file=file)
                else:
                    for empenho in empenhos:
                        empenho.update({'codContrato': codContrato})
                        empenhos_join_contratos.append(empenho)
                        empenhos_json = json.dumps(empenhos)
                        with open(f"dados/empenhos-contratos/{codContrato}.json", "w") as file:
                            print(empenhos_json, file=file)
            except Exception as e:
                print(f"ERROR: while handling contrato {codContrato}:")
                print(e)
        else:
            print(f"ERROR: for contrato {codContrato} status code was {r.status_code}")

def chunkify(lst,n):
    return [lst[i::n] for i in range(n)]

num_workers = 6
parts = list(chunkify(codigos_list, num_workers))

def func1():
  scrape(parts[0], 'red')
def func2():
  scrape(parts[1], 'green')
def func3():
  scrape(parts[2], 'blue')
def func4():
  scrape(parts[3], 'yellow')
def func5():
  scrape(parts[4], 'magenta')
def func6():
  scrape(parts[5], 'cyan')

if __name__ == '__main__':
  p1 = Process(target=func1)
  p2 = Process(target=func2)
  p3 = Process(target=func3)
  p4 = Process(target=func4)
  p5 = Process(target=func5)
  p6 = Process(target=func6)
  p1.start()
  p2.start()
  p3.start()
  p4.start()
  p5.start()
  p6.start()
  p1.join()
  p2.join()
  p3.join()
  p4.join()
  p5.join()
  p6.join()
