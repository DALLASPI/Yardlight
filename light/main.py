#!/usr/bin/env python 3
#
#
#
#
#
#
#Set Timer Functions
import datetime, time,calendar,math
from datetime import datetime
from datetime import timedelta
from time import sleep

#GPIO Library
import RPi.GPIO as GPIO

#Logging Function
import logging
import logging.handlers

#GetAstronomy Function
import bs4
from urllib.request import urlopen as uReq
from bs4 import BeautifulSoup as soup
import requests

#Some Colour Text
from colorama import Fore, Back, Style


class Light():


    def __init__(self):
        self.set_time = self


    def default_setup():

        global PIN, timeStart, timeStop, logger

        PIN = 8
        print( 'GPIO pin   : ', PIN )
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(PIN, GPIO.OUT)
        GPIO.output(PIN, True)
        now = datetime.now().strftime('%Y-%m-%d')
        try:
            logger = Light.start_logger('/home/pi/Yardlight/light/logs/'+now+'_light.log', 5000000, 5)
            logger.info(datetime.now().strftime(' %Y-%m-%d %I:%M %p') + ' Logger Started...')
        except Exception:
            print('Error Starting Logger')
        sleep(1)
        GetAstronomy()
        timeStart = sunset#'07:31 PM'#
        timeStop = sunrise#'07:32 PM'#
        logger.info(' Light Start time : {}'.format(timeStart) )
        logger.info(' Light Stop time  : {}'.format(timeStop) )
        print( '\nStart Time : {}'.format(timeStart),'\nStop Time  : {}'.format(timeStop))
        Light.time_difference()


    def custom_setup():
        global logger
        Light.set_pin()

        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(PIN, GPIO.OUT)
        GPIO.output(PIN, True)
        GetAstronomy()
        Light.set_on()
        Light.set_off()
        Light.time_difference()

        logger = Light.start_logger('/home/pi/Yardlight/light/logs/custom_yardlight.log', 5000000, 5)
        logger.info(' Logger Started...')
        logger.info(datetime.now().strftime('%Y-%m-%d %I:%M %p') + ' Script Started with custom settings.')
        sleep(1)


    def set_pin():

        global PIN

        print ( '\nThis project uses the physical pin mode GPIO.BOARD\n  ' )
        PIN = int ( input ( 'Choose a pin to use: ' ) )
        return PIN


    def set_on():

        global timeStart

        print('What time will the light turn on? \n')
        timeStart = Light.set_time()
        print('\nThe on time is set to '+ timeStart, '\n')

        return TIME_SET


    def set_off():

        global timeStop

        print('What time will the light turn off? \n')
        timeStop = Light.set_time()
        print('\nThe off time is set to '+timeStop, '\n')

        return TIME_SET


    def set_time():

        '''

    DOCSTRING: Returns TIME_SET = ['%I:%M %p'] / or [HH:MM AM/PM]
    Sliced values

    ##        HRS     = TIME_SET[:2]
    ##        MIN     = TIME_SET[3:5]
    ##        MER     = TIME_SET[6:]

        '''

        global HRS, MIN, MER, TIME_SET
        # Set the Hour
        HRS        = input('Hour: ').zfill(2)
        while HRS > '12' :
             print('Please enter a value between 1-12 ')
             HRS   = input('Hour: ').zfill(2)
        while len(HRS) > 2:
             print( 'Please enter a value between 1-12 ' )
             HRS = input('Hour: ').zfill(2)

        # Set the Minutes
        MIN = input('Minute: ').zfill(2)
        while MIN > '59':
            print( 'Please Enter a value between 0-59 ')
            MIN = input('Minute: ').zfill(2)
        while len(MIN) > 2:
             print('Please enter a value between 0-59 ' )
             MIN = input('Minute: ').zfill(2)

        # Set the Meridiem
        MERLIST = ['AM','PM'] #Create a  list to reference inside the method
        MER = input('AM or PM: ').upper()
        while MER not in MERLIST:
            print( 'Please Respond with AM or PM ' )
            MER = input( 'AM or PM:  ' ).upper()
        while len(MER) > 2:
            print( 'Please Respond with AM or PM ' )
            MER = input('AM or PM:  ').upper()

        #Create a return Variable TIME_SET = [HH:MM %p]
        TIME_SET = '{}:{} {}'
        TIME_SET = TIME_SET.format(HRS, MIN, MER).zfill(8)

        while TIME_SET == '00:00 PM':

            if yes_no('restart the start time? ') == True:
                Light.set_on()
                break

            else:
                if yes_no('restart the stop time? ') == True:
                    Light.set_off()
                    break
                else:
                    print("Valid Start/Stop times are required.\nLet's Start Over.\nWhat time will the light come on?\n")
                    Light.set_time()
                    break


        return TIME_SET


    def time_difference():

        from datetime import datetime

        """ Calculates the duration difference of set_on() and set_off()."""

        timeNow = datetime.now().strftime('%I:%M %p')

        global time_diff, minutes_diff,timeStop_sleep, timeStart_sleep, off_diff_minutes, off_diff_seconds

        timeFormat = '%I:%M %p'

        if timeStart[6:] == 'PM' and timeStop[6:] == 'AM': # For timedelta with PM to AM Meridiems

            time_diff = datetime.strptime ( timeStart, timeFormat )\
                      - datetime.strptime ( timeStop, timeFormat )

        else:
            # if timeStart[6:] == 'AM' and timeStop[6:] == 'PM'\
            # or timeStart[6:] == 'PM' and timeStop[6:] == 'PM'\
            # or timeStart[6:] == 'AM' and timeStop[6:] == 'AM':

            time_diff = datetime.strptime ( timeStop, timeFormat )\
                       - datetime.strptime ( timeStart, timeFormat )

        minutes_diff = int ( time_diff.seconds // 60 )

        off_diff = datetime.strptime ( timeStop, timeFormat )\
                    - datetime.strptime ( timeStart, timeFormat )
        off_diff_seconds = str(off_diff.seconds)
        off_diff_minutes = str((off_diff.seconds // 60))

        civil_twilight_duration= datetime.strptime(civil_twilight_start, timeFormat)\
                                 - datetime.strptime(nautical_twilight_start, timeFormat)

        print ( '\nDifference : {} {}'.format(str(off_diff).replace('-1 day, ','' ),' (HH:MM:SS)'))
        print ( 'Minutes    : {}'.format(off_diff_minutes))
        print ( 'Seconds    : {}'.format(off_diff_seconds)+'\n')
        
        logger.info(' Difference : {} {}'.format(str(off_diff).replace('-1 day, ','' ),' (HH:MM:SS)'))
        logger.info(' Minutes    : {}'.format(off_diff_minutes))
        logger.info(' Seconds    : {}'.format(off_diff_seconds)+'\n')

    def on():
        GPIO.output(PIN, False)

    def off():
        GPIO.output(PIN, True)

    # Main loop
    def main():
            
        """Main Loop"""
        
        global timeStart, timeStop
        try:
            x = True
            y = True
            z = True
            a = True
            weather_update = '00'
            while True:
                
                timeNow = datetime.now().strftime('%I:%M %p') #Gets the time
                minuteNow = datetime.now().strftime('%M') #Gets the time
                monthNow = datetime.now().strftime('%m').strip('0')
                    
                if timeNow == '12:00 AM' and y == True:
                    print(Fore.GREEN +'*************UPDATING YARDLIGHT***************')
                    
                    logger.info(datetime.now().strftime(' %Y-%m-%d %I:%M %p') + ' Updating Start and Stop times')
                    logger.info(' Old start  : {}'.format(timeStart))
                    logger.info(' Old stop   : {}'.format(timeStop))
                    #update start and stop times

                    GetTwilightZone()

                    timeStart = sunset
                    timeStop = sunrise

                    logger.info(' New start  : {}'.format(timeStart))
                    logger.info(' New stop   : {}'.format(timeStop))

                    Light.time_difference()
                    
                    logger.info(datetime.now().strftime(' %Y-%m-%d %I:%M %p') + ' Gathering Astronomical Data')
                    logger.info('{}'.format(title))
                    logger.info('Response from Site : {}'.format(response.status_code))
                    logger.info('Data provided by   : {}'.format(url))
                    logger.info('Daylight Hours        {} - {}\n                  Night                 {} - {}\n'.format(sunrise, sunset,astro_twilight_end, astro_twilight_start))
                    logger.info('Civil Twilight        {} - {}\n                                        {} - {}\n'.format(civil_twilight_start,sunrise,sunset, civil_twilight_end))
                    logger.info('Nautical Twilight     {} - {}\n                                        {} - {}\n'.format(nautical_twilight_start,civil_twilight_start,civil_twilight_end, nautical_twilight_end))
                    logger.info('Astronomical Twilight {} - {}\n                                        {} - {}\n'.format(astro_twilight_start,nautical_twilight_start,nautical_twilight_end, astro_twilight_end))

                    print('*************UPDATE COMPLETE****************'+Fore.WHITE)

                    y = False

                #Collect weather and astronomical data every hour on the hour    
                if minuteNow == weather_update and z == True:
                    #Try to get weather data.
                    try:
                        GetWeather()
                        sleep(1)
                        logger.info(datetime.now().strftime(' %Y-%m-%d %I:%M %p') + ' Gatherng Weather Data...')
                        logger.info(' {}'.format(title))
                        logger.info(' Response from Site : {}'.format(response.status_code))
                        logger.info(' Data provided by   : {}'.format(url))
                        logger.info(' Current Temp       : {}'.format(temp))
                        logger.info(' Condition Now      : {}'.format(cond))
                        logger.info(' Feels Like         : {}'.format(feels_like))
                        logger.info(' Todays Forecast    : {}'.format(hi_lo))
                        logger.info(' UV Index           : {}'.format(uv_index))
                        logger.info(' Wind               : {}'.format(wind))
                        logger.info(' Humidity           : {}'.format(humidity))
                        logger.info(' Dew Point          : {}'.format(dew_point))
                        logger.info(' Pressure           : {}'.format(pressure))
                        logger.info(' Visibility         : {}'.format(visibility)+'\n')
                    except Exception:
                        logger.error(datetime.now().strftime(' %Y-%m-%d %I:%M %p') + 'Error Getting Weather Data. \n')

                    #try to get sun data
                    try:
                        GetSolar()
                        sleep(1)
                        
                        logger.info(datetime.now().strftime(' %Y-%m-%d %I:%M %p') + ' Gatherng Solar Data...')
                        logger.info(' {}'.format(title))
                        logger.info(' Response from Site : {}'.format(response.status_code))
                        logger.info(' Data provided by : {}'.format(url))
                        logger.info(' Current Time     : {}'.format(current_time))
                        logger.info(' Sun Direction    : {}'.format(sun_direction))
                        logger.info(' Sun Altitude     : {}'.format(sun_altitude))
                        logger.info(' Equinox/Solstice : {}'.format(next_equinox))
                        logger.info(' Sunrise          : {}'.format(sunrise))
                        logger.info(' Sunset           : {}'.format(sunset))
                        logger.info(' Sunrise Direction: {}'.format(sunrise_direction))
                        logger.info(' Sunset Direction : {}'.format(sunset_direction)+'\n')
                    except Exception:
                        logger.error(datetime.now().strftime(' %Y-%m-%d %I:%M %p') + 'Error Getting Solar Data. /n')
                    #try to get lunar data
                    try:
                        GetLunar()
                        sleep(1)
                        logger.info(datetime.now().strftime(' %Y-%m-%d %I:%M %p') + ' Gatherng Lunar Data...')
                        logger.info(' {}'.format(title))
                        logger.info(' Response from Site : {}'.format(response.status_code))
                        logger.info(' Data provided by : {}'.format(url))
                        logger.info(' Current Time       : {}'.format(current_time))
                        logger.info(' Moon Direction     : {}'.format(moon_direction))
                        logger.info(' Moon Altitude      : {}'.format(moon_altitude))
                        logger.info(' Moon Distance      : {}'.format(moon_distance))
                        logger.info(' Next Full Moon     : {}'.format(next_full_moon))
                        logger.info(' Next New Moon      : {}'.format(next_new_moon))
                        logger.info(' {}'.format(next_state))
                        logger.info(' Moon Phase         : {}'.format(moon_phase)+'\n')
                    except Exception:
                        logger.error(datetime.now().strftime(' %Y-%m-%d %I:%M %p') + 'Error Getting Lunar Data. \n')
                    sleep(1)
                    #Only do this once in a one hour period.
                    z = False

                #if its not minute 00 z is true
                if minuteNow != weather_update :
                    z = True
                    sleep(1)
                
                if timeNow == astro_twilight_start and a == True:
                    print('Night Ended, Now Entering Astronomical Twilight {} - {}'.format(astro_twilight_start, nautical_twilight_start))
                    logger.info(' Now Entering Astronomical Twilight {} - {}'.format(astro_twilight_start, nautical_twilight_start))
                    a = False

                if timeNow == nautical_twilight_start and a == False:
                    print('Astronomical Twilight Ended, Now Entering Nautical Twilight {} - {}'.format(nautical_twilight_start, civil_twilight_start))
                    logger.info(' Now Entering Nautical Twilight {} - {}'.format(nautical_twilight_start, civil_twilight_start))
                    a = True
                        
                if timeNow == civil_twilight_start and a == True:
                    print('Nautical Twilight Ended, Now Entering Civil Twilight {} - {}'.format(civil_twilight_start, sunrise))
                    logger.info(' Nautical Twilight Ended, Now Entering Civil Twilight {} - {}'.format(civil_twilight_start, sunrise))
                    a = False
                        

                #ON (do the thing)   
                if timeNow == timeStart and x == True: #Turn ON yard light logic
                    Light.on() # Turns on light
                    print( '\nRelay is now on!! \nThe relay will shut off today at ' + timeStop )
                    logger.info(datetime.now().strftime(' %Y-%m-%d %I:%M %p') + ' Light ON   : '+str(off_diff_minutes)+' Mintues\n')
                    x = False
                    sleep(1)
                    
                  #OFF (stop doing the thing)   
                if timeNow == timeStop and x == False: # Turn OFF yard light logic
                    Light.off() # Turns off light
                    print( '\nRelay is now off!! \nThe relay will turn on again tomorrow at '+timeStart)
                    print(' \nCivil Twilight Started...')
                    logger.info(datetime.now().strftime(' %Y-%m-%d %I:%M %p') + ' Light OFF  : {} Minutes'.format(str(minutes_diff)))
                    logger.info(datetime.now().strftime(' %Y-%m-%d %I:%M %p') + ' Daylight   : {}'.format(daylight_hours))
                    x = True
                    y = True
                    a = True
                    sleep(1)
                
                if timeNow == civil_twilight_end and a == False:
                    print(' Civil Twilight Ended, Now Entering Nautical Twilight {}'.format(civil_twilight_end))
                    logger.info(' Civil Twilight Ended, Now Entering Nautical Twilight {}'.format(civil_twilight_end))
                    a = True
                    
                if timeNow == nautical_twilight_end and a == True:
                    print(' Nautical Twilight Ended, Now Entering Astronomical Twilight {}'.format(nautical_twilight_end))
                    logger.info(' Nautical Twilight Ended, Now Entering Astronomical Twilight {}'.format(nautical_twilight_end))
                    a = False
                    
                
                if timeNow == astro_twilight_end and a == False:
                    print(' Now Entering Night {}'.format(astro_twilight_end))
                    logger.info(' Astroomical Twilight Ended, Now Entering Night {}'.format(astro_twilight_end))
                    a = True
                else:
                    sleep(1)
                    continue
                    
        except KeyboardInterrupt:
            logger.warning(' KeyboardInterrupt!! Please restart yardlight.py')
            print('Main loop has stopped \nCleaning up GPIO pin')
            Light.destroy()


    def destroy():
        GPIO.output(PIN, True)
        GPIO.cleanup()


    def start_logger(filename, maxBytes, backupCount):

        '''

    start_logger(filename, maxBytes, backupCount) - " Creates a logger to record the Light.main() events.
    This could be used later on to update a web app of the lighting status."

        '''

        global logger

        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)

        # create file handler which logs even debug messages
        handler = logging.handlers.RotatingFileHandler(filename, 'w', maxBytes, backupCount)
        handler.setLevel(logging.INFO)

        # create formatter and add it to the handlers
        formatter = logging.Formatter( '%(levelname)s - %(name)s - %(message)s' )
        handler.setFormatter(formatter)

        # add the handlers to logger
        logger.addHandler(handler)
        logger.info(' Starting Logger....')

        return logger

def yes_no(question):
    reply = str(input(question+' (y/n): ')).lower().strip()
    if reply[0] == 'y':
        print('You Answered Yes')
        return True
    if reply[0] == 'n':
        return False
    else:
        return yes_or_no("Please respond with y/n or 'yes' or 'no' ")


def GetWeather():
    global page_soup, response, data,location, time_stamp, temp, cond, feels_like, hi_lo, uv_index, wind,\
           humidity, dew_point, pressure, visibility, data_list, url
    data = []
    url =  'https://weather.com/en-CA/weather/today/l/CAXX0619:1:CA'
    headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.75 Safari/537.36'}
    response = requests.get(url, headers = headers)
    uClient = uReq(url)
    page_html = uClient.read()
    uClient.close()
    page_soup = soup(page_html, 'html.parser')
    title = page_soup.title.text
    if response.status_code == 200:
        #Current Weather Conditions
        w = page_soup.find('div',{'class':'today_nowcard-section today_nowcard-condition'})
        w = w.findAll('div')
        [data.append(v.text) for i,v in enumerate(w)]
        data.pop(0)

        #wind, pressure, dew point, humidity and visibility

        right_now = page_soup.find('div', {'class','today_nowcard-sidecar component panel'})
        right_now = right_now.table.findAll('tr')
        [data.append(v.text) for i,v in enumerate(right_now)]

        #variables to store data
        location = page_soup.find('h1',{'class':'h4 today_nowcard-location'}).text
        time_stamp = page_soup.p.text
        temp = data[0]+'C'
        cond = data[1]
        feels_like = data[2].strip('Feels Like ')+'C'
        hi_lo = data[3][:-16]
        uv_index = data[4]
        wind= data[5].replace('Wind','')
        humidity = data[6].replace('Humidity','')
        dew_point = data[7].replace('Dew Point','')+'C' 
        pressure = str(round(float(data[8].strip('Pressure').replace(' mb ', '').replace(',',''))/10.0, 3)) + ' Kpa' 
        visibility = data[9].replace('Visibility','')
        data_list =[location,
                    time_stamp,
                    temp,
                    cond,
                    feels_like,
                    hi_lo,
                    uv_index,
                    wind,
                    humidity,
                    dew_point,
                    pressure,
                    visibility
                    ]
        print('\n{}'.format(title))
        print('Response from Site : {}'.format(response.status_code))
        print('Data provided by   : {}'.format(url))
        print('Current Weather Conditions for {}'.format(location))
        print('{} '.format(time_stamp))
        print('Current Temp.......: {}'.format(temp))
        print('Condition Now......: {}'.format(cond))
        print('Feels Like.........: {}'.format(feels_like))
        print('Todays Forecast....: {}'.format(hi_lo))
        print('UV Index...........: {}'.format(uv_index))
        print('Wind...............: {}'.format(wind))
        print('Humidity...........: {}'.format(humidity))
        print('Dew Point..........: {}'.format(dew_point))
        print('Pressure...........: {}'.format(pressure))
        print('Visibility.........: {}'.format(visibility))

    else:
        print('Bad Response From Site.')
        

def GetSolar():
    
    global p,page_soup, data, solar_data, title, status, current_time, sun_direction, sun_altitude,\
           next_equinox, sunrise, sunset, sunrise_direction, sunset_direction,\
           daylight, daylight_hours,url
    data = []
    url =  'https://www.timeanddate.com/sun/@6028050'
    headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.75 Safari/537.36'}
    response = requests.get(url, headers = headers)

    uClient = uReq(url)
    page_html = uClient.read()
    uClient.close()
    page_soup = soup(page_html, 'html.parser')

    if response.status_code == 200:
        title = page_soup.title.text
        data.append(title)
        #Get Quick Facts
        try:
            qfacts = page_soup.body.find('div',{'id':'qfacts'})
            [data.append(fact.text.replace('\xa0',' ')) for i, fact in enumerate(qfacts.findAll('p'))]
                 
        except Exception:
            pass

        #Get Paragraph
        try:
            p = page_soup.p.text
            data.append(p)
        except Exception :
            pass
        try:
            table = page_soup.find('table',{'id':'lm-key'})
            th = [th.text for th in table.find_all('th')]
            td = [td.text for td in table.find_all('td')]
            for i, v in enumerate(th):
                value = v+' '+td[i]
                data.append(value)
        except Exception:
            pass


        #astronomy data
        title = data[0]
        current_time = data[1].replace('Current Time: ','')
        sun_direction = data[2].replace('Sun Direction: ↑ ','')
        sun_altitude = data[3].replace('Sun Altitude: ','')
        sun_distance = data[4].strip('Sun Distance: ')
        next_equinox = data[5].strip('Next Equinox: ').replace('Solstice: ','')
        sunrise =data[6][:-10].strip('Sunrise Today: ').zfill(8).upper()
        sunset = data[7][:-11].strip('Sunset Today: ').zfill(8).upper()
        sunrise_direction = data[6][-9:]
        sunset_direction = data[7][-9:]
        daylight = sunrise+' - '+sunset
        daylight_hours = data[8][-20:]
        

        solar_data = [title,
                      current_time,
                      sun_direction,
                      sun_altitude,
                      next_equinox,
                      sunrise,
                      sunset,
                      sunrise_direction,
                      sunset_direction,
                      daylight,
                      daylight_hours
                      ]
        print('\n{}'.format(title))
        print('Response from Site : {}'.format(response.status_code))
        print('Data provided by   : {}'.format(url))
        print('Current Time       : {}'.format(current_time))
        print('Sun Direction      : {}'.format(sun_direction))
        print('Sun Altitude       : {}'.format(sun_altitude))
        print('Equinox/Solstice   : {}'.format(next_equinox))
        print('Sunrise            : {}'.format(sunrise))
        print('Sunset             : {}'.format(sunset))
        print('Sunrise Direction  : {}'.format(sunrise_direction))
        print('Sunset Direction   : {}'.format(sunset_direction))
        print('Daylight Time      : {}'.format(daylight))
        print('Daylight Hours     : {}'.format(daylight_hours))
    else:
        print('Bad Request From {}'.format(url))

        
def GetLunar():
    
    global p,page_soup, data, lunar_data, title, current_time, moon_direction, moon_altitude,\
           moon_distance, next_state , next_full_moon, next_new_moon,moon_phase, url
    data = []
    url =  'https://www.timeanddate.com/moon/@6028050'
    headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.75 Safari/537.36'}
    response = requests.get(url, headers = headers)

    uClient = uReq(url)
    page_html = uClient.read()
    uClient.close()
    page_soup = soup(page_html, 'html.parser')

    if response.status_code == 200: 
        title = page_soup.title.text
        data.append(title)

        #Get Quick Facts
        try:
            qfacts = page_soup.body.find('div',{'id':'qfacts'})
            [data.append(fact.text.replace('\xa0',' ')) for i, fact in enumerate(qfacts.findAll('p'))]
                 
        except Exception:
            pass
        #Get Paragraph
        try:
            p = page_soup.p.text
            data.append(p)
        except Exception :
            pass
        #Lunar data
        title = data[0]
        current_time = data[1].replace('Current Time: ','')
        moon_direction = data[2].replace('Moon Direction: ↑ ','')
        moon_altitude = data[3].replace('Moon Altitude: ','')
        moon_distance = data[4].replace('Moon Distance: ','')

        
        if 'Next New Moon: ' in data[5][:-18]:
            next_new_moon = data[5][:-7].replace('Next New Moon: ','')
            
        elif  'Next Full Moon: ' in data[5][:-18]:
            next_full_moon = data[5][:-7].replace('Next Full Moon: ','')

        if 'Next New Moon: ' in data[6][:-19]:
            next_new_moon =data[6][:-7].replace('Next New Moon: ','')
            
        elif 'Next Full Moon: ' in data[6][:-19]:
            next_full_moon = data[6][:-7].replace('Next Full Moon: ','')
            
        next_state = data[7]
        if 'Next Moonrise: ' in next_state:
            next_state = data[7].replace('Next Moonrise: ','Next Moonrise      : ')
            if 'Today' in next_state:
                next_state = next_state.replace('Today','Today ')
            if 'Tomorrow' in next_state:
                next_state = next_state.replace('Tomorrow','Tomorrow ')
        elif 'Next Moonset: ' in next_state:
            next_state = data[7].replace('Next Moonset: ','Next Moonset       : ')
            if 'Today' in next_state:
                next_state = next_state.replace('Today','Today ')
            if'Tomorrow' in next_state:
                next_state = next_state.replace('Tomorrow','Tomorrow ')
            
        moon_phase = data[8]
        

        lunar_data = [title,
                      current_time,
                      moon_direction,
                      moon_altitude,
                      moon_distance,
                      next_full_moon,
                      next_new_moon,
                      next_state,
                      moon_phase,
                      ]
        print('\n{}'.format(title))
        print('Response from Site : {}'.format(response.status_code))
        print('Data provided by   : {}'.format(url))
        print('Current Time       : {}'.format(current_time))
        print('Moon Direction     : {}'.format(moon_direction))
        print('Moon Altitude      : {}'.format(moon_altitude))
        print('Moon Distance      : {}'.format(moon_distance))
        
        print('Next Full Moon     : {}'.format(next_full_moon))
        print('Next New Moon      : {}'.format(next_new_moon))
        print('{}'.format(next_state))
        print('Moon Phase         : {}'.format(moon_phase))

    else:
        print('Bad Request From {}'.format(url))

def GetTwilightZone():
    global data, sunrise, sunset, astro_twilight_start,nautical_twilight_start,civil_twilight_start,\
               daylight,daylight_hours,civil_twilight_end,nautical_twilight_end,\
               astro_twilight_end,night,url, title,twilight_data
    data = []
    url =  'https://www.timeanddate.com/astronomy/@6028050'
    headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.75 Safari/537.36'}
    response = requests.get(url, headers = headers)
    uClient = uReq(url)
    page_html = uClient.read()
    uClient.close()
    page_soup = soup(page_html, 'html.parser')
    if response.status_code == 200:
        #get page title
        title = page_soup.title.text
        data.append(title)

        #Try Get Twilight times
        try:
            table = page_soup.find('table',{'id':'lm-key'})
            th = [th.text for th in table.find_all('th')]
            td = [td.text for td in table.find_all('td')]
            for i, v in enumerate(th):
                value = v+' '+td[i]
                data.append(value)
        except Exception:
            pass

        sunrise = data[5][:-10].replace(' Daylight ','').zfill(8).upper()
        sunset = data[5][-7:].zfill(8).upper()
        astro_twilight_start = data[2][17:-10].zfill(8).upper()
        nautical_twilight_start = data[3][19:-10].zfill(8).upper()
        civil_twilight_start = data[4][16:-10].zfill(8).upper()
        daylight = sunrise+' - '+sunset
        daylight_hours = data[5].replace(' Daylight ','').upper()
        
        civil_twilight_end = data[6][-7:].zfill(8).upper()
        nautical_twilight_end = data[7][-7:].zfill(8).upper()
        astro_twilight_end = data[8][-7:].zfill(8).upper()
        night_start = data[9][7:-11].zfill(8).upper()
        night_end = data[0][-7:].zfill(8).upper()
        night = data[9][7:-11].zfill(8).upper()+' - '+sunrise
        
        twilight_data = [title,
                         astro_twilight_start,
                         nautical_twilight_start,
                         civil_twilight_start,
                         sunrise,
                         sunset,
                         civil_twilight_end,
                         nautical_twilight_end,
                         astro_twilight_end,
                         night,
                         daylight,
                         daylight_hours,
                         ]
        print('\n{}'.format(title))
        print('Response from Site  : {}'.format(response.status_code))
        print('Data provided by    : {}'.format(url))
        print('Daylight Hours        {} - {}\nNight                 {} - {}\n'.format(sunrise, sunset,astro_twilight_end, astro_twilight_start))
        print('Civil Twilight        {} - {}\n                      {} - {}\n'.format(civil_twilight_start,sunrise,sunset, civil_twilight_end))
        print('Nautical Twilight     {} - {}\n                      {} - {}\n'.format(nautical_twilight_start,civil_twilight_start,civil_twilight_end, nautical_twilight_end))
        print('Astronomical Twilight {} - {}\n                      {} - {}\n'.format(astro_twilight_start,nautical_twilight_start,nautical_twilight_end, astro_twilight_end))

    else:
        print('Bad Request From {}'.format(url))




def GetAstronomy():
    GetWeather()
    GetSolar()
    GetTwilightZone()
    GetLunar()
Light.default_setup() 
Light.main()
