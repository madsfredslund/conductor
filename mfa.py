#!/usr/bin/python

# This module will make sure that numerical calculations will be performed with double precision. 
# mean
# std
# rms
# sum
# ...

import numpy
from scipy.optimize import curve_fit
from scipy.interpolate import UnivariateSpline
from scipy.optimize import leastsq
import numpy as np

def mean(array):
	# Returns the mean value of an array with double precision
	return numpy.mean(array, dtype=numpy.float64)

def std(array):
	# Returns the standard deviation of an array with double precision
	return numpy.std(array, dtype=numpy.float64)

def rms(array):
	# Returns the Root-Mean-Square value of an array with double precision
	return numpy.sqrt(numpy.mean(array**2, dtype=numpy.float64))

def sum_total(array):
	# Returns the sum of an array with double precision
	return numpy.sum(array, dtype=numpy.float64)

def fit_with_gauss(xlist,ylist,coeffi=""):
#######################################
	def gauss(x, *p):
	    A, mu, sigma = p
	    return A*numpy.exp(-(x-mu)**2/(2.*sigma**2))

	if coeffi != "":
		p0 = coeffi
	else:
		p0 = [1., 0., 1.]

	coeff, var_matrix = curve_fit(gauss, xlist, ylist, p0=p0)
	new_xlist = [float(i)/100. for i in range(len(ylist)*100)]
	new_ylist = gauss(new_xlist, *coeff)

#######################################
	return new_xlist, new_ylist, coeff[1], coeff[0]

def fit_with_2d_gauss(xlist,ylist,coeffi=""):
#######################################
	def gauss(x, *p):
	    A, mu, sigma = p
	    return A*numpy.exp(-(x-mu)**2/(2.*sigma**2))

	if coeffi != "":
		p0 = coeffi
	else:
		p0 = [1., 0., 1.]

	coeff, var_matrix = curve_fit(gauss, xlist, ylist, p0=p0)
	new_xlist = [float(i)/100. for i in range(len(ylist)*100)]
	new_ylist = gauss(new_xlist, *coeff)

#######################################
	return new_xlist, new_ylist, coeff[1], coeff[0], coeff[2]

def fwhm(xlist,ylist):
	spline = UnivariateSpline(xlist, ylist-numpy.max(ylist)/2., s=0)
	r1, r2 = spline.roots() # find the roots
	fwhm_value = r2-r1
	return fwhm_value

def findShift(im0, im1):
	"""
	    This method is based on fft method of registering images.
	"""
	IM0 = numpy.fft.fft2(im0)
	IM1 = numpy.fft.fft2(im1)

	numer = IM0*numpy.conj(IM1)
	denom = numpy.abs(IM0*IM1)

	#pulse_im = numpy.fft.ifft2(numer/denom)
	pulse_im = numpy.fft.ifft2(numer)
	mag = numpy.abs(pulse_im)
	x, y = numpy.where(mag == mag.max())

        x = numpy.array(x.tolist())   	# if images are read only
	y = numpy.array(y.tolist())

	X, Y = im0.shape

	coeffi = [float(mag[x,y] / numpy.max(mag[x,:][0])), float(y), 1.0]
	new_x1, new_y1, x_max, bla = fit_with_gauss(range(len(mag[x,:][0])), mag[x,:][0], coeffi)	# LINE 1 ( Worst )

	coeffi = [float(mag[x,y] / numpy.max(numpy.transpose(mag[:,y])[0])), float(x), 1.0]
	new_x2, new_y2, y_max, bla = fit_with_gauss(range(len(mag[:,y])), numpy.transpose(mag[:,y])[0], coeffi)	# LINE 2 ( Best )

	if x_max > X/2.:
		x_max -= X
	if y_max > Y/2.:
		y_max -= Y

	return x_max, y_max

