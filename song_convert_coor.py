class COOR_CONVERTER():

	def convert_ra(self, ra,type_of_ra=24):
		if len(str(ra).split(':')) == 1:
			if len(str(ra).split('.')) == 2 and type_of_ra == 24:
				ra_hours,ra1 = str(ra).split('.')
				ra2 = float(str('0.'+str(ra1))) * 60.0
				ra_minutes, ra3 = str(ra2).split('.')
				ra_seconds = float(str('0.'+str(ra3))) * 60.0
				return "%02i:%02i:%02.3f" % (int(ra_hours),int(ra_minutes),float(ra_seconds))

			elif len(str(ra).split('.')) == 2 and type_of_ra == 360:
				ra = float(ra) / 15.0
				ra_hours,ra1 = str(ra).split('.')
				ra2 = float(str('0.'+str(ra1))) * 60.0
				ra_minutes, ra3 = str(ra2).split('.')
				ra_seconds = float(str('0.'+str(ra3))) * 60.0
				return "%02i:%02i:%02.3f" % (int(ra_hours),int(ra_minutes),float(ra_seconds))


		elif len(str(ra).split(':')) > 1 and type_of_ra == 24:
			if len(str(ra).split(':')) == 2:
				ra_h, ra_m = str(ra).split(':')
				return float(ra_h) + (float(ra_m) / 60.)
				
			elif len(str(ra).split(':')) == 3:				
				ra_h, ra_m, ra_s = str(ra).split(':')
				return float(ra_h) + (float(ra_m) / 60.) + (float(ra_s) / 3600.)

		elif len(str(ra).split(':')) > 1 and type_of_ra == 360:
			if len(str(ra).split(':')) == 2:
				ra_h, ra_m = str(ra).split(':')
				return (float(ra_h) + float(ra_m) / 60.) * 15.
				
			elif len(str(ra).split(':')) == 3:				
				ra_h, ra_m, ra_s = str(ra).split(':')
				return (float(ra_h) + (float(ra_m) / 60.) + (float(ra_s) / 3600.)) * 15.
		else:
			return "The coordinates were not in the format HH:MM:SS, HH.hh, DD:MM:SS or DD.dd"

	def convert_dec(self, dec):
		if len(str(dec).split(':')) == 1:
			if len(str(dec).split('.')) == 2:
				if float(dec) >= -90.0 and float(dec) <= 90.0:
					dec_degrees,dec1 = str(dec).split('.')
					dec2 = float(str('0.'+str(dec1))) * 60.0
					dec_minutes, dec3 = str(dec2).split('.')
					dec_seconds = float(str('0.'+str(dec3))) * 60.0
					return "%02i:%02i:%02.3f" % (int(dec_degrees),int(dec_minutes),float(dec_seconds))


		elif len(str(dec).split(':')) > 1:
			if str(dec[0]) != "-":			
				if "\xe2\x80" not in str(dec):
					if len(str(dec).split(':')) == 2:
						dec_d, dec_m = str(dec).split(':')
						return float(dec_d) + (float(dec_m) / 60.)
				
					elif len(str(dec).split(':')) == 3:				
						dec_d, dec_m, dec_s = str(dec).split(':')
						return float(dec_d) + (float(dec_m) / 60.) + (float(dec_s) / 3600.)

				else:
					if len(str(dec).split(':')) == 2:
						dec_d, dec_m = str(dec).strip("\xe2\x80\x93").split(':')
						return float(dec_d) + (float(dec_m) / 60.)
				
					elif len(str(dec).split(':')) == 3:				
						dec_d, dec_m, dec_s = str(dec).strip("\xe2\x80\x93").split(':')
						return -1.0 *(float(dec_d) + (float(dec_m) / 60.) + (float(dec_s) / 3600.))
			else:
				dec = str(dec).replace("-", "")
				if "\xe2\x80" not in str(dec):
					if len(str(dec).split(':')) == 2:
						dec_d, dec_m = str(dec).split(':')
						return -1.0 * (float(dec_d) + (float(dec_m) / 60.))
				
					elif len(str(dec).split(':')) == 3:				
						dec_d, dec_m, dec_s = str(dec).split(':')
						return -1.0 * (float(dec_d) + (float(dec_m) / 60.) + (float(dec_s) / 3600.))

				else:
					if len(str(dec).split(':')) == 2:
						dec_d, dec_m = str(dec).strip("\xe2\x80\x93").split(':')
						return -1.0 * (float(dec_d) + (float(dec_m) / 60.))
				
					elif len(str(dec).split(':')) == 3:				
						dec_d, dec_m, dec_s = str(dec).strip("\xe2\x80\x93").split(':')
						return -1.0 * (float(dec_d) + (float(dec_m) / 60.) + (float(dec_s) / 3600.))		

		else:
			return "The coordinates were not in the format DD:MM:SS or DD.dd"

	def convert_ra_pm(self, ra_pm, units="mas"):
		if units == "mas":
			ra_pm_modified = (float(ra_pm) / (1000. * 3600. * 15. ))	# Converts from milliarcseconds per year to hours per year 
			
		return ra_pm_modified		

	def convert_dec_pm(self, dec_pm, units="mas"):
		if units == "mas":
			dec_pm_modified = (float(dec_pm) / (1000. * 3600.))	# Converts from milliarcseconds per year to hours per year 
			
		return dec_pm_modified	



