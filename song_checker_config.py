# Configuration file for the checker. 

# Boundaries for the weather checks:
max_temp = 35.0 # Maximum outdoor temperature in centigrade permitted.
min_temp = -10.0 # Minimum outdoor temperature in centigrade permitted.
max_hum = 75.0 # Maximum outdoor humidity in percentage permitted.
max_w_speed = 15.0 # Maximum outdoor windspeed in meters per second permitted.
max_w_speed_into = 10.0 # Maximum outdoor windspeed in meters per second permitted to blow into the dome.
max_w_speed_flap = 10.0 # The maximum wind speed allowed when opening the dome flap

insert_margin = 20 # Angle in degrees which is a margin for the selector when wind is too high to observe into
angle_into = 90.0 # If the wind is blowing into the dome opening then only the small windspeed is allowed. 
clouds = [3] # Values: 0 = unknown, 1 = clear, 2 = cloudy, 3 = very cloudy, Numbers entered are not allowed.
delay_time = 20 # Delay time for actions after a triggering event in minutes.
telescope_delay_time = 60 # Delay time for actions after a triggering event in minutes.
search_time = 5 # Time in the past to check for more then one triggering event. More then 3 rain events must occur in the last 5 minutes to trigger. 
max_rain_events = 3 
dust_limit = 0.015 # The limit when the dust level is too high (0.015)
dust_limit_daytime = 0.003 # The limit when the dust level is too high during daytime (0.003)
open_time_if_dust = 0.0	# Time before sunset when telescope is allowed to open when there is some dust.
downtime = 120 # maximum downtime of database permitted in seconds.

max_wind_side_ports = 17.0 # Maximum outdoor windspeed in meters per second permitted to blow into the side ports.

wind_blow_events = 5 	# Maximum allowed number of wind gusts above max_wind_side_ports in delay_time. 
side_ports_angle = 60.0 # The angle at which the wind is not allowed to ecceed max_wind_side_ports value # 60.0 is standard
side_port_events = 3 	# Maximum allowed number of rain and humidity events in delay_time.
min_wind_side_ports = 7	# If wind speed is less than this the side ports should not open and cooling unit should run
day_search_time = 40	# Check if wind speed is high or low for sideports vs. cooler.

#### Which rain detector(s) to use:
rain_detector = ["wxt520", "bw"]	# If name in list then it is used: ["drd11", "bw", "wxt520"]

# Site based parameters:
#song_site = "tenerife"	# 1 = tenerife, 
# Database values:
#db_host = "192.168.66.65"
#db_user = "postgres"
#db_password = ""
#db_name = "db_tenerife"


# Maximum temperatures in container, dome and spec box.
dome_temp = 40			# Maximum allowed temperature inside the dome before warnings are sendt out
container_temp = 35		# Maximum allowed temperature inside the container before warnings are sendt out
spec_box_temp_max = 30.5	# Maximum allowed temperature inside the spectrograph bex before warnings are sendt out
spec_box_temp_min = 28.5	# Maximum allowed temperature inside the spectrograph bex before warnings are sendt out


o_star_dir = "/home/obs/CONFIG_FILES/o-stars/"

#Coordinates of the site in use.
#lat_obs = "28.2983" # Teide: 28.2983
#lon_obs = "-16.5094" # Teide: -16.5094
#elev_obs = 2400 # Teide: 2400

# Object on the sky:
#object_min_alt = 16.0 # Minimum altitude of an object that can be observed.