def fit_gauss_circular(xy, data):
	"""
	---------------------
	Purpose
	Fitting a star with a 2D circular gaussian PSF.
	---------------------
	Inputs
	* xy (list) = list with the form [x,y] where x and y are the integer positions in the complete image of the first pixel (the one with x=0 and y=0) of the small subimage that is used for fitting.
	* data (2D Numpy array) = small subimage, obtained from the full FITS image by slicing. It must contain a single object : the star to be fitted, placed approximately at the center.
	---------------------
	Output (list) = list with 6 elements, in the form [maxi, floor, height, mean_x, mean_y, fwhm]. The list elements are respectively:
	- maxi is the value of the star maximum signal,
	- floor is the level of the sky background (fit result),
	- height is the PSF amplitude (fit result),
	- mean_x and mean_y are the star centroid x and y positions, on the full image (fit results), 
	- fwhm is the gaussian PSF full width half maximum (fit result) in pixels
	---------------------
	"""
	
	#find starting values
	maxi = data.max()
	floor = numpy.ma.median(data.flatten())
	height = maxi - floor
	if height==0.0:				#if star is saturated it could be that median value is 32767 or 65535 --> height=0
		floor = numpy.mean(data.flatten())
		height = maxi - floor

	mean_x = (numpy.shape(data)[0]-1)/2
	mean_y = (numpy.shape(data)[1]-1)/2

	fwhm = numpy.sqrt(numpy.sum((data>floor+height/2.).flatten()))
	
	#---------------------------------------------------------------------------------
	sig = fwhm / (2.*numpy.sqrt(2.*numpy.log(2.)))
	width = 0.5/numpy.square(sig)
	
	p0 = floor, height, mean_x, mean_y, width

	#---------------------------------------------------------------------------------
	#fitting gaussian
	def gauss(floor, height, mean_x, mean_y, width):		
		return lambda x,y: floor + height*numpy.exp(-numpy.abs(width)*((x-mean_x)**2+(y-mean_y)**2))

	def err(p,data):
		return numpy.ravel(gauss(*p)(*numpy.indices(data.shape))-data)
	
	p = leastsq(err, p0, args=(data), maxfev=1000)
	p = p[0]
	
	#---------------------------------------------------------------------------------
	#formatting results
	floor = p[0]
	height = p[1]
	mean_x = p[2] + xy[0]
	mean_y = p[3] + xy[1]

	sig = numpy.sqrt(0.5/numpy.abs(p[4]))
	fwhm = sig * (2.*numpy.sqrt(2.*numpy.log(2.)))	
	
	output = [maxi, floor, height, mean_x, mean_y, fwhm]
	return output

