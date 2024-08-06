import requests
import json
import numpy as np
from PIL import Image
"""Authorize
Function for authorization on the network. 
inputs: -
output: session_token: unique session token to be used to retrieve data
"""
def authorize():
    session_url = "https://prod.meandair.com/api/v1/auth/session"
    username = "ubotica"
    password = "tE9sKBJhhPEdZ4qn"

    payload = {'uid': username, 'passwd': password}

    # Making the POST request to get the auth token
    response = requests.post(session_url, json=payload)
    if response.status_code == 200:
        session_token = response.text
        print(f"Example URL: https://prod.meandair.com/api/v1/tiles/{{weather}}/{{zoom}}_{{altitude}}_{{col}}_{{row}}_{{datetime}}.png?session={session_token}")
        return session_token
    else:
        print(f'Error requesting from URL {session_url}: {response.status_code}')

""" Request weather TAF
Request weather for one location, returns nowcast data (e.g. cloud cover) for t0, t0 +1hr, t0 +2 etc. 
for a specified bounding box.
Resolution of data can not be changed
input: 
            session token: unique session token to be used to retrieve data
output: 
            string containing lots of data, amongst others the cloud cover and surface visibility.
https://hq.meandair.com/api/v1.html#tag/Airport-and-Location-Weather/operation/awTaf
"""
def requestWeatherTAF(session_token, lat, long):
    url = f"https://prod.meandair.com/api/v1/aw-taf?latitude={lat}&longitude={long}&session={session_token}" 
    # Making the GET request to get the data
    response = requests.get(url)
    #cloud_cover = response.text.get("elevation")
    #print(f"cloud cover {cloud_cover}")
    if response.status_code == 200:
        #print(f"The response is {response.text}")
        return response.text
    else:
        print(f'Error requesting from URL {url}: {response.status_code}')

""" Request Coverage
Generates a png(2D) or netCDF file (3 & 4D) that shows cloud composite at specific resolution
returns data at temporal resolution t0, t0+5min, t0+10min, etc. 
Temporal resolution can be adjusted with lowest resolution 1min.
input: 
            session token: unique session token to be used to retrieve data
            type: Type of data to request, "precipitation-rate" "cloud-composite" "cloud-top-amsl" etc.
output: 
            string containing lots of data, amongst others the cloud cover and surface visibility.
https://hq.meandair.com/api/v1.html#tag/Weather-Coverages/operation/coverage
"""
def requestCoverage(session_token,lat,long, type, bbox, width=800, height = 800, format ="image/png"):
    url1 = f"https://prod.meandair.com/api/v1/coverage?weather={type}&latitude={lat}&longitude={long}&session={session_token}&bbox={long-10},{lat-10},{long+10},{lat+10}&width={width}&height={height}&format={format}&time=now-plus-30m" 
    url2 = f"https://prod.meandair.com/api/v1/coverage?weather={type}&latitude={lat}&longitude={long}&session={session_token}&bbox={long-10},{lat-10},{long+10},{lat+10}&width={width}&height={height}&format={format}&time=now-plus-100m" 
    response1 = requests.get(url1)
    response2 = requests.get(url2)
    print(url2)
    #cloud_cover = response.text.get("elevation")
    #print(f"cloud cover {cloud_cover}")
    if response1.status_code == 200:
        #print(f"The response is {response.text}")
        with open("/home/amaury/Documents/Nowcasting/rotterdam_weather_30.png", "wb") as file:
            file.write(response1.content)
        if response2.status_code == 200:
            with open("/home/amaury/Documents/Nowcasting/rotterdam_weather_180.png", "wb") as file:
                file.write(response2.content)
        else :
            print(f'Error requesting from URL {url2}: {response2.status_code}')
        return response1.text
    else:
        print(f'Error requesting from URL {url1}: {response1.status_code}')

# authorize
token = authorize()

#Request data for Rotterdam
responseStr = requestWeatherTAF(token, 51.95416285, 4.435664924) #Rotterdam Airport

#unpack str response in json format.
response = json.loads(responseStr)

#unpack desired data
cloudData = response["nowcast"]["cloud_cover"]
print(f"Cloud data is {cloudData}")

bbox = [-26.25,24.5,43.7,74.25]
requestCoverage(token, 51.95416285, 4.435664924, "cloud-cover", bbox) 

image_path = "/home/amaury/Documents/Nowcasting/rotterdam_weather_180.png"
image_path_modified = "/home/amaury/Documents/Nowcasting/rotterdam_weather_180_modified.jpeg"
# Open the image file using PIL
image = Image.open(image_path)

# Convert the image to a NumPy array
image_array = np.array(image)

image_array_modified = np.copy(image_array)*2.55
I8 = (((image_array_modified - image_array_modified.min()) / (image_array_modified.max() - image_array_modified.min())) * 255.9).astype(np.uint8)

im = Image.fromarray(I8)
im.save(image_path_modified)

# Print the shape of the image array to verify
print('Image array shape:', image_array.shape)