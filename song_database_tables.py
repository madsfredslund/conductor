# Database tables:
import time

tid = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())

tel_dome = {		"tel_ready_state":		0,
			"tel_motion_state":		0,
			"tel_ra":			0,
			"tel_dec":			0,
			"tel_az":			0,
			"tel_zd":			0,
			"tel_alt":			0,
			"tel_error":			0,
			"tel_focus":			0,
			"obj_ra":			0,
			"obj_dec":			0,
			"dome_az":			0,
			"dome_slit_state":		0,
			"dome_flap_state":		0,
			"dome_state":			0,
			"floor_hatch_state":		0,
			"mirror_cover_state":		0,
			"third_mirror":			0,
			"rot2_status":			0,
			"rot2_angle":			0,
			"rot2_field_direct":		0,
			"wavefr_status":		0,
			"cabinet_state":		0,
			"window_az":			0,
			"side_port_1":			0,
			"side_port_2":			0,
			"side_port_3":			0,
			"side_port_4":			0,
			"side_port_5":			0,
			"side_port_6":			0,
			"side_port_7":			0,
			"temp_cabinet":			0,
			"temp_m1":			0,
			"temp_m2":			0,
			"temp_m3":			0,
			"temp_n1":			0,
			"temp_n2":			0,
			"gps_ut":			"'%s'" % tid,
			"gps_st":			"'%s'" % tid,
			"extra_param_1":		0,
			"extra_param_2":		0,
			"extra_param_3":		0,
			"ins_at":			"'%s'" % tid			
}

house_hold = {		"box_id":			0,
			"temperature_1":		0,
			"temperature_2":		0,
			"temperature_3":		0,
			"temperature_4":		0,
			"temperature_5":		0,
			"temperature_6":		0,
			"temperature_7":		0,
			"temperature_8":		0,
			"temperature_9":		0,
			"temperature_10":		0,
			"temperature_11":		0,
			"temperature_12":		0,
			"temperature_13":		0,
			"temperature_14":		0,
			"temperature_15":		0,
			"temperature_16":		0,
			"power_1":			0,
			"power_2":			0,
			"power_3":			0,
			"power_4":			0,
			"power_5":			0,
			"power_6":			0,
			"power_7":			0,
			"power_8":			0,
			"humidity_1":			0,
			"humidity_2":			0,
			"sensor_1":			'off',
			"sensor_2":			'off',
			"sensor_3":			'off',
			"aircon_set_temp":		0,
			"aircon_actual_temp":		0,
			"ins_at":			"'%s'" % tid
}

lucky_cam = {		"cam_no":			0,
			"exp_time":			0,
			"gain_1":			0,
			"gain_2":			0,
			"x_begin":			1,
			"y_begin":			1,
			"x_end":			500,
			"y_end":		        500,
			"z_dim":			1,
			"x_bin":			1,
			"y_bin":			1,
			"shutter":			"'close'",
			"file_name":			"'test.fits'",
			"ins_at":			"'%s'" % tid
}

spectrograph_cam = {	"exp_time":			1,
			"gain":				1,
			"x_begin":			1,
			"y_begin":			1,
			"x_end":			2,
			"y_end":			2,
			"x_bin":			1,
 			"y_bin":			1,
			"file_name":			"'test.fits'",
			"photon_mid_time":		"'%s'" % tid,
			"req_no":			1,
			"param_1":			0,
			"param_2":			0,
			"ins_at":			"'%s'" % tid
}

weather_station = {	"wxt520_temp1":			0,
			"wxt520_temp2":			0,
			"wxt520_humidity":		0,
			"wxt520_pressure":		0,
			"wxt520_rain_int":		0,
			"wxt520_rain_acc":		0,
			"wxt520_rain_dur":		0,
			"wxt520_rain":			0,
			"drd11_rain":			0,
			"wxt520_hail_int":		0,
			"wxt520_hail_acc":		0,
			"wxt520_hail_dur":		0,
			"wxt520_wind_speed":		0,
			"wxt520_wind_direction":	0,
			"wxt520_wind_avg":		0,
			"wxt520_wind_avgdir":		0,
			"bw_cloud_cond":		0,
			"bw_wind_cond":			0,
			"bw_rain_cond":			0,
			"bw_sky_cond":			0,
			"bw_delta_temp":		0,
			"bw_temp_amb":			0,
			"bw_windspeed":			0,
			"bw_wetsensor":			0,
			"bw_rainsensor":		0,
			"bw_humidity":			0,
			"bw_dewp_temp":			0,
			"bw_temp_case":			0,
			"bw_day_cond":			0,
			"bw_day_inten":			0,
			"dust_level":			0,
			"ins_at":			"'%s'" % tid
}

