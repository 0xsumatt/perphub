import asyncio

import pandas as pd
import requests
import streamlit as st
from streamlit_autorefresh import st_autorefresh
from zo import Zo



import json

st.set_page_config (
    page_title = "Basic Perp Info",
    page_icon = "random",
    layout = "wide",
    menu_items = {
        "About":"",
        
    
    })
refresh = st_autorefresh(interval=60000)


def HubbleData():
    st.header("Hubble Exchange ")
    s = requests.session()
    get_json = s.get("https://mainnet-efb9f.web.app/market/AVAX-PERP")
    json_data = json.loads(get_json.text)
    FundingRate = float(round(json_data['predictedFR'],3))
    MarkPrice  = float(json_data['markPrice'])
    FundingRate_df= pd.DataFrame([FundingRate],columns = ["AVAXPERP"],index = ['Predicted Funding Rate (1H)'])
    MarkPrice_df = pd.DataFrame([MarkPrice],columns = ["AVAXPERP"],index = ['Mark Price'])
    APR = FundingRate * 8760
    APR_df = pd.DataFrame([APR],columns = ["AVAXPERP"],index = ['APR'])
    df = pd.concat([MarkPrice_df,FundingRate_df,APR_df])
    st.write(df)


        
def MangoData():
        
    st.header("Mango Markets")
        
    base_df = pd.read_json("https://mango-all-markets-api.herokuapp.com/markets")
    df_index = base_df.set_index('name',drop = False)
    df_choice = df_index.loc['MNGO-PERP':'GMT-PERP']
    df2= df_choice[['markPrice','change24h','funding1h']]
    add_APR= df2['funding1h']*8760
    pd.set_option('mode.chained_assignment', None)
    df2['Predicted APR ']=add_APR
    
    convert_format = df2.transpose()
    st.write(convert_format)
            
            
            
            
def ftxData():
    st.header("FTX")
    s = requests.session()
    req = s.get("https://ftxpremiums.com/assets/data/funding.json")

    df = pd.read_json(req.text)
    df = df.set_index('name',drop = False)


    df1 = df.loc['BTC-PERP':'SRM-PERP']

    df1 = df1[['predicted_funding',"volume"]]
    new_row = df1['predicted_funding']/8760
    df1['Hourly Predicted funding']=new_row
    renamed_df = df1.rename(columns = {"predicted_funding":'APR'},inplace = True)
    df3 = df1.transpose()


    st.write(df3)

async def Zero_one():

    st.header("01 Exchange")
    markets = ["BTC-PERP","SOL-PERP","ETH-PERP","AVAX-PERP","APE-PERP","NEAR-PERP","GMT-PERP","SYN-PERP"]
    
    zo = await Zo.new(cluster="mainnet",create_margin=False, load_margin=False)
    list = []
    for i in markets :
         value = (zo.markets[i].funding_info.hourly)*100
         list.append(value)
    
    apr = []
    for i in markets:
         value = ((zo.markets[i].funding_info.hourly)*100)*8760
         apr.append(value)
    
      
    df = pd.DataFrame([list], columns= [markets],index = ["Predicted Funding rate (1h)"])
    df2 = pd.DataFrame([apr],columns= [markets],index = ["APR"])
    df = pd.concat([df,df2])

    
    st.write(df)

        
st.write("TODO : ")

st.write("1.Implement more exchanges")
st.write("2.Add styling")

if __name__ == "__main__":
    
    Hubble = HubbleData()
    mango = MangoData()
    zero_one = asyncio.run(Zero_one())
    ftx = ftxData()
    

    refresh