def cntrd(img, x, y,
          fwhm, verbose = True, 
          debug = False, 
          extendbox = False, 
          keepcenter = False):
    """Compute the centroid of a star using a derivative search 
    (adapted for IDL from DAOPHOT, then translated from IDL to Python).

    CNTRD uses an early DAOPHOT "FIND" centroid algorithm by locating the 
    position where the X and Y derivatives go to zero.   This is usually a 
    more "robust"  determination than a "center of mass" or fitting a 2d 
    Gaussian  if the wings in one direction are affected by the presence
    of a neighboring star.

    xcen,ycen = cntrd.cntrd(img, x, y, fwhm)
    
    REQUIRED INPUTS:
         img  - Two dimensional image array
         x,y  - Scalar or vector integers giving approximate integer stellar 
                 center
         fwhm - floating scalar; Centroid is computed using a box of half
                 width equal to 1.5 sigma = 0.637* fwhm.

    OPTIONAL KEYWORD INPUTS:
         verbose -    Default = True.  If set, CNTRD prints an error message if it 
                       is unable to compute the centroid.
         debug -      If this keyword is set, then CNTRD will display the subarray
                       it is using to compute the centroid.
         extendbox -  {non-negative positive integer}.   CNTRD searches a box with
                       a half width equal to 1.5 sigma  = 0.637* FWHM to find the
                       maximum pixel.    To search a larger area, set extendbox to
                       the number of pixels to enlarge the half-width of the box.
                       Default is 0; prior to June 2004, the default was extendbox = 3
                       keepcenter - By default, CNTRD finds the maximum pixel in a box
                       centered on the input X,Y coordinates, and then extracts a new
                       box about this maximum pixel.  Set the keepcenter keyword
                       to skip then step of finding the maximum pixel, and instead use
                       a box centered on the input X,Y coordinates.

    RETURNS:
         xcen - the computed X centroid position, same number of points as X
         ycen - computed Y centroid position, same number of points as Y, 
                 floating point
    
         Values for xcen and ycen will not be computed if the computed
         centroid falls outside of the box, or if the computed derivatives
         are non-decreasing.   If the centroid cannot be computed, then a 
         message is displayed and xcen and ycen are set to -1.
    
    PROCEDURE:
         Maximum pixel within distance from input pixel X, Y  determined
         from FHWM is found and used as the center of a square, within
         which the centroid is computed as the value (XCEN,YCEN) at which
         the derivatives of the partial sums of the input image over (y,x)
         with respect to (x,y) = 0.  In order to minimize contamination from
         neighboring stars stars, a weighting factor W is defined as unity in
         center, 0.5 at end, and linear in between
    
    RESTRICTIONS:
         (1) Does not recognize (bad) pixels.   Use the procedure GCNTRD.PRO
              in this situation.
         (2) DAOPHOT now uses a newer algorithm (implemented in GCNTRD.PRO) in
              which centroids are determined by fitting 1-d Gaussians to the
              marginal distributions in the X and Y directions.
         (3) The default behavior of CNTRD changed in June 2004 (from EXTENDBOX=3
              to EXTENDBOX = 0).
         (4) Stone (1989, AJ, 97, 1227) concludes that the derivative search
              algorithm in CNTRD is not as effective (though faster) as a
              Gaussian fit (used in GCNTRD.PRO).
    
    MODIFICATION HISTORY:
         Written following algorithm used by P. Stetson in DAOPHOT      J. K. Hill, S.A.S.C.   2/25/86
         Allowed input vectors                                          G. Hennessy            April,  1992
         Fixed to prevent wrong answer if floating pt. X & Y supplied   W. Landsman            March, 1993 
         Convert byte, integer subimages to float                       W. Landsman            May, 1995
         Converted to IDL V5.0                                          W. Landsman            September, 1997
         Better checking of edge of frame                               David Hogg             October, 2000
         Avoid integer wraparound for unsigned arrays                   W.Landsman             January, 2001
         Handle case where more than 1 pixel has maximum value          W.L.                   July, 2002
         Added /KEEPCENTER, EXTENDBOX (with default = 0) keywords       WL                     June, 2004
         Some errrors were returning X,Y = NaN rather than -1,-1        WL                     Aug, 2010
         Converted to Python                                            D. Jones               January, 2014
    """

    
    sz_image = np.shape(img)

    xsize = sz_image[1]
    ysize = sz_image[0]
    # dtype = sz_image[3]              ;Datatype

    #   Compute size of box needed to compute centroid

    if not extendbox: extendbox = 0
    nhalf =  int(0.637*fwhm)  
    if nhalf < 2: nhalf = 2
    nbox = 2*nhalf+1             #Width of box to be used to compute centroid
    nhalfbig = nhalf + extendbox
    nbig = nbox + extendbox*2        #Extend box 3 pixels on each side to search for max pixel value
    if type(x) == np.float or type(x) == np.int: npts = 1
    else: npts = len(x) 
    if npts == 1: xcen = float(x) ; ycen = float(y)
    else: xcen = x.astype(float) ; ycen = y.astype(float)
    ix = np.round( x )          #Central X pixel        ;Added 3/93
    iy = np.round( y )          #Central Y pixel
    
    if npts == 1: x,y,ix,iy,xcen,ycen = [x],[y],[ix],[iy],[xcen],[ycen]
    for i in range(npts):        #Loop over X,Y vector
        
        pos = str(x[i]) + ' ' + str(y[i])
        
        if not keepcenter:
            if ( (ix[i] < nhalfbig) or ((ix[i] + nhalfbig) > xsize-1) or \
                     (iy[i] < nhalfbig) or ((iy[i] + nhalfbig) > ysize-1) ):
                if verbose:
                    print('Position '+ pos + ' too near edge of image')
                    xcen[i] = -1   ; ycen[i] = -1
                    continue
            
            bigbox = img[int(iy[i]-nhalfbig) : int(iy[i]+nhalfbig+1), int(ix[i]-nhalfbig) : int(ix[i]+nhalfbig+1)]

            #  Locate maximum pixel in 'NBIG' sized subimage 
            goodrow = np.where(bigbox == bigbox)
            mx = np.max( bigbox[goodrow])     #Maximum pixel value in BIGBOX
            mx_pos = np.where(bigbox.reshape(np.shape(bigbox)[0]*np.shape(bigbox)[1]) == mx)[0] #How many pixels have maximum value?
            Nmax = len(mx_pos)
            idx = mx_pos % nbig          #X coordinate of Max pixel
            idy = mx_pos / nbig            #Y coordinate of Max pixel
            if Nmax > 1:                 #More than 1 pixel at maximum?
                idx = np.round(np.sum(idx)/Nmax)
                idy = np.round(np.sum(idy)/Nmax)
            else:
                idx = idx[0]
                idy = idy[0]

            xmax = ix[i] - (nhalf+extendbox) + idx  #X coordinate in original image array
            ymax = iy[i] - (nhalf+extendbox) + idy  #Y coordinate in original image array
        else:
            xmax = ix[i]
            ymax = iy[i]