coude_unit = {		"iodine_pos":			1,
			"filter_pos":			1,
			"calib_mirror_pos":		1,
			"mirror_slide":			1,
			"spectrograph_foc":		150000,
			"slit_pos":			1,
			"iodine_temp_set":		1,
			"iodine_temp_read":		1,
			"iodine_heater_on":		0,
			"lamp_halogen_on":		0,
			"lamp_thar_on":			0,
			"lamp_optional_on":		0,
			"ins_at":			"'%s'" % tid
}

nasmyth_unit = {	"image_derotator_angle":	0,
			"image_derotator_orientation":	0,
			"image_derotator_tracking":	0,
			"adc_angle_1":			0,
			"adc_angle_2":			0,
			"adc_tracking":			0,
			"filter_wheel_red_pos":		0,
			"filter_wheel_vis_pos":		0,
			"beam_selector":		0,
			"ins_at":			"'%s'" % tid			
}

guide_cam = {		"s_guiding":			"'False'",
			"s_paused":			"'False'",
			"s_act_pos_x":			1,
			"s_act_pos_y":			1,
			"s_act_in_lim":			"'False'",
			"s_pointing_enabl":		"'False'",
			"s_focus_enabl":		"'False'",
			"s_pointing_offs_x":		1,
			"s_pointing_offs_y":		1,
			"s_focus_offs":			1,
			"s_slow_sig":			"'False'",
			"s_fast_sig":			"'False'",
			"s_exp_integr":			"'False'",
			"s_exp_leng":			1,
			"s_exp_mid":			1,
			"s_exp_rate":			1,
			"s_exp_mask_mid ":		1,
			"s_exp_mask_rate":		1,
			"s_exp_saturated":		"'False'",
			"s_x_dim":			1,
			"s_y_dim":			1,
			"s_x_beg":			1,
			"s_y_beg":			1,
			"s_x_bin":			1,
			"s_y_bin":			1,
			"s_exp_time":			1,
			"s_filename":			"'test_s.fits'",
			"s_ins_at":			"'%s'" % tid,
			"p_guiding":			"'False'",
			"p_paused":			"'False'",
			"p_act_pos_x":			1,
			"p_act_pos_y":			1,
			"p_act_in_lim":			"'False'",
			"p_guide_sig_ok":		"'False'",
			"p_x_dim":			1,
			"p_y_dim":			1,
			"p_x_beg":			1,
			"p_y_beg":			1,
			"p_x_bin":			1,
			"p_y_bin":			1,
			"p_exp_time":			1,
			"p_filename":			"'test_p.fits'",
			"p_ins_at":			"'%s'" % tid,
			"n_guiding":			"'False'",
			"n_paused":			"'False'",
			"n_pointing_enabl":		"'False'",
			"n_focus_enabl":		"'False'",
			"n_pointing_offs_x":		1,
			"n_pointing_offs_y":		1,
			"n_guide_sig_ok":		"'False'",
			"n_focus_offs":			1,
			"n_x_dim":			1,
			"n_y_dim":			1,
			"n_x_beg":			1,
			"n_y_beg":			1,
			"n_x_bin":			1,
			"n_y_bin":			1,
			"n_exp_time":			1,
			"n_filename":			"'test_s.fits'",
			"n_ins_at":			"'%s'" % tid,
			"ins_at":			"'%s'" % tid
			
}

web_cam = {		"cam_no":			0,
			"x_dim":			0,
			"y_dim":			0,
			"file_name":			"'test_s.fits'",
			"ins_at":			"'%s'" % tid			
}

star_tracker = {	"exp_time":			100,
			"x_dim":			500,
			"y_dim":			500,
			"right_ascension":		0,
			"declination":			0,
			"file_name":			"'test_s.fits'",
			"ins_at":			"'%s'" % tid
}

system_component = {	"component_name":		0,
			"dsc":				0			
}

heartbeat = {		"heartbeat_id":			1,
			"wall_clock":			"'%s'" % tid
}

system_status = {	"system_component_id":		1,
			"heartbeat_id":			1,
			"power_id":			1,
			"power_on":			0,
			"cur_amps":			0,
			"over_all_obs_state":		0
}

