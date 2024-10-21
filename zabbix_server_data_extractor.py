import os
import requests
from bs4 import BeautifulSoup
import pandas as pd
import warnings

# InsecureRequestWarning
warnings.filterwarnings("ignore", message="Unverified HTTPS request")

# To login
login_url = 'https://your_login_url.com'  

# Login Data
login_data = {
    'name': os.getenv('LOGIN_NAME'),  
    'password': os.getenv('LOGIN_PASSWORD'),  
    'autologin': '1',  
    'enter': 'Sign in' 
}

# Create a session
session = requests.Session()

# Send login request
login_response = session.post(login_url, data=login_data, verify=False)

# To Confirm if you are Logged in or not 
if login_response.status_code == 200 and "You are not logged in" not in login_response.text:
    print("Successfully logged in!")

    # Target URL fetch from it
    target_url = 'https://your_target_url.com'

    # Using the session to reach the URL
    target_response = session.get(target_url, verify=False)

    if target_response.status_code == 200:
        # Using bs4 to arrange the page 
        soup = BeautifulSoup(target_response.text, 'html.parser')
        
        # looking for all <a> to reach to host_id 
        server_info = []
        for link in soup.find_all('a'):
            # To check if this <a> contain on data-menu-popup or not 
            data_menu_popup = link.get('data-menu-popup')
            if data_menu_popup and 'hostid' in data_menu_popup:
                #Fetch the host id for every server 
                start = data_menu_popup.find('"hostid":') + 9
                end = data_menu_popup.find('}', start)
                host_id = data_menu_popup[start:end].strip(' "')
                
                # fetch the servers name
                server_name = link.get_text().strip()

                # IP for every server
                interface_element = link.find_next('td', class_='nowrap')
                interface_number = interface_element.get_text() if interface_element else "N/A"
                interface_number = interface_number.split(':')[0]

                # Get in server url to extract Utilization
                server_link = f"https://your_server_url.com&filter_hostids%5B0%5D={host_id}"
                server_response = session.get(server_link, verify=False)
                if server_response.status_code == 200:
                    # Using bs4 to arrange the page
                    server_soup = BeautifulSoup(server_response.text, 'html.parser')

                    # Looking on CPU utilization
                    cpu_utilization_value = None
                    cpu_utilization_label = server_soup.find('span', text='CPU utilization')
                    if cpu_utilization_label:
                        # Fetch the CPU utilizaation
                        cpu_utilization_td = cpu_utilization_label.find_parent('div').find_next('td').find_next_sibling('td')
                        if cpu_utilization_td:
                            cpu_utilization_value = cpu_utilization_td.get_text(strip=True)

                    # Looking on Memory utilization 
                    memory_utilization_value = None
                    memory_utilization_label = server_soup.find('span', text='Memory utilization')
                    if memory_utilization_label:
                        # Fetch the Memory utilizaation
                        memory_utilization_td = memory_utilization_label.find_parent('div').find_next('td').find_next_sibling('td')
                        if memory_utilization_td:
                            memory_utilization_value = memory_utilization_td.get_text(strip=True)

                    disk_labels = ['C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K' , 'L' , 'M' , 'N', 'O' , 'P', 'Q' , 'R' , 'S' , 'T' , 'U' ,'V' , 'W' , 'X' , 'Y' , 'Z']
                    disk_utilization_values = {}

                    for label in disk_labels:
                        utilization_value = None
                        Total_space_value = None
                        Used_space_value = None
                        utilization_label = server_soup.find('span', text=f'{label}:: Space utilization')
                        Total_space_label = server_soup.find('span', text=f'{label}:: Total space')
                        Used_space_label = server_soup.find('span', text=f'{label}:: Used space')

                        if utilization_label:
                            # Fetch the Space utilization
                            utilization_td = utilization_label.find_parent('div').find_next('td').find_next_sibling('td')
                            if utilization_td:
                                utilization_value = utilization_td.get_text(strip=True)
                        
                        if Total_space_label:
                            # Fetch the Space utilization
                            Total_space_td = Total_space_label.find_parent('div').find_next('td').find_next_sibling('td')
                            if Total_space_td:
                                Total_space_value = Total_space_td.get_text(strip=True)

                        if Used_space_label:
                            # Fetch the Space utilization
                            Used_space_td = Used_space_label.find_parent('div').find_next('td').find_next_sibling('td')
                            if Used_space_td:
                                Used_space_value = Used_space_td.get_text(strip=True)
                
                        # Saving in Dictionary
                        disk_utilization_values[f'{label}::Space '] = utilization_value
                        disk_utilization_values[f'{label}::Total Space '] = Total_space_value
                        disk_utilization_values[f'{label}::Used Space'] = Used_space_value

                    # Add the information to list
                    server_info.append({
                        'Server Name': server_name,
                        'IP': interface_number,
                        'CPU Utilization': cpu_utilization_value,
                        'Memory Utilization': memory_utilization_value,
                        **disk_utilization_values
                    })

                else:
                    print("Can't get access")

        # Save in Excel file
        df = pd.DataFrame(server_info)
        df.to_excel("servers_utilization.xlsx", index=False)
        print("Server information with Host ID has been saved to 'servers_utilization.xlsx' successfully!")

    else:
        print(f"Error: Unable to retrieve the target page (Status code: {target_response.status_code})")
else:
    print(f"Error: Login failed (Status code: {login_response.status_code})")
