#!/usr/bin/env python
# coding: utf-8

# # COVID-19 em Goiás

# Vamos analisar a questao do COVID-19 no estado de Goiás no Brasil, analisando o numero de casos, numero de mortes, as tendencias de casos e mortes e media movel os ultimos 7 dias em  2021, e a partir dessas análises chegar a conclusão se os numeros cresceram ou declinaram com o passar dos meses.

# # Pacotes e Bibliotecas

# Primeiro importamos os pacotes e bibliotecas necessários para a elaboração da análise do arquivo.

# In[1]:


import math
from typing import Iterator
from datetime import datetime, timedelta

import numpy as np
import pandas as pd


# # Extração

# Importamos os dados diários da COVID-19 da base de dados da **CSSEGISandData** estacionado no GitHub.

# In[2]:


cases = pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports/01-12-2021.csv', sep=',')


# Foi definido uma função **date_range** para gerar um intervalo das datas que queremos trabalhar usando o **start_date** e **end_date**.
# 
# Em seguida, foi criado um loop para iterar sobre essas datas, formatando-as para obter o nome do arquivo correspondente de cada dia.

# In[3]:


def date_range(start_date: datetime, end_date: datetime) -> Iterator[datetime]:
  date_range_days: int = (end_date - start_date).days
  for lag in range(date_range_days):
    yield start_date + timedelta(lag)

start_date = datetime(2021,  1,  1)
end_date   = datetime(2021, 12, 31)


# Depois, um arquivo CSV correspondente foi lido a cada data e filtrando os dados para obter apenas as informações do Brasil e especificamente do estado de Goiás.

# In[4]:


cases = None
cases_is_empty = True

for date in date_range(start_date=start_date, end_date=end_date):

  date_str = date.strftime('%m-%d-%Y')
  data_source_url = f'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports/{date_str}.csv'

  case = pd.read_csv(data_source_url, sep=',')

  case = case.drop(['FIPS', 'Admin2', 'Last_Update', 'Lat', 'Long_', 'Recovered', 'Active', 'Combined_Key', 'Case_Fatality_Ratio'], axis=1)
  case = case.query('Country_Region == "Brazil" and Province_State == "Goias"').reset_index(drop=True)
  case['Date'] = pd.to_datetime(date.strftime('%Y-%m-%d'))
  if cases_is_empty:
    cases = case
    cases_is_empty = False
  else:
    cases = pd.concat([cases, case], axis= 0, ignore_index=True)


# Por fim, você concatena esses dados em um único **DataFrame** chamado *cases*.
# 
# O resultado é um DataFrame que contém os dados diários de COVID-19 para Goiás durante o ano de 2021

# In[5]:


cases.head()


# Verifica-se a quantidade e linhas e colunas

# In[6]:


cases.shape


# Verifica-se o tipo de cada coluna

# In[7]:


cases.info()


# Renomeia as colunas selecionadas e troca o nome de Goias para Goiás.

# In[8]:


cases = cases.rename(
  columns={
    'Province_State': 'State',
    'Country_Region': 'Country'
  }
)

for col in cases.columns:
  cases = cases.rename(columns={col: col.lower()})


# In[9]:


states_map = {
    'Goias': 'Goiás',
}

cases['state'] = cases['state'].apply(lambda state: states_map.get(state) if state in states_map.keys() else state)


# Inicia-se a análise para visualizar a evolução diária dos casos confirmados e das mortes ao longo do tempo. Isso ajudará a identificar picos e quedas no número de casos, foi criado gráficos de linha para o número de casos confirmados e mortes por dia.

# In[10]:


import matplotlib.pyplot as plt

# Agrupando por data
grouped = cases.groupby('date').sum()

# Gráfico de casos confirmados
plt.figure(figsize=(10, 6))
plt.plot(grouped.index, grouped['confirmed'], label='Casos Confirmados')
plt.xlabel('Data')
plt.ylabel('Casos Confirmados')
plt.title('Tendência de Casos Confirmados em Goiás (2021)')
plt.legend()
plt.show()

# Gráfico de mortes
plt.figure(figsize=(10, 6))
plt.plot(grouped.index, grouped['deaths'], label='Mortes', color='red')
plt.xlabel('Data')
plt.ylabel('Mortes')
plt.title('Tendência de Mortes em Goiás (2021)')
plt.legend()
plt.show()


# Calcula-se a taxa de letalidade (relação entre mortes e casos confirmados) ao longo do tempo.
# 
# Método: Dividir o número de mortes pelo número de casos confirmados para obter a taxa de letalidade diária.

# In[11]:


import matplotlib.pyplot as plt

# Cria uma cópia do DataFrame original
cases_copy = cases.copy()

# Calcula a coluna 'Letalidade' na cópia do DataFrame
cases_copy['Letalidade'] = cases_copy['deaths'] / cases_copy['confirmed'] * 100

# Gráfico da letalidade usando a cópia do DataFrame
plt.figure(figsize=(10, 6))
plt.plot(cases_copy['date'], cases_copy['Letalidade'], label='Taxa de Letalidade (%)', color='orange')
plt.xlabel('Data')
plt.ylabel('Taxa de Letalidade (%)')
plt.title('Taxa de Letalidade em Goiás (2021)')
plt.legend()
plt.show()


# Calcula-se a taxa de crescimento diário dos casos confirmados e mortes para avaliar se o número de infecções estava aumentando ou diminuindo ao longo do tempo.
# 
# Método: Calcular a taxa de crescimento percentual usando a diferença entre dias consecutivos.

# In[12]:


