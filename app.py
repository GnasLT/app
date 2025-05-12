import streamlit as st
from datetime import datetime, timedelta
import time
import sensordata as ss
import SensorData as SS
import pandas as pd
from streamlit_option_menu import option_menu
import Plants
import asyncio
import threading
from streamlit.runtime.scriptrunner import add_script_run_ctx
from streamlit_autorefresh import st_autorefresh



def main_page():
    current_page = slidebar()
    if current_page == 'Home':
        st.title("Plant Management Dashboard")
        sessionstatecreate()
        show_plant_table()
        createform()
        show_sensor_table()
        st_autorefresh(interval=6000)

    elif current_page == 'Chart':
        st.title('Chart')
        selectbox = st.selectbox('Choose an option: ',['24 hours',' 7 days','1 month' ])
        
        if selectbox == '24 hours':
            create24hchart()
        if selectbox == '7 days':
            create7dchart()
        if selectbox == '1 month':
            create30dchart()
#   st.

def create30dchart():
    sensor = SS.SensorData()
    #temp = sensor.findone({'plant_id': 'plant1'}).get('time')
    
    deltatime = datetime.now() - timedelta(day=30)
    query = {
        "$expr": {
            "$gt": [
                {
                    "$dateFromString": {
                        "dateString": "$time",  
                        "format": "%d-%m-%Y_%H:%M"  
                    }
                },
                deltatime
            ]
        }
    }
    listsensor = sensor.findmany(query)
    for doc in listsensor:
        st.write(doc)

def create7dchart():
    sensor = SS.SensorData()
    #temp = sensor.findone({'plant_id': 'plant1'}).get('time')
    
    deltatime = datetime.now() - timedelta(day=7)
    query = {
        "$expr": {
            "$gt": [
                {
                    "$dateFromString": {
                        "dateString": "$time",  
                        "format": "%d-%m-%Y_%H:%M"  
                    }
                },
                deltatime
            ]
        }
    }
    listsensor = sensor.findmany(query)
    for doc in listsensor:
        st.write(doc)

def create24hchart():
    sensor = SS.SensorData()
    #temp = sensor.findone({'plant_id': 'plant1'}).get('time')
    
    deltatime = datetime.now() - timedelta(hours=24)
    query = {
        "$expr": {
            "$gt": [
                {
                    "$dateFromString": {
                        "dateString": "$time",  
                        "format": "%d-%m-%Y_%H:%M"  
                    }
                },
                deltatime
            ]
        }
    }
    listsensor = sensor.findmany(query)
    for doc in listsensor:
        st.write(doc)

    

def sessionstatecreate():
    if 'selected_plant' not in st.session_state:
        st.session_state.selected_plant = {'id': '', 'name': ''}
        
    if 'showsensor' not in st.session_state:
        st.session_state.showsensor = False
            
    if 'sensorvalue' not in st.session_state:
        st.session_state.sensorvalue = []
    
    if 'sensor' not in st.session_state:
        st.session_state.sensor = None
        
    if 'thread' not in st.session_state:
        st.session_state.thread = None
       
    if 'rerun' not in st.session_state:
        st.session_state.rerun = False
       
        
def createform():
    with st.form("plant_form"):
        st.subheader("Add Plant or Select Plant Monitor ")
        col1, col2 = st.columns(2)
        
        
        
        plant_id = col1.text_input("Plant ID", 
                            value=st.session_state.selected_plant['id'],
                            key="plant_id")
        plant_name = col2.text_input("Plant Name", 
                            value=st.session_state.selected_plant['name'],
                            key="plant_name")
            
        time_sleep = col1.text_input("Time ", key="time",placeholder = 'Minutes')
        col_start, col_stop, col_add, col_up , col_del = st.columns([3, 3, 3, 3, 3])
        
        
        #create button
        submitted_start = col_start.form_submit_button("Start")
        submitted_stop = col_stop.form_submit_button("Stop")
        submitted_add = col_add.form_submit_button("Add")
        submitted_up = col_up.form_submit_button("Update")
        submitted_del = col_del.form_submit_button("Delete")
        
        if submitted_stop: handle_start_stop('stop' ,st.session_state.selected_plant.get('id'))
        if submitted_add: handle_plant_operation('add', plant_id, plant_name)
        if submitted_up: handle_plant_operation('update', plant_id, plant_name)
        if submitted_del: handle_plant_operation('delete', plant_id)
        if submitted_start:
            handle_start_stop('start' ,st.session_state.selected_plant.get('id'), time_sleep)
            #handle_plant_operation('start', st.session_state.selected_plant.get('id'), time_sleep=time_sleep)
       
        st_autorefresh(interval=0.1*60, key="data_refresh")
       
    
 