#; ---------------------------------------------------------------------
#; check *new* center location for range
#; added by Hogg

        if ( (xmax < nhalf) or ((xmax + nhalf) > xsize-1) or \
                 (ymax < nhalf) or ((ymax + nhalf) > ysize-1) ):
            if verbose:
                print('Position '+ pos + ' moved too near edge of image')
                xcen[i] = -1 ; ycen[i] = -1
                continue
#; ---------------------------------------------------------------------
#
#;  Extract smaller 'STRBOX' sized subimage centered on maximum pixel 

        strbox = img[int(ymax-nhalf) : int(ymax+nhalf+1), int(xmax-nhalf) : int(xmax+nhalf+1)]
# if (dtype NE 4) and (dtype NE 5) then strbox = float(strbox)

        if debug:
            print('Subarray used to compute centroid:')
            print(strbox)

        ir = (nhalf-1)
        if ir < 1: ir = 1
        dd = np.arange(nbox-1).astype(int) + 0.5 - nhalf
    # Weighting factor W unity in center, 0.5 at end, and linear in between 
        w = 1. - 0.5*(np.abs(dd)-0.5)/(nhalf-0.5) 
        sumc   = np.sum(w)

    #; Find X centroid
        deriv = np.roll(strbox,-1,axis=1) - strbox    #;Shift in X & subtract to get derivative
        deriv = deriv[nhalf-ir:nhalf+ir+1,0:nbox-1] #;Don't want edges of the array
        deriv = np.sum( deriv, 0 )                    #    ;Sum X derivatives over Y direction
        sumd   = np.sum( w*deriv )
        sumxd  = np.sum( w*dd*deriv )
        sumxsq = np.sum( w*dd**2 )

        if sumxd >= 0:    # ;Reject if X derivative not decreasing
   
            if not verbose:
                print('Unable to compute X centroid around position '+ pos)
                xcen[i]=-1 ; ycen[i]=-1
                continue

        dx = sumxsq*sumd/(sumc*sumxd)
        if ( np.abs(dx) > nhalf ):    #Reject if centroid outside box  
            if verbose:
                print('Computed X centroid for position '+ pos + ' out of range')
                xcen[i]=-1 ; ycen[i]=-1 
                continue

        xcen[i] = xmax - dx    #X centroid in original array

#  Find Y Centroid

        deriv = np.roll(strbox,-1,axis=0) - strbox    #;Shift in X & subtract to get derivative
        deriv = deriv[0:nbox-1,nhalf-ir:nhalf+ir+1]
        deriv = np.sum( deriv,1 )
        sumd =   np.sum( w*deriv )
        sumxd =  np.sum( w*deriv*dd )
        sumxsq = np.sum( w*dd**2 )

        if (sumxd >= 0):  #;Reject if Y derivative not decreasing
            if not verbose:
                print('Unable to compute Y centroid around position '+ pos)
                xcen[i] = -1 ; ycen[i] = -1
                continue

        dy = sumxsq*sumd/(sumc*sumxd)
        if (np.abs(dy) > nhalf):  #Reject if computed Y centroid outside box
            if verbose:
                print('Computed X centroid for position '+ pos + ' out of range')
                xcen[i]=-1 ; ycen[i]=-1
                continue
 
        ycen[i] = ymax-dy

    if npts == 1: xcen,ycen = xcen[0],ycen[0]
    return(xcen,ycen)