cases['Crescimento_Confirmados'] = cases['confirmed'].pct_change() * 100
cases['Crescimento_Mortes'] = cases['deaths'].pct_change() * 100

# Gráfico de taxa de crescimento de casos confirmados
plt.figure(figsize=(10, 6))
plt.plot(cases['date'], cases['Crescimento_Confirmados'], label='Taxa de Crescimento de Casos Confirmados', color='green')
plt.xlabel('Data')
plt.ylabel('Taxa de Crescimento (%)')
plt.title('Taxa de Crescimento de Casos Confirmados em Goiás (2021)')
plt.legend()
plt.show()

# Gráfico de taxa de crescimento de mortes
plt.figure(figsize=(10, 6))
plt.plot(cases['date'], cases['Crescimento_Mortes'], label='Taxa de Crescimento de Mortes', color='purple')
plt.xlabel('Data')
plt.ylabel('Taxa de Crescimento (%)')
plt.title('Taxa de Crescimento de Mortes em Goiás (2021)')
plt.legend()
plt.show()


# Adiciona colunas de mês e ano ao dataframe utilizando **.apply**, formata as datas para strings com ano e mês (**%Y-%m**) e apenas ano (**%Y**).

# In[13]:


cases['month'] = cases['date'].apply(lambda date: date.strftime('%Y-%m'))
cases['year']  = cases['date'].apply(lambda date: date.strftime('%Y'))


# Estima-se a população baseada na razão entre casos confirmados e a taxa de incidência.
# 
# Remove a coluna **incident_rate**: A coluna de taxa de incidência é descartada.

# In[14]:


cases['population'] = round(100000 * (cases['confirmed'] / cases['incident_rate']))
cases = cases.drop('incident_rate', axis=1)


# Define a função **get_trend** que classifica a tendência de crescimento ou redução dos casos e mortes (e.g.,***downward, upward, stable***).
# 
# Depois, processa os dados:
# 
# Para Goiás filtra os dados, calcula médias móveis de 7 dias para casos confirmados e mortes, e determina a tendência baseada na média móvel ajustada.
# 
# Concatenação: Junta os dados processados por estado em um DataFrame consolidado.

# In[15]:


cases_ = None
cases_is_empty = True

def get_trend(rate: float) -> str:

  if np.isnan(rate):
    return np.NaN

  if rate < 0.75:    # Se a divisão for menor que 0.75 (correção 0.85)
    status = 'downward'
  elif rate > 1.15:
    status = 'upward'
  else:
    status = 'stable'

  return status


for state in cases['state'].drop_duplicates():

  cases_per_state = cases.query(f'state == "{state}"').reset_index(drop=True)
  cases_per_state = cases_per_state.sort_values(by=['date'])

  cases_per_state['confirmed_1d'] = cases_per_state['confirmed'].diff(periods=1)
  cases_per_state['confirmed_moving_avg_7d'] = np.ceil(cases_per_state['confirmed_1d'].rolling(window=7).mean())
  cases_per_state['confirmed_moving_avg_7d_rate_14d'] = cases_per_state['confirmed_moving_avg_7d']/cases_per_state['confirmed_moving_avg_7d'].shift(periods=14)
  cases_per_state['confirmed_trend'] = cases_per_state['confirmed_moving_avg_7d_rate_14d'].apply(get_trend)

  cases_per_state['deaths_1d'] = cases_per_state['deaths'].diff(periods=1)
  cases_per_state['deaths_moving_avg_7d'] = np.ceil(cases_per_state['deaths_1d'].rolling(window=7).mean())
  cases_per_state['deaths_moving_avg_7d_rate_14d'] = cases_per_state['deaths_moving_avg_7d']/cases_per_state['deaths_moving_avg_7d'].shift(periods=14)
  cases_per_state['deaths_trend'] = cases_per_state['deaths_moving_avg_7d_rate_14d'].apply(get_trend)

  if cases_is_empty:
    cases_ = cases_per_state
    cases_is_empty = False
  else:
    cases_ = pd.concat([cases_, cases_per_state],axis=0, ignore_index=True)

cases = cases_
cases_ = None


# Finalmente, converte algumas colunas para o tipo Int64 para melhor manipulação dos dados.
# 
# Tudo isso resulta em um DataFrame mais limpo e informativo, focado nas tendências de casos confirmados e mortes para análise.

# In[16]:


cases['population'] = cases['population'].astype('Int64')
cases['confirmed_1d'] = cases['confirmed_1d'].astype('Int64')
cases['confirmed_moving_avg_7d'] = cases['confirmed_moving_avg_7d'].astype('Int64')
cases['deaths_1d'] = cases['deaths_1d'].astype('Int64')
cases['deaths_moving_avg_7d'] = cases['deaths_moving_avg_7d'].astype('Int64')


# Por fim, vamos reorganizar as colunas e conferir o resultado final.

# In[17]:


cases = cases[['date', 'country', 'state', 'population', 'confirmed', 'confirmed_1d', 'confirmed_moving_avg_7d', 'confirmed_moving_avg_7d_rate_14d', 'confirmed_trend', 'deaths', 'deaths_1d', 'deaths_moving_avg_7d', 'deaths_moving_avg_7d_rate_14d', 'deaths_trend', 'month', 'year']]


# In[18]:


cases.head(n=25)


# E por fim salvamos em um arquivo **.csv.**

# In[19]:


cases.to_csv('./covid-cases-goias.csv', sep=',', index=False)


# Com a análise chegando ai fim percebemos que o numero de casos e de mortes no estado de Goias em dezembro esta menor do que registrado no inicio de 2021, onde a partir de Maio percebe-se claramente essa queda continua do numero de casos.