def show_sensor_table():
    
    if 'sensor' not in st.session_state:
        st.session_state.sensor = None

    
    if st.session_state.showsensor == False:
        return

    st.subheader("Sensor List")
    if st.session_state.sensor != None:
        while not st.session_state.sensor.data_queue.empty():
            new_data = st.session_state.sensor.data_queue.get_nowait()
            st.session_state.sensorvalue.append(new_data)
           
            
        
    if not st.session_state.sensorvalue:
        st.warning("No data found in database!")
    else:
        df = pd.DataFrame(st.session_state.sensorvalue)
        st.dataframe(
            st.session_state.sensorvalue,
            use_container_width=True,
            key = 'sensor_table',
            )
        
   

    
    
def handle_start_stop(operation, plant_id='', time_sleep=''):
    plant = Plants.Plant()
    if time_sleep == '':
        time_sleep = 20
    if operation =='start':
        if plant.check_plant_exist(plant_id) or plant_id != '':
            sessionstatecreate()
            if st.session_state.sensor == None and st.session_state.thread == None:
                st.session_state.sensor = SS.SensorData(plant_id, float(time_sleep))
                st.session_state.thread = threading.Thread(target = st.session_state.sensor.start, daemon=True ) #daemon dam bao thread dung 
                add_script_run_ctx(st.session_state.thread)
                st.session_state.thread.start()
                st.session_state.showsensor = True
            return True
        else:
            return st.warning("Plant dont exist")
    elif operation =='stop':
        if st.session_state.sensor != None and st.session_state.thread != None:
            st.session_state.sensor.stop()
            st.session_state.thread.join(timeout = 10)
            del st.session_state.sensor 
            del st.session_state.thread 
            return st.success("Stopped")
        
        else: return st.warning("No sensor")

def handle_plant_operation(operation, plant_id='', plant_name='', time_sleep = ''):
    plant = Plants.Plant()
    if operation in ['add', 'update'] and (not plant_id or not plant_name):
        return st.warning("Missing ID or Name ")
    if operation in ['delete', 'start'] and not plant_id:
        return st.warning("Missing Plant ID")
    if time_sleep == '':
        time_sleep = 15
    try:
        ops = {
            'add': lambda: (
                plant.insertone(plant_id, plant_name),
                st.session_state.selected_plant.update({'id': plant_id, 'name': plant_name}),
                st.success("")
            ) if not plant.check_plant_exist(plant_id) else st.warning("Plant exist"),
            
            'update': lambda: (
                plant.updateone(
                    {'_id': st.session_state.selected_plant['id'],
                    'name': st.session_state.selected_plant['name']},
                    {'_id': plant_id, 'name': plant_name}
                ),
                st.session_state.selected_plant.update({'id': plant_id, 'name': plant_name}),
                st.success("")
            ) if plant.check_plant_exist(plant_id) else st.warning("Plant dont exist"),
            
            'delete': lambda: (
                plant.deleteone(plant_id),
                st.session_state.selected_plant.update({'id': '', 'name': ''}),
                st.success("")
            ) if plant.check_plant_exist(plant_id) else st.warning("Plant dont exist"),
            
        }
        ops.get(operation, lambda: st.warning(""))()
        
    except Exception as e:
        st.error(f"Error: {e}")
        
    finally:
        if operation != 'stop':
            del plant


def Checktext(check):
    if check == '' or check == None:
        return False
    return True




    
def show_plant_table():
    st.subheader("Plant List")
    plants = Plants.Plant().findmany()  #
    if not plants:
        st.warning("No plants found in database!")
    else:
        data = pd.DataFrame(plants)
        
        df = st.dataframe(
                    data,
                    on_select='rerun',
                    selection_mode='single-row',
                    hide_index = True,
                    use_container_width=True,
                    key = 'plant_table')
                    
        if len(df.selection['rows']):
            selected_row = df.selection['rows'][0]

            st.session_state.selected_plant = {
                'id': data.iloc[selected_row]['_id'],
                'name': data.iloc[selected_row]['name']
        }
        else:
            st.session_state.selected_plant = {
                'id': "",
                'name': ""
                }
        #st.write(st.session_state.selected_plant)
        #st.rerun()
def slidebar():
    with st.sidebar:
        selected=option_menu(
            menu_title = "Menu",
            options = ["Home","Chart","Analysis"],
            icons = ["house-heart-fill","bi bi-graph-up", "bi bi-clipboard2-data"],
            menu_icon = "heart-eyes-fill",
            default_index = 0,
    )
    return selected
if __name__ == "__main__":
    main_page()
