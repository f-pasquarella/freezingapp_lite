import streamlit as st
from scipy.interpolate import interp1d
import pandas as pd
import numpy as np
import time


st.set_page_config(page_title="Freya", page_icon="🧊",
                   layout="centered", initial_sidebar_state="collapsed")

st.image('logo.png', width=600)
st.markdown('Free-zing APP Lite - Software Open Source per il calcolo del ghiaccio e della dolcezza di un gelato - 2022 Fabio & Aldo Pasquarella')

url1 = "https://didatticagelato.it/"
st.markdown("[www.didatticagelato.it](%s)" % url1)

st.write(" ")

with st.expander("Espandimi per le istruzioni"):
    st.write("""

    Free-zing APP Lite ti fornisce la possibilità di calcolare due parametri importanti per la previsione della qualità del gelato: POD e quantità di ghiaccio in % sul peso complessivo. 
    La curva di congelamento si basa sul lavoro presente in "Ice Cream" di Goff. Se sei un professionista, puoi avere una versione più accurata della curva, 
    con molte funzionalità, parametri e ingredienti in più: collegati qui sotto per maggiori info:
     """)

    url2 = "https://didatticagelato.it/free-zing-app/"
    st.markdown(
        "Scopri la Web-App più avanzata sul mercato di analisi di una ricetta: [Free-zing APP!](%s)" % url2)


st.write(" ")


FPD = [0, 0.18, 0.35, 0.53, 0.72, 0.90, 1.10, 1.29, 1.47, 1.67, 1.86, 2.03, 2.21, 2.40, 2.60, 2.78, 2.99, 3.20, 3.42, 3.63, 3.85,
       4.10, 4.33, 4.54, 4.77, 5.00, 5.26, 5.53, 5.77, 5.99, 6.23, 6.50, 6.80, 7.04, 7.32, 7.56, 7.80, 8.04, 8.33, 8.62, 8.92, 9.19, 9.45,
       9.71, 9.96, 10.22, 10.47, 10.72, 10.97, 11.19, 11.41, 11.63, 11.88, 12.14, 12.40, 12.67, 12.88, 13.08, 13.28, 13.48, 13.68]

SE = [0., 2.91262136,  5.66037736,  8.25688073, 10.71428571,
      13.04347826, 15.25423729, 17.3553719, 19.35483871, 21.25984252,
      23.07692308, 24.81203008, 26.47058824, 28.05755396, 29.57746479,
      31.03448276, 32.43243243, 33.77483444, 35.06493506, 36.30573248,
      37.5, 38.65030675, 39.75903614, 40.82840237, 41.86046512,
      42.85714286, 43.82022472, 44.75138122, 45.65217391, 46.52406417,
      47.36842105, 48.1865285, 48.97959184, 49.74874372, 50.4950495,
      51.2195122, 51.92307692, 52.60663507, 53.27102804, 53.91705069,
      54.54545455, 55.15695067, 55.75221239, 56.33187773, 56.89655172,
      57.44680851, 57.98319328, 58.50622407, 59.01639344, 59.51417004,
      60., 60.4743083, 60.9375, 61.38996139, 61.83206107,
      62.26415094, 62.68656716, 63.099631, 63.50364964, 63.89891697,
      64.28571429]

f_interp2 = interp1d(FPD, SE, kind='quadratic')

df = pd.read_excel('x_lite.xlsx',engine='openpyxl')
df.dropna(inplace=True, axis=1, how='all')
df.reset_index(drop=True, inplace=True)
df = df.sort_values('INGREDIENTE')
df = df.set_index(df.INGREDIENTE)
df = df.drop('INGREDIENTE', axis=1)

values = []
t = st.slider("Imposta la temperatura di servizio in °C", -
              18.0, -8.0, -12.0, 0.5)

ingredienti = st.multiselect(
    'Scegli gli ingredienti della tua ricetta', df.index.tolist(),
    help="Uno degli errori più frequenti è l'uso di molti ingredienti, scelta che spesso si rivela controproducente.Ti consiglio di partire con l'ingrediente caratterizzante la ricetta (cioccolato, nocciola, etc.), almeno un paio di zuccheri come saccarosio e destrosio in piccole quantità, un paio di addensanti come carruba e guar, magari una fibra e un ingrediente liquido come latte o acqua.")

nr_ing = len(ingredienti)

for i in range(nr_ing):
    values.append(st.number_input(
        ingredienti[i], min_value=0.0, key=str(i % 4)))

ricetta = dict(zip(ingredienti, values))


if len(ingredienti) > 0:

    try:

        totale = sum(ricetta.values())
        st.write('Somma Totale: ', np.round(totale, 4))

    except:
        pass

    st.write('___')

    if st.button('Calcola Ghiaccio e POD'):

        try:

            ricetta = {key: np.round((value/totale)*100, 4)
                       for key, value in ricetta.items()}

            percentuali = np.array(list(ricetta.values()))/100
            ingredienti = df.loc[list(ricetta.keys())]

            ingr_ricetta = (df.loc[list(ricetta.keys())]).apply(
                lambda x: x * percentuali)
            acqua = (ingr_ricetta['acqua']).sum()
            lattosio = (ingr_ricetta['lattosio']).sum()
            latt_max = np.exp(2.389+0.028*-12)*acqua*0.6/100
            SE_zuc = (ingr_ricetta['PAC']).sum()
            SDL = ingr_ricetta['SDL'].sum()
            sale_SE = (ingr_ricetta['sale_pac']).sum()
            SE_sali_latte = SDL*5
            SE_sale_SE = 11.722*sale_SE
            latt = min([lattosio, latt_max])
            se = SE_zuc + latt+SE_sali_latte+SE_sale_SE
            se_rel = se*(100-se)/acqua
            POD = (ingr_ricetta['POD']).sum()
            ghiaccio = 100-se_rel/(f_interp2(-t)/100)
            st.write("______")
            st.write("Ghiaccio, % in peso =", np.round(ghiaccio, 1))
            st.write("POD =", np.round(POD, 2))

        except:
            with st.spinner("Ingredienti non validi"):
                time.sleep(2)

        st.write('____')

    url2 = "https://didatticagelato.it/free-zing-app/"
    st.markdown(
        "Scopri la Web-App più avanzata di analisi di una ricetta: [Free-zing APP!](%s)" % url2)
    st.write('____')
    st.markdown(
        "![Alt Text](https://www.paypalobjects.com/it_IT/IT/i/btn/btn_donateCC_LG.gif)")
    url3 = "https://www.paypal.com/donate/?cHJwPXJwdA="
    st.markdown(
        "Aiuta questo progetto libero, anche con una piccola [donazione qui!](%s)" % url3)
