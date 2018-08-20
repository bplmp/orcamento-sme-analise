import pandas as pd
import json
import glob

json_files = glob.glob("dados/empenhos-contratos/*.json")

frames = []

for f in json_files:
    e = json.load(open(f))
    e_df = pd.DataFrame(e)
    frames.append(e_df)

empenhos_contratos_df = pd.concat(frames)
del frames

empenhos_contratos_df.to_json('dados/empenhos-contratos-2017.json', orient='records')
