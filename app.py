import streamlit as st
import requests
import json
import pandas as pd

token = st.secrets["token"]
databasdID = st.secrets["databaseID"]
admin_ID = st.secrets["admin_ID"]
admin_PW = st.secrets["admin_PW"]

notion_api_link_query = f"https://api.notion.com/v1/databases/{databasdID}/query"
notion_api_link_add = "https://api.notion.com/v1/pages"

headers = {
    "Authorization": token,
    "accept": "application/json",
    "Notion-Version": "2022-06-28",
    "content-type": "application/json"
}

def parseData(data):
    imei_list = []
    iccid_list = []
    carrier_list = []
    rat_list = []
    owner_list = []
    desc_list = []
    
    for result in data['results']:
        imei_output = result['properties']['IMEI']['rich_text'][0]['plain_text']
        iccid_outout = result['properties']['ICCID']['rich_text'][0]['plain_text']
        carrier_output = result['properties']['CARRIER']['select']['name']
        rat_output = result['properties']['RAT']['select']['name']
        owner_output = result['properties']['OWNER']['rich_text'][0]['plain_text']
        if not result['properties']['Description']['rich_text']:
            desc_output = ''
        else:
            desc_output = result['properties']['Description']['rich_text'][0]['plain_text']
        imei_list.append(imei_output)
        iccid_list.append(iccid_outout)
        carrier_list.append(carrier_output)
        rat_list.append(rat_output)
        owner_list.append(owner_output)
        desc_list.append(desc_output)
        
    df = pd.DataFrame({
        'IMEI' : imei_list,
        'ICCID' : iccid_list,
        'CARRIER' : carrier_list,
        'RAT' : rat_list,
        'OWNER' : owner_list,
        'Description' : desc_list 
    })
    
    filter_container = st.container()
    
    with filter_container:
        if select_type == "ICCID":
            search_str = st.text_input("Input")
            str_expr = f"ICCID.str.contains('{search_str}', case=False)"
            df = df.query(str_expr)
        
        elif select_type == "CARRIER":
            search_str = st.selectbox("Input", ["","SKT","KT","LGU","other"])
            str_expr = f"CARRIER.str.startswith('{search_str}')" # SKT, KT
            df = df.query(str_expr)
        
        elif select_type == "RAT":
            search_str = st.selectbox("Input", ["","NB","eMTC","LTE","5G"])
            str_expr = f"RAT.str.contains('{search_str}', case=False)"
            df = df.query(str_expr)

    st.dataframe(df, use_container_width=True)
    st.write(f'Total : :blue[{len(df.index)}] pcs')
    
def readDatabase():
    payload = {"page_size": 100}
    response = requests.post(notion_api_link_query, json=payload, headers=headers)
    data_bytes = response.content
    data_str = data_bytes.decode('utf-8')
    data = json.loads(data_str)

    if response :
        # if '\"status\":200' in response.text:
        parseData(data)
    
    elif '\"status\":400' in response.text:
        err = f'[readDatabase] {response}'
        st.write(err)
        
    elif '\"status\":401' in response.text:
        err = f'[readDatabase] {response}'
        st.write(err)
        
def writeDatabase():
    payload_dict = {
        "parent": {
            "type": "database_id",
            "database_id": databasdID
        },
        "properties": {
            "IMEI": {
                "rich_text": [{ "text": { "content": imei_input } }]
            },
            "ICCID": {
                "rich_text": [{ "text": { "content": iccid_input } }]
            },
            "CARRIER": {
                "select": { "name": carrier_input }
            },
            "RAT": {
                "select": { "name": rat_input }
            },
            "OWNER": {
                "rich_text": [{ "text": { "content": owner_input } }]
            },
            "Description": {
                "rich_text": [{ "text": { "content": desc_input } }]
            }
        }
    }
    payload_json = json.dumps(payload_dict)
    response = requests.post(notion_api_link_add, data=payload_json, headers=headers)
    
    if response :
        # if '\"status\":200' in response.text:
        st.write('Done!')
    
    elif '\"status\":400' in response.text:
        err = f'[writeDatabase] {response}'
        st.write(err)
        
    elif '\"status\":401' in response.text:
        err = f'[writeDatabase] {response}'
        st.write(err)
        
def deleteDatabase():
    st.write('[TBD] deleteDatabase')
    
# start from here
st.set_page_config(page_title = "USIM DB")
st.title("USIM DB")
st.write("This app is USIM information management tool based on Jay's notion database. Read and write available only.")
    
tab1, tab2 = st.tabs(["read mode","write mode"])
with tab1:
    select_type = st.selectbox("Search with",("ICCID","CARRIER","RAT"))
    with st.spinner("Waiting for readDatabase..."):
        readDatabase()
        
with tab2:
    with st.form("auth"):
        id_input = st.text_input("ID")
        pw_input = st.text_input("PW")
        auth = st.form_submit_button("Submit")
          
    if id_input == admin_ID and pw_input == admin_PW:
        with st.form("write"):
            imei_input = st.text_input("IMEI")
            iccid_input = st.text_input("ICCID")
            carrier_input = st.selectbox("CARRIER", ["SKT","KT","LGU","other"])
            rat_input = st.selectbox("RAT", ["NB","eMTC","LTE","5G"])
            owner_input = st.text_input("OWNER")
            desc_input = st.text_input("Description")
            write = st.form_submit_button("Write")
            
            if write:
                if not imei_input or not iccid_input or not owner_input:
                    st.write("please fill in the blanks!")
                else:
                    with st.spinner("Waiting for writeDatabase..."):
                        writeDatabase()
    elif (id_input != admin_ID or pw_input != admin_PW) and auth:
        st.write("please check account info")
