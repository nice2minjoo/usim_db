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
        carrier_output = result['properties']['CARRIER']['rich_text'][0]['plain_text']
        rat_output = result['properties']['RAT']['rich_text'][0]['plain_text']
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
        
     st.write(pd.DataFrame({
        'IMEI' : imei_list,
        'ICCID' : iccid_list,
        'CARRIER' : carrier_list,
        'RAT' : rat_list,
        'OWNER' : owner_list,
        'Description' : desc_list
    }))
    st.write('Total : {} pcs'.format(len(imei_list)))
    
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
                "rich_text": [{ "text": { "content": carrier_input } }]
            },
            "RAT": {
                "rich_text": [{ "text": { "content": rat_input } }]
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
st.title("USIM DB")
with st.form("INIT"):
    st.write("This is USIM information based on Jay's notion database. Read and write available only.")
    mode_select = st.radio("Mode select", ["read mode","write mode"])
    select_button = st.form_submit_button("Select")
    
if "read mode" in mode_select:
    with st.form("read"):
        read = st.form_submit_button("Read")
        st.write()
        
        if read:           
            with st.spinner("Waiting for readDatabase..."):
                readDatabase()
                
else:
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
                    # st.write(':red[please fill in the blanks]')
                    st.write("please fill in the blanks!")
                else:
                    with st.spinner("Waiting for writeDatabase..."):
                        writeDatabase()
    elif auth:
        st.write("please check account info!")
                
