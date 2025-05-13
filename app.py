import streamlit as st
from datetime import datetime, timedelta
import time
import SensorData as SS
import pandas as pd
from streamlit_option_menu import option_menu
import Plants
import asyncio
import threading
from streamlit.runtime.scriptrunner import add_script_run_ctx
from streamlit_autorefresh import st_autorefresh
import os
import ImageData
import cv2
from multiprocessing.pool import ThreadPool

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
        listplant = Plants.Plant().findmany()
        ids = [item['_id'] for item in listplant]
        col1, col2, col3 = st.columns(3)

        with col1:
            selecttime = st.selectbox('Choose an option: ',['24 hours','7 days','1 month' ])
        with col3:
            selecttype = st.selectbox('Choose an option: ',['Light','Temperature, Humidity','CO2' ])
        with col2:
            selectplant = st.selectbox('Choose an option: ',   ids)
            
        if selecttime == '24 hours':
            deltatime = datetime.now() - timedelta(hours=24)
            light,t,h,co2 = get_data_base_time(deltatime,selectplant)
            if selecttype == 'Light':
                createchart(light)
            if selecttype == 'Temperature, Humidity':
                createchart(t,h)
            if selecttype == 'CO2':
                createchart(co2)
                
        if selecttime == '7 days':
            deltatime = datetime.now() - timedelta(days= 7)
            light,t,h,co2 = get_data_base_time(deltatime,selectplant)
            if selecttype == 'Light':
                createchart(light)
            if selecttype == 'Temperature, Humidity':
                createchart(t,h)
            if selecttype == 'CO2':
                createchart(co2)
                
        if selecttime == '1 month':
            deltatime = datetime.now() - timedelta(days=30)
            light,t,h,co2 = get_data_base_time(deltatime,selectplant)
            if selecttype == 'Light':
                createchart(light)
            if selecttype == 'Temperature, Humidity':
                createchart(t,h)
            if selecttype == 'CO2':
                createchart(co2)
            
    elif current_page == 'Analysis':
        st.title("Plant Timelapse Analysis")
        listplant = Plants.Plant().findmany()
        ids = [item['_id'] for item in listplant]
        selectplant = st.selectbox('Choose an option: ',   ids)
        if selectplant:
            show_timelapse(selectplant)

def createchart(datalist, temp = None):
    if temp != None:
        df = pd.DataFrame({'Temperature': datalist,
                            'Humidity': temp })
        st.line_chart(df, x_label = 'Total Value', y_label = 'Value', color=[ "#0000FF","#FF0000"])
    else:
        df = pd.DataFrame(datalist)
        st.line_chart(df,x_label = 'Total Value', y_label = 'Value')

def get_data_base_time(time,plant_id):
    sensor = SS.SensorData()
    query = [
    {
        '$match': {
            '$expr': {
                '$and': [
                    {
                        '$gt': [
                            {
                                '$dateFromString': {
                                    'dateString': '$time',
                                    'format': '%d-%m-%Y_%H:%M'
                                }
                            },
                            time.strftime('%d-%m-%Y_%H:%M')
                        ]
                    },
                    {
                        '$eq': ['$plant_id', plant_id]
                    }
                ]
            }
        }
    }
]
    listsensor = sensor.aggregate(query)
    light = []
    h = []
    t = []
    co2 = []
    
    for item in listsensor:
        for value in item['values']:
            if value['type'] == 'light':
                light.append(value['value'])
            elif value['type'] == 'temperature':
                t.append(value['value'])   
            elif value['type'] == 'humidity':
                h.append(value['value'])   
            else:
                co2.append(value['value'])       
    return light,t,h,co2

    

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
    
def get_sorted_images(plant_id):
    pipeline = [
        {
            '$match': {
                'plant_id': plant_id
                    },
        },
        {
            '$project': 
            {
                'plant_id':1,
                'time': 
                {
                '$dateFromString': 
                    {
                    'dateString': '$time',
                    'format': '%d-%m-%Y_%H:%M'
                    }
                },
                 'values': {
                        '$map': {
                            'input': '$values',
                            'as': 'value',
                            'in': { 'path': '$$value.path' ,'type': '$$value.type' }
                        }
                    }
            }
        },
        { '$sort': { 'time' : 1} } ] 

    colle = ImageData.ImageData(plant_id) 
    temp = colle.find_time(pipeline)
    rgb = []
    nir = []
    for item in temp:
        if 'values' in item and isinstance(item['values'], list):
            for value_item in item['values']:
                if 'type' in value_item and 'path' in value_item:
                    if value_item['type'] == 'rgb':
                        rgb.append(value_item['path'])
                    elif value_item['type'] == 'nir':
                        nir.append(value_item['path'])
                        
    return rgb,nir

def process_image(path,resize_ratio=0.8, quality = 0.8):
    img = cv2.imread(path)

    if resize_ratio != 1:
        h, w = img.shape[:2]
        
        img = cv2.resize(
            img,
            (int(w * resize_ratio), int(h * resize_ratio)),
             interpolation=cv2.INTER_AREA
        )
    return img

@st.cache_data
def create_timelapse(image_paths, output_path, fps=24):
    
    

    
    frame = cv2.imread(image_paths[0])

    height, width, _ = frame.shape
    
    
    fourcc = cv2.VideoWriter_fourcc(*'avc1')  
    video = cv2.VideoWriter(output_path, fourcc, fps, (int(width*0.8),int(height*0.8)))
    
    if not video.isOpened():
        st.error("Failed to create video file")
        return False

   
    frames=[]
    success_count = 0
    with ThreadPool(os.cpu_count()) as pool:  
        frames = pool.map(process_image, image_paths)
        
    for frame in frames:
        if frame is not None:
            video.write(frame)

        success_count += 1

        if success_count % 100 == 0:
            gc.collect()

    video.release()
    return True

def show_timelapse(plant_id):
    

    os.makedirs('/home/gnas/Desktop/thesis', exist_ok=True)
    
    rgb_paths, nir_paths = get_sorted_images(plant_id)
    col1, col2 = st.columns(2)
    

    rgb_video_path = '/home/gnas/Desktop/thesis/rgb_timelapse.mp4'
    nir_video_path = '/home/gnas/Desktop/thesis/nir_timelapse.mp4'
    
    
    st.subheader("RGB Timelapse")
    if rgb_paths:
        if create_timelapse(rgb_paths, rgb_video_path):
            st.video(rgb_video_path)
            open(rgb_video_path, "rb") 
        else:
            st.error("Failed to create RGB timelapse")
    else:
        st.warning("No RGB images found")


    st.subheader("NIR Timelapse")
    if nir_paths:
        if create_timelapse(nir_paths, nir_video_path):
                st.video(nir_video_path)
                open(nir_video_path, "rb") 
        else:
            st.error("Failed to create NIR timelapse")
    else:
        st.warning("No NIR images found")

if __name__ == "__main__":
    main_page()
