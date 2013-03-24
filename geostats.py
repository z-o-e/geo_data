import numpy as np
import math
import matplotlib
import matplotlib.pyplot as plt
from optparse import OptionParser

#
# main(): main function
# read file from command line and plot World and American topolographic map
# input: none
# output: none
#
def main():
    #load data file from command line
    parser = OptionParser(usage = "%prog [options] arg1 arg2 arg3 arg4 arg5",
                          version = "version 1.0")
    parser.add_option("--file", dest = "filename",
                      help = "input data")
    parser.add_option("--lat", dest = "lat",
                      help = "starting latitude")
    parser.add_option("--latres", dest = "latres",
                      help = "resolution of latitude")
    parser.add_option("--lon", dest = "lon",
                      help = "starting longitude")
    parser.add_option("--lonres", dest = "lonres",
                      help = "resolution of longitude")
    (options, args) = parser.parse_args()

    # error handler
    if(options.filename == None):
        parser.error("missing filename")
    if(options.lat == None):
        parser.error("missing starting latitude")
    if(options.latres == None):
        parser.error("missing latitude resolution")
    if(options.lon == None):
        parser.error("missing longitude")
    if(options.lonres == None):
        parser.error("missing longitude resolution")

    # transfer data type
    x_delta = float(options.lonres)
    y_delta = float(options.latres)
    lon = float(options.lon)
    lat = float(options.lat)

    # calculate number of points in each axis
    lon_num = int((360 - lon) / x_delta) + 1
    lat_num = int((90 + lat) / y_delta) + 1
    lon_max = (lon_num - 1) * x_delta + lon
    lat_max = (lat_num - 1) * y_delta - lat

    # build x and y axis
    x = np.linspace(lon, lon_max, lon_num)
    y_r = np.linspace(- lat, lat_max, lat_num)

    # reverse the y axis to make north hemisphere at the top
    # and south hemisphere at the bottom
    y = y_r[::-1]

    # build the grid
    X, Y = np.meshgrid(x, y)

    # read altitude from file
    fd = open(options.filename, 'r')
    Z_1D = np.fromfile(file = fd, dtype = np.int, count = lon_num * lat_num,
                       sep = " ")
    Z = Z_1D.reshape(lat_num, -1)

    # find the highest and lowest point
    peak_x   = Z.argmax() % lon_num
    peak_y   = Z.argmax() / lon_num
    trench_x = Z.argmin() % lon_num
    trench_y = Z.argmin() / lon_num

    # calculate ocean area and volume
    print "Area of Ocean   = " + repr(area(lat_num, lat, y_delta, lon_num, Z_1D))\
          + " km^2 "
    print "Volume of Ocean = " + repr(volume(lat_num, lat, y_delta, lon_num, Z_1D))\
          + " km^3 "

    # plot the World topographic map
    plt.figure()
    CS = plt.contour(X, Y, Z)
    plt.annotate('highest', (peak_x, peak_y),
                 xytext = (peak_x - 10, peak_y + 10),
                 arrowprops=dict(arrowstyle="->"))
    plt.annotate('lowest', (trench_x, trench_y),
                 xytext = (trench_x - 10, trench_y + 10),
                 arrowprops=dict(arrowstyle="->"))
    plt.clabel(CS, inline=1, fontsize=10)
    plt.xlabel('longitude')
    plt.ylabel('S <---  latitude  ---> N')
    plt.title('World Topographic Map')

    # plot the American topographic map
    america_plot(lat_num, lat, y_delta, lon_num, lon, x_delta, x, y_r, Z)
    plt.show()

#
# area(): calculate the total ocean area
# input:
#       lat_num : total number of points in latitude axis
#       lat     : the starting point in latitude axis
#       lat_step: step in latitude axis
#       lon_num : total number of points in longitude axis
#       data    : input data from file
# output:
#       A       : total ocean area
#
def area(lat_num, lat, lat_step, lon_num, data):
    A = 0
    dtheta = math.pi / lat_num
    dphi   = 2 * math.pi / lon_num 
    for i in range(0, lat_num):
        for j in range(0, lon_num):
            # if this point is at or below sea level
            # treat it as ocean
            if(data[i * lat_num + j] <= 0):
                A = A + math.cos(lat / 180.0 * math.pi) * dtheta * dphi 
        lat = lat - lat_step
    A = A * pow(6378.1, 2)
    return A

#
# volume(): calculate the total ocean volume
# input:
#       lat_num : total number of points in latitude axis
#       lat     : the starting point in latitude axis
#       lat_step: step in latitude axis
#       lon_num : total number of points in longitude axis
#       data    : input data from file
# output:
#       V       : total ocean volume
#
def volume(lat_num, lat, lat_step, lon_num, data):
    V = 0
    dtheta = math.pi / lat_num
    dphi   = 2 * math.pi / lon_num 
    for i in range(0, lat_num):
        for j in range(0, lon_num):
            if(data[i * lat_num + j] < 0):
                V = V + math.cos(lat / 180.0 * math.pi) * \
                    dtheta * dphi * (- data[i * lat_num + j]) 
        lat = lat - lat_step
    V = V * pow(6378.1, 2) / 1000.
    return V
#
# america_plot(): draw the American topographic map
# input:
#       lat_num : total number of points in latitude axis
#       lat     : the starting point on latitude axis
#       lat_step: step in latitude axis
#       lon_num : total number of points in longitude axis
#       lon     : the starting point on longitude axis
#       lon_step: step in longitude axis
#       x       : original x axis from world map
#       y       : original y axis from world map
#       data    : input data from file
# output: none
#
def america_plot(lat_num, lat, lat_step, lon_num, lon, lon_step, x, y, data):
    # find the starting and ending point on x and y axis for America
    y_max = int((lat - 66.5) / lat_step) + 1
    y_min = int((lat - 12) / lat_step)
    y_axis= y[y_max: y_min + 1]
    x_min = (230 - lon) / lon_step + 1
    x_max = (300 - lon) / lon_step
    x_axis= x[x_min: x_max + 1]
    
    # make the north at top and south at bottom
    y_axis=y_axis[::-1]

    # clip the input World data to only America
    z     = data[y_max: y_min + 1]
    z     = np.transpose(z)
    z     = z[x_min: x_max + 1]
    Z     = np.transpose(z)

    # set up the plot
    X, Y = np.meshgrid(x_axis, y_axis)
    plt.figure()
    CS = plt.contour(X, Y, Z)
    plt.clabel(CS, inline=1, fontsize=10)
    plt.xlabel('longitude')
    plt.ylabel('latitude  ---> N')
    plt.title('American Topographic Map')
    plt.show()

if __name__ == '__main__':
    main()