maintenance = {		"maintenance_id":		1,
			"bias_mean":			0,
			"bias_rms":           		0,
			"bias_std":	         	0,
			"thar_xoff1":         		0,
			"thar_yoff1":         		0,
			"thar_xoff2":			0,
			"thar_yoff2":  			0,        
			"thar_line_width_1": 		0, 
			"thar_line_width_2":		0,  
			"spec_focus":			0,          
			"spec_resolution": 		0,    
			"blaze_peak_level":		0,     
			"extra_param_1":		0,	 
			"extra_param_2":		0,	
			"extra_param_3":		0,	 
			"extra_param_4":		0,	
			"extra_param_5":		0,	 
			"extra_param_6":		0,	
			"extra_param_7":		0,	
			"extra_param_8":		0,	
			"extra_param_9":		0,	 
			"extra_param_10": 		0,
			"extra_value_1":		0,	
			"extra_value_2":		0,	
			"extra_value_3":		0,	 
			"extra_value_4":		0,	 
			"extra_value_5":		0,	
			"extra_value_6":		0,	
			"extra_value_7":		0,	 
			"extra_value_8":		0,	 
			"extra_value_9":		0,	
			"extra_value_10":		0,	 
			"ins_at": 			"'%s'" % tid  
}


def return_list(table, what):
	if table == "tel_dome" and what == "names":
		cString = ""
		joinVar = "("
		for c, v in tel_dome.iteritems():
			cString = joinVar.join((cString, c))
			joinVar = ","
		    
		cString = "".join((cString, ")"))		
		return cString
	if table == "tel_dome" and what == "values":
		vString = ""
		joinVar = "("
		for c, v in tel_dome.iteritems():
		    vString = joinVar.join((vString, str(v)))
		    joinVar = ","
		    
		vString = "".join((vString, ")"))
		return vString
	if table == "house_hold" and what == "names":
		cString = ""
		joinVar = "("
		for c, v in house_hold.iteritems():
			cString = joinVar.join((cString, c))
			joinVar = ","
		    
		cString = "".join((cString, ")"))		
		return cString
	if table == "house_hold" and what == "values":
		vString = ""
		joinVar = "("
		for c, v in house_hold.iteritems():
		    vString = joinVar.join((vString, str(v)))
		    joinVar = ","
		    
		vString = "".join((vString, ")"))
		return vString
	if table == "lucky_cam" and what == "names":
		cString = ""
		joinVar = "("
		for c, v in lucky_cam.iteritems():
			cString = joinVar.join((cString, c))
			joinVar = ","
		    
		cString = "".join((cString, ")"))		
		return cString
	if table == "lucky_cam" and what == "values":
		vString = ""
		joinVar = "("
		for c, v in lucky_cam.iteritems():
		    vString = joinVar.join((vString, str(v)))
		    joinVar = ","
		    
		vString = "".join((vString, ")"))
		return vString
	if table == "spectrograph_cam" and what == "names":
		cString = ""
		joinVar = "("
		for c, v in spectrograph_cam.iteritems():
			cString = joinVar.join((cString, c))
			joinVar = ","
		    
		cString = "".join((cString, ")"))		
		return cString
	if table == "spectrograph_cam" and what == "values":
		list_of_values = []
		items = spectrograph_cam.items()
		for i,j in items:	
			list_of_values.append(j)		
		return tuple(list_of_values)
	if table == "weather_station" and what == "names":
		cString = ""
		joinVar = "("
		for c, v in weather_station.iteritems():
			cString = joinVar.join((cString, c))
			joinVar = ","
		    
		cString = "".join((cString, ")"))		
		return cString
	if table == "weather_station" and what == "values":
		vString = ""
		joinVar = "("
		for c, v in weather_station.iteritems():
		    vString = joinVar.join((vString, str(v)))
		    joinVar = ","
		    
		vString = "".join((vString, ")"))
		return vString	
	if table == "spectrograph" and what == "names":
		cString = ""
		joinVar = "("
		for c, v in spectrograph.iteritems():
			cString = joinVar.join((cString, c))
			joinVar = ","
		    
		cString = "".join((cString, ")"))		
		return cString
	if table == "spectrograph" and what == "values":
		vString = ""
		joinVar = "("
		for c, v in spectrograph.iteritems():
		    vString = joinVar.join((vString, str(v)))
		    joinVar = ","
		    
		vString = "".join((vString, ")"))
		return vString
	if table == "coude_unit" and what == "names":
		cString = ""
		joinVar = "("
		for c, v in coude_unit.iteritems():
			cString = joinVar.join((cString, c))
			joinVar = ","
		    
		cString = "".join((cString, ")"))		
		return cString
	if table == "coude_unit" and what == "values":
		vString = ""
		joinVar = "("
		for c, v in coude_unit.iteritems():
		    vString = joinVar.join((vString, str(v)))
		    joinVar = ","
		    
		vString = "".join((vString, ")"))
		return vString
	if table == "nasmyth_unit" and what == "names":
		cString = ""
		joinVar = "("
		for c, v in nasmyth_unit.iteritems():
			cString = joinVar.join((cString, c))
			joinVar = ","
		    
		cString = "".join((cString, ")"))		
		return cString
	if table == "nasmyth_unit" and what == "values":
		vString = ""
		joinVar = "("
		for c, v in nasmyth_unit.iteritems():
		    vString = joinVar.join((vString, str(v)))
		    joinVar = ","
		    
		vString = "".join((vString, ")"))
		return vString
	if table == "guide_cam" and what == "names":
		cString = ""
		joinVar = "("
		for c, v in guide_cam.iteritems():
			cString = joinVar.join((cString, c))
			joinVar = ","
		    
		cString = "".join((cString, ")"))		
		return cString
	if table == "guide_cam" and what == "values":
		vString = ""
		joinVar = "("
		for c, v in guide_cam.iteritems():
		    vString = joinVar.join((vString, str(v)))
		    joinVar = ","
		    
		vString = "".join((vString, ")"))
		return vString
	if table == "web_cam" and what == "names":
		cString = ""
		joinVar = "("
		for c, v in web_cam.iteritems():
			cString = joinVar.join((cString, c))
			joinVar = ","
		    
		cString = "".join((cString, ")"))		
		return cString
	if table == "web_cam" and what == "values":
		vString = ""
		joinVar = "("
		for c, v in web_cam.iteritems():
		    vString = joinVar.join((vString, str(v)))
		    joinVar = ","
		    
		vString = "".join((vString, ")"))
		return vString
	if table == "star_tracker" and what == "names":
		cString = ""
		joinVar = "("
		for c, v in star_tracker.iteritems():
			cString = joinVar.join((cString, c))
			joinVar = ","
		    
		cString = "".join((cString, ")"))		
		return cString
	if table == "star_tracker" and what == "values":
		vString = ""
		joinVar = "("
		for c, v in star_tracker.iteritems():
		    vString = joinVar.join((vString, str(v)))
		    joinVar = ","
		    
		vString = "".join((vString, ")"))
		return vString
	if table == "system_component" and what == "names":
		cString = ""
		joinVar = "("
		for c, v in system_component.iteritems():
			cString = joinVar.join((cString, c))
			joinVar = ","
		    
		cString = "".join((cString, ")"))		
		return cString
	if table == "system_component" and what == "values":
		vString = ""
		joinVar = "("
		for c, v in system_component.iteritems():
		    vString = joinVar.join((vString, str(v)))
		    joinVar = ","
		    
		vString = "".join((vString, ")"))
		return vString
	if table == "heartbeat" and what == "names":
		cString = ""
		joinVar = "("
		for c, v in heartbeat.iteritems():
			cString = joinVar.join((cString, c))
			joinVar = ","
		    
		cString = "".join((cString, ")"))		
		return cString
	if table == "heartbeat" and what == "values":
		vString = ""
		joinVar = "("
		for c, v in heartbeat.iteritems():
		    vString = joinVar.join((vString, str(v)))
		    joinVar = ","
		    
		vString = "".join((vString, ")"))
		return vString
	if table == "system_status" and what == "names":
		cString = ""
		joinVar = "("
		for c, v in system_status.iteritems():
			cString = joinVar.join((cString, c))
			joinVar = ","
		    
		cString = "".join((cString, ")"))		
		return cString
	if table == "system_status" and what == "values":
		vString = ""
		joinVar = "("
		for c, v in system_status.iteritems():
		    vString = joinVar.join((vString, str(v)))
		    joinVar = ","
		    
		vString = "".join((vString, ")"))
		return vString
	if table == "maintenance" and what == "names":
		cString = ""
		joinVar = "("
		for c, v in maintenance.iteritems():
			cString = joinVar.join((cString, c))
			joinVar = ","
		    
		cString = "".join((cString, ")"))		
		return cString
	if table == "maintenance" and what == "values":
		vString = ""
		joinVar = "("
		for c, v in maintenance.iteritems():
		    vString = joinVar.join((vString, str(v)))
		    joinVar = ","
		    
		vString = "".join((vString, ")"))
		return vString





