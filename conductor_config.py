pidfile='/tmp/conductor.pid'
outstream='/home/madsfa/conductor.log'
outstream_old='/home/madsfa/conductor.old_log'
check_time = 10.0	#Checks for new ORs every 10th of a seconds.
daytime_sleep = 600

project_critical_type = ["rv-standard", "periodical", "filler", "backup"]	# ["rv-standard", "timecritical", "periodical", "filler", "backup"]
#project_critical_type = ["backup"]

insert_ors = "yes"
update_or_status = "yes"
update_nightly = "yes"
insert_solar_ors = "yes"
use_only_soda = "yes"
insert_solar_synopic = "yes"

solar_times = [-4, -2, 0, 2, 4]
#solar_times = [0]

check_for_timecritical = "yes"
insert_timecritical = "yes"

### Check observed ORs within:
check_within_days = 1

##
insert_time_before = 120	# Allow to insert ORs 2 minutes (120s) before gap start

wind_alt_prime_limit = 25	#Primary asteroseismic target
wind_alt_other_limit = 30
wind_delay = 20

# Site based parameters:
song_site = "tenerife"	# 1 = tenerife,
#Coordinates of the site in use.
lat_obs = "28.2983" 	# Teide: 28.2983
lon_obs = "-16.5094" 	# Teide: -16.5094
long_obs = "-16.5094" 	# Teide: -16.5094
elev_obs = 2400 	# Teide: 2400

obs_sun_alt = -6
telescope_min_altitude = 16.0	# Minimum altitude of the telescope at all times.
tel_dist_to_moon = 5.0		# Minimum distance from the pointing direction to the Moon

max_alt_auto = 82.0		# Close to zenith
#seeing_limit_s5 = 1.7		# For faint objects
#seeing_limit_s6 = 1.5		# For faint objects
#seeing_limit_s8 = 1.2		# For faint objects
#vmag_seeing_limit = 9.5		# From vmag the seeing should be good when observing.
telescope_slewtime = 60
thar_overhead = 120


readoutsec = 4
readoutms = 210


