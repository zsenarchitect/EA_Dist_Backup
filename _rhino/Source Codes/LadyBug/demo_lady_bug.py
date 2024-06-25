import sys
sys.path.append("..\lib")
import EnneadTab
import sys
sys.path.append(r"L:\4b_Applied Computing\03_Rhino\12_EnneadTab for Rhino\Dependency Modules")

def main():
    # load epw weather data
    from ladybug.epw import EPW
    epw_data = EPW(r"C:\Users\szhang\Desktop\USA_NY_New.York.City-Central.Park.744860_TMY2\USA_NY_New.York.City-Central.Park.744860_TMY2.epw")
    dry_bulb_temp = epw_data.dry_bulb_temperature

    # Get altitude and longitude
    from ladybug.location import Location
    from ladybug.sunpath import Sunpath

    # Create location. You can also extract location data from an epw file.
    sydney = Location('Sydney', 'AUS', latitude=-33.87, longitude=151.22, time_zone=10)

    # Initiate sunpath
    sp = Sunpath.from_location(sydney)
    sun = sp.calculate_sun(month=11, day=15, hour=11.0)

    print('altitude: {}, azimuth: {}'.format(sun.altitude, sun.azimuth))



if __file__== "__main__":
    main()