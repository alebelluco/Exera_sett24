# Versione 23-04-2024

# esportare in pickle l'agenda dal sw programmazione


import streamlit as st
from streamlit_folium import folium_static
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from datetime import time, timedelta, datetime, date
import math
import xlrd
import folium
import openrouteservice
import pickle
from utils import persistence_ab as pe
from io import BytesIO
import xlsxwriter
import random

st.set_page_config(page_title="Planner interventi", layout='wide')

client = openrouteservice.Client(key='5b3ce3597851110001cf6248d1d5a3c164ef475d8ae776eeb594fda6')
coordinate_exera = (11.594276, 44.817830)

operatori = [
 'JOLLY',
 'SQUADRA1',
 'SQUADRA2',
 'SQUADRA3',
 'FURLATTI STEFANO',
 'SACCENTI FABRIZIO',
 'ALTIERI NICO',
 'FARINA MIRKO',
 'BERTAZZINI ALBIERI NICHOLAS',
 'BERGOSSI MATTIA',
 'BINELLI RICCARDO',
 'GOVONI ENRICO',
 'FABBRI MATTEO',
 'CESARI UMBERTO',
 'PASQUALI NICOLA',
 'OMEROVIC ESAD',
 'FRANCESCHINI ANDREA',
 'AGUIARI STEFANO',
 'MALAGUTTI FILIPPO',
 'BARALDI CLAUDIO'
 ]


headsx, headcx, headdx, headlogo = st.columns([1,1,1,6])
with headsx:
    placeholder = st.empty()
with headcx:
    placeholder2 = st.empty()
with headdx:
    placeholder3 =  st.empty()


col1, col2 = st.columns([4,1])
with col1:
    #st.title('Visualizzazione programma di lavoro')
    pass

with col2:
    #st.image('https://github.com/alebelluco/Test_EX/blob/main/exera_logo.png?raw=True')
    pass

layout  = {'Layout_select':['Check','Cliente','Sito','N_op','Op_vincolo','Indirizzo Sito','IstruzioniOperative','orari','Servizio','Periodicita','SitoTerritoriale','Citta',
                            'Durata_stimata','ID','lat','lng','date_range','Mensile'],

        'Layout_no_dup':['Cliente','Sito','N_op','Op_vincolo','Indirizzo Sito','IstruzioniOperative','orari','Servizio','Periodicita','SitoTerritoriale','Citta',
                            'Durata_stimata','ID','lat','lng','Target_range','Mensile'],


           'Layout_agenda':['Check','Cliente','Sito','N_op','Op_vincolo','Indirizzo Sito','IstruzioniOperative','orari','Servizio','Periodicita','SitoTerritoriale','Citta',
                            'Durata_stimata','ID','lat','lng','Operatore','date_range','Mensile'],

            'Layout_agenda_work':['Durata_stimata','Cliente','Sito','Servizio','Periodicita','Operatore','lat','lng','Data','Mensile'],

            'Agenda_edit' : ['IstruzioniOperative','Ordine_intervento','Durata_viaggio','Arrivo_da_precedente','Inizio','Durata_stimata','Fine','Cliente','Sito','Servizio','Periodicita','Operatore','lat','lng','Data','ID'],
                            
            'Agenda_esporta' : ['Data','Inizio','Fine','Durata_stimata','IstruzioniOperative','Cliente','Sito','Indirizzo Sito', 'Servizio','Operatore'] ,

            'Agenda_completa' : ['Operatore','Inizio','Fine','Durata_stimata','IstruzioniOperative','Cliente','Sito','Indirizzo Sito', 'Servizio'],

            'Scacchiera' : ['Durata_viaggio','Inizio','Fine','Durata_stimata','Cliente' ,'Indirizzo Sito' ,'IstruzioniOperative', 'Servizio'],

            'Refresh' : ['ID', 'Confronto','key']  ,   

            'Mappa'  : ['Check','Cliente','Durata_stimata', 'Servizio','Sito','N_op','Op_vincolo','Indirizzo Sito','orari','IstruzioniOperative','Periodicita','SitoTerritoriale','Citta',
                            'ID','lat','lng','Operatore','date_range','Mensile']  ,

            'Mappa2'  : ['S','PrezzoEUR','Check','Cliente','Durata_stimata','Servizio','Sito','N_op','Op_vincolo','Indirizzo Sito',
                         'IstruzioniOperative','Periodicita','SitoTerritoriale','ID','lat','lng','Operatore','date_range',
                         'Mensile','ultimo_intervento','Ritardo']               
                                                        
                            }

percorso_altri = st.sidebar.file_uploader("Caricare altri siti")
if not percorso_altri:
    st.stop()

st.sidebar.subheader('Coordinate mancanti:')

altri_siti=pd.read_csv(percorso_altri)
altri_siti = altri_siti.drop_duplicates()

altri_siti['SitoTerritoriale']=np.where(altri_siti['SitoTerritoriale'].astype(str)=='nan','ND',altri_siti['SitoTerritoriale'])

siti_unici = altri_siti['SitoTerritoriale'].unique()

if 'altri_siti' not in st.session_state: 
    st.session_state.altri_siti = altri_siti.copy()
    st.session_state.altri_siti['Durata_stimata'] = st.session_state.altri_siti['Durata_stimata'].str.replace(',','.')
    st.session_state.altri_siti['lat'] = st.session_state.altri_siti['lat'].str.replace(',','.')
    st.session_state.altri_siti['lng'] = st.session_state.altri_siti['lng'].str.replace(',','.')
    st.session_state.altri_siti['Durata_stimata'] = st.session_state.altri_siti['Durata_stimata'].str.replace(',','.')
    st.session_state.altri_siti['Durata_stimata'] = st.session_state.altri_siti['Durata_stimata'].astype(float)
    st.session_state.altri_siti['key_distanze'] = st.session_state.altri_siti['Cliente']+" | "+st.session_state.altri_siti['Indirizzo Sito']
    #st.session_state.siti_unici = st.session_state.altri_siti['SitoTerritoriale'].unique()
    st.session_state.altri_siti['no_spazi'] = [stringa.replace(' ','') for stringa in st.session_state.altri_siti['Target_range']]
    st.session_state.altri_siti['appoggio'] = [stringa.replace('[','') for stringa in st.session_state.altri_siti['no_spazi']]
    st.session_state.altri_siti['appoggio2'] = [stringa.replace(']','') for stringa in st.session_state.altri_siti['appoggio']]
    st.session_state.altri_siti['date_range'] = [str.split(stringa, ',') for stringa in st.session_state.altri_siti['appoggio2']]
    st.session_state.altri_siti['Check'] = False
    #st.session_state.altri_siti = st.session_state.altri_siti.rename(columns={'N_op_x':'N_op','Op_vincolo_x':'Op_vincolo'})
    #st.session_state.altri_siti = st.session_state.altri_siti.merge(vincolo_nop, how='left',left_on='ID',right_on='ID')   
    #st.session_state.altri_siti = st.session_state.altri_siti.rename(columns={'N_op_x':'N_op','Op_vincolo_x':'Op_vincolo'})
    #st.session_state.altri_siti = st.session_state.altri_siti.drop(columns=['Note','Target_range','no_spazi','appoggio','appoggio2','N_op_y','Op_vincolo_y'])

if 'agenda' not in st.session_state:
    st.session_state.agenda = st.session_state.altri_siti[st.session_state.altri_siti['Check'] == True]
    st.session_state.agenda['Operatore'] = None
    st.session_state.agenda['Data'] = None
    st.session_state.agenda['Inizio'] = None #np.datetime64('NaT')
    st.session_state.agenda['Fine'] = None #np.datetime64('NaT')
    st.session_state.agenda['Ordine_intervento'] = None
    st.session_state.agenda['Durata_viaggio'] = None
    st.session_state.agenda['Arrivo_da_precedente'] = None


def callback3():    
        #st.session_state.agenda = pd.concat([st.session_state.agenda,st.session_state.altri_siti[st.session_state.altri_siti['Check']==True]])
        st.session_state.agenda = pd.concat([st.session_state.agenda, work[work['Check']==True]])
        for i in range (len(st.session_state.altri_siti)):
                id = st.session_state.altri_siti.ID.iloc[i]
                for k in range(len(work)):
                    id_work = work.ID.iloc[k]
                    if id == id_work:
                        st.session_state.altri_siti.Check.iloc[i] = work.Check.iloc[k]
        st.session_state.altri_siti = st.session_state.altri_siti[st.session_state.altri_siti['Check'] == False]


scelta_giorno = st.date_input('Inserire data da pianificare')
scelta_sito = st.multiselect('Selezionare Sito', siti_unici)
if not scelta_sito:
        #st.stop()
        scelta_sito=siti_unici
work = st.session_state.altri_siti.copy()
work_rit = st.session_state.altri_siti.copy()

work = work[[any(sito in word for sito in scelta_sito) for word in work['SitoTerritoriale'].astype(str)]]

if st.toggle('Mostra tutti gli interventi del mese'):
    work = work
    #improrogabili = list(work.ID[[len(date)==1 for date in work.date_range ]])
    improrogabili = list(work[work.S == 'F*'].ID)
    st.write(f'{len(improrogabili)} interventi improrogabili nel sito nel mese')

else:
    #st.write('work',work)
    work = work[[str(scelta_giorno.day) in tgtrange for tgtrange in work.date_range]]
    improrogabili = list(work[work.S == 'F*'].ID)
    st.write(f'{len(improrogabili)} interventi improrogabili nel sito nella data selezionata')


if st.toggle('Mostra improrogabili'):
    try:            
        work = work[work.S == 'F*']
    except:
        st.write('nessun intervento')
else:       
    work = work


if st.toggle('Mostra interventi in ritardo'):
    work = work_rit
    try:
        work = work[work['Ritardo'] == 'x']
    except:
        st.write('nessun intervento in ritardo sul sito')

else:
    work = work

if st.toggle('Mostra interventi con disponibilità ristretta'):
    try:            
        work = work[[len(date)<=5 for date in work.date_range ]]
    except:
        st.write('nessun intervento')
else:       
    work = work


if st.toggle(('2Operatori')):
    try:
        work = work[work['N_op']==' 2 OPERATORI']
    except:
        st.write('Nessun intervento')
else:
    try:
        work = work[work['N_op']!=' 2 OPERATORI']
    except:
        st.write('Nessun intervento')


work['Operatore'] = None

try:
    coordinate_inizio = work[['Cliente','lat','lng']].copy()
except:
        st.write(':orange[Nessun intervento sul sito disponibile nelle date selezionate]')

coordinate_inizio  = coordinate_inizio[(coordinate_inizio.lat != 0) & (coordinate_inizio.lat.astype(str) != 'nan')]

if len(coordinate_inizio) != 0:
        inizio = (coordinate_inizio.lat.iloc[0],coordinate_inizio.lng.iloc[0])
else:
        st.write(':orange[Nessun intervento nei siti selezionati]')
        inizio = (coordinate_exera[1],coordinate_exera[0])



try:
    mensili = {'si':'red','no':'blue'}
    centro_mappa = st.session_state.agenda.copy()
    #st.write(centro_mappa)
    #st.write(scelta_giorno)
    #st.write(centro_mappa.Data.iloc[-1])
    #st.stop()
    #centro_mappa = centro_mappa[centro_mappa.Operatore == nome_cognome]
    #centro_mappa = centro_mappa[centro_mappa.Data == scelta_giorno]
    #st.write(centro_mappa)
    #st.stop()



    try:
        lat_inizio = centro_mappa.lat.iloc[-1]
        lng_inizio = centro_mappa.lng.iloc[-1]
        if (not lat_inizio) or (str(lat_inizio)=='nan'):
            lat_inizio = coordinate_exera[0]
            lng_inizio = coordinate_exera[0]
            lat_inizio = work.lat.iloc[1]
            lng_inizio = work.lng.iloc[0]
            if (not lat_inizio) or (str(lat_inizio)=='nan'):
                lat_inizio = coordinate_exera[1]
                lng_inizio = coordinate_exera[0]

    
    except:

        lat_inizio = coordinate_exera[1]
        lng_inizio = coordinate_exera[0]
        #lat_inizio = work.lat.iloc[1]
        #lng_inizio = work.lng.iloc[0]


    #st.write(lat_inizio)
    #lat_inizio = coordinate_exera[1]
    #lng_inizio = coordinate_exera[0]

    #mappa=folium.Map(location=inizio,zoom_start=15)
    mappa=folium.Map(location=(lat_inizio,lng_inizio),zoom_start=15)
    
    #stampo il punto dell'ultimo intervento

    folium.CircleMarker(location=(lat_inizio,lng_inizio),
                                radius=30,
                                color='red',
                                stroke=False,
                fill=True,
                fill_opacity=0.8,
                opacity=1,
                ).add_to(mappa)
    
    for i in range(len(work)):

        if work.IstruzioniOperative.astype(str).iloc[i] != 'nan':
            ist = 'Note: ' + work.IstruzioniOperative.astype(str).iloc[i]
        else:
            ist = 'Nessuna nota'


        if work.ultimo_intervento.astype(str).iloc[i] != 'nan':
            ultimo = 'Ultimo intervento: \n ' + work.ultimo_intervento.astype(str).iloc[i][0:10]
        else:
            ultimo= 'Pianificazione libera'



        try:
            folium.CircleMarker(location=[work.lat.iloc[i], work.lng.iloc[i]],
                                radius=7,
                                color=mensili[work.Mensile.iloc[i]],
                                stroke=False,
                fill=True,
                fill_opacity=1,
                opacity=1,
                popup=ultimo +'   \n  '+ ist,
                tooltip=work.Cliente.iloc[i]+' | '+ work.Servizio.iloc[i]+' | '+' Durata: '+
                    str(work['Durata_stimata'].iloc[i]) + '| Valore: '+str(work['PrezzoEUR'].iloc[i])+'€'
                ).add_to(mappa)
        except:
            #st.sidebar.write('Cliente {} non visibile sulla mappa per mancanza di coordinate su Byron'.format(work.Cliente.iloc[i]))
            st.sidebar.write('{}'.format(work.Cliente.iloc[i]))
            pass
    #
    # st.stop() 

    sxmappa, dxmappa = st.columns([2,1])    
    with sxmappa:
        folium_static(mappa,width=1300,height=800)
        #st.write('work',work[layout['Mappa']])

    with dxmappa:
        work = st.data_editor(work[layout['Mappa2']],height=800)
    sx4, spazio1, cx4, dx4 =st.columns([4,1,3,2])

# view agenda    
    with sx4:
        nome_cognome = st.selectbox('Seleziona operatore',operatori)
        data_pianificazione = st.date_input('Seleziona data assegnazione', value=scelta_giorno)
        submit_button = st.button(label='Aggiungi interventi', on_click=callback3)
        work['Operatore'] = nome_cognome
        work['Data'] = data_pianificazione  
        agenda_work = st.session_state.agenda.copy()
        agenda_work = agenda_work[agenda_work.Operatore == nome_cognome]
        agenda_work = agenda_work[agenda_work.Data == data_pianificazione]
        agenda_work[layout['Layout_agenda_work']]
        
# Cruscotto dati giornata
    with cx4:
        distanze = st.toggle('Abilita calcolo distanze')         
        tempo = agenda_work.Durata_stimata.sum()         
        st.subheader('Indicatori giornata', divider='orange')
        st.subheader('Operatore: :orange[{}]'.format(nome_cognome))
        st.subheader('Ore di intervento: :orange[{:0.2f}]'.format(tempo/60))

        viaggio = 0

        if distanze:

            if len(agenda_work)==0:
                st.stop()
            else:
                primo_intervento = (agenda_work.lng.iloc[0],agenda_work.lat.iloc[0])

            try:
                res = client.directions((coordinate_exera, primo_intervento))
                durata = res['routes'][0]['summary']['duration']
                viaggio+=(durata/3600)
            except:
                viaggio += 0.25
                st.write('coordinate non presenti, stimato 15 minuti primo viaggio della giornata')

            for i in range(1,len(agenda_work)):
                part = (agenda_work.lng.iloc[i-1],agenda_work.lat.iloc[i-1])
                arr = (agenda_work.lng.iloc[i],agenda_work.lat.iloc[i])
            
                try:
                    res = client.directions((part , arr))
                    durata = res['routes'][0]['summary']['duration']/3600
                    viaggio+=durata

                except:
                    if part == arr:
                        durata = 0
                    else:
                        durata = 0.25
                        st.write('coordinate non presenti')
                    viaggio+=durata
        
            ultimo_intervento = (agenda_work.lng.iloc[-1],agenda_work.lat.iloc[-1])
            try:
                res = client.directions((ultimo_intervento,coordinate_exera))
                durata = res['routes'][0]['summary']['duration']
                viaggio+=(durata/3600)
            except:
                viaggio += 0.25
                st.write('coordinate non presenti, stimato 15 minuti ultimo viaggio della giornata')        
        else:
            viaggio = 15*len(agenda_work)/60

        st.subheader('Ore di viaggio stimate: :orange[{:0.2f}]'.format(viaggio))
        st.subheader('Ore totali agenda: {:0.2f}'.format(viaggio + tempo/60))
except:
    pass

