######################################################################################################
### This file contains the values and parameters used by many of the scripts, daemons and so on...####
######################################################################################################

######################################################################################################
################			TELESCOPE SETTINGS			######################
######################################################################################################
telescope_min_altitude = 16.0	# Minimum altitude of the telescope at all times.
tel_dist_to_sun = 20.0		# Minimum distance from the pointing direction to the Sun
tel_dist_to_moon = 5.0		# Minimum distance from the pointing direction to the Moon
open_time_tel = 2.0		# When less than 2.0 hour to sun set the dome is allowed to be opened.
tel_park_az = 90.0		# Pointing towards east
tel_park_alt = 75.0		# Pointing to make air from cooling unit go to M1
dome_tel_off = 10.0		# Maximum offset between telescope azimuth and dome azimuth direction
max_alt_auto = 82.0		# Close to zenith
seeing_limit_s5 = 1.7		# For faint objects
seeing_limit_s6 = 1.5		# For faint objects
seeing_limit_s8 = 1.2		# For faint objects
vmag_seeing_limit = 9.5		# From vmag 7.5 the seeing should be good when observing.

######################################################################################################
################			SIDE PORTS SETTINGS			######################
######################################################################################################
open_time_side_port = 20.0	# When less than X hours to sun set the sideport can be opened.
close_sun_alt_side_port = 1.0	# The altitude of the Sun when side port should close at sun rise

######################################################################################################
################			DOME COOLING SETTINGS			######################
######################################################################################################
cooling_temp = 15.0		# Temperature in degrees which the cooling unit will be set to when turned on.

######################################################################################################
################			SKYCAM SETTINGS				######################
######################################################################################################
start_skycam_movie = 1		# 1 = yes, 0 = no
skycam_start_sun_alt = -9.0	# Altitude of the Sun when skycam movie should start.
skycam_movie_exptime = 20.0	# exposure time for each image for the movie.
skycam_movie_delay = 1		# time between movie exposures

######################################################################################################
################			GENERAL SETTINGS			######################
######################################################################################################
obs_sun_alt = -6		# when the Sun is under this angle from the horizon we can observe
do_not_observe = ["1/1", "2/1", "24/12", "25/12"]

### Message system.. who should receive messages:
notify_email_who = ["mads", "frank", "jens", "ditte", "vichi", "eric", "rene"]
notify_email_2 = ["mads", "frank", "jens", "ditte", "vichi", "rene"]
notify_sms_who = ["Mads", "Jens", "Ditte", "Vichi", "Rene"]
wakeup_sms_who = ["Mads", "Jens", "Ditte", "Vichi", "Frank", "Rene"]


# Site based parameters:
song_site = "tenerife"	# 1 = tenerife,
#Coordinates of the site in use.
lat_obs = "28.2983" 	# Teide: 28.2983
lon_obs = "-16.5094" 	# Teide: -16.5094
long_obs = "-16.5094" 	# Teide: -16.5094
elev_obs = 2400 	# Teide: 2400


#### Database things:
data_db = 'db_tenerife'				# The database name of the Tenerife data
or_db = 'db_song'				# The OR database on all nodes
db_host = '192.168.66.65'			# 'site02'	The local db host in Tenerife 
db_c_host = '192.168.64.65'			# 'central'	The central db host in aarhus
db_user = 'postgres'				# Default username of a postgres database
db_password = ''				# Default password of a postgres database
#[OR]
or_table = 'obs_request_1'			# The Spectrograph observing mode table name
or_status_table = 'obs_request_status_1'	# The status table of the spectrograph observing mode

soda_db = 'db_aadc'
soda_host = 'trinity.phys.au.dk'
soda_user = 'pipeline_conductor'
soda_pw = ''

# Spectrograph focus value file:
focus_val_file = "/home/obs/logs/focus_val_file.txt"

######################################################################################################
################			CALIBRATION SETTINGS			######################
######################################################################################################
# focus_guess = 2.0 + 0.04 * float(gettsi.get_auxiliary_ttelescope(sender="monitor")) + 5.0 / float(gettsi.get_position_horizontal_alt(sender="monitor"))
#tel_focus_function_values = [2.2, 0.04, 5.0]
use_temp_from = "m3" # ["m1", "m2", "m3", "tt", "out"]
tel_focus_function_values = [2.19, 0.025, 4.0, 0.01]
old_tel_focus_function_values = [2.2, 0.03, 3.0]

######################################################################################################
################			CALIBRATION SETTINGS			######################
######################################################################################################
do_morning_calib = 1	# 1 = yes
do_evening_calib = 1	# 1 = yes
start_pipeline_morning = "yes"

thar_exptime = 1.5
halo_exptime = 2.0


######################################################################################################
################			IODINE HEATER SETTINGS			######################
######################################################################################################
i2_set_temp = 65	# Iodine cell will be heated to this temperature

######################################################################################################
################			HEARTBEAT TABLE				######################
######################################################################################################
pst_id = 1
i2_write_to_db_id = 2
get_dust_id = 3
monitor_id = 4
weather_station = 5	# Running in c, and not using this table...
obs_notify_id = 6
guide_ims_to_srf_id = 7
tcs_comm_id = 8
scheduler_id = 9
spec_ccd_id = 10
daily_calib_id = 11
skycam_id = 12
conductor_id = 13


