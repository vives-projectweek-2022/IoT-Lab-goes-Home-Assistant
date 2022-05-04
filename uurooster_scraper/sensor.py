import requests
import html
import json
from homeassistant.helpers.entity import Entity
import homeassistant.helpers.config_validation as cv
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.util import Throttle
import voluptuous as vol
import urllib.error
from datetime import datetime, date, timedelta
import calendar


from .constants.const import (
    _LOGGER,
    CONF_SEL_JAAR,
    CONF_OBJID,
    CONF_SC_OBJID,
    CONF_UPDATE_FREQUENCY,
    SENSOR_PREFIX,
    ATTR_LAST_UPDATE,
    ATTR_UPDATE_FREQUENCY,
    ATTR_DAY,
    ATTR_TURN_ON_LIGHT_KLAS_2_85,
    ATTR_TURN_ON_LIGHT_KLAS_2_65,
    ATTR_TURN_OFF_LIGHT_KLAS_2_85,
    ATTR_TURN_OFF_LIGHT_KLAS_2_65,
    ATTR_MAANDAG_VAKKEN_TOTAAL,
    ATTR_MAANDAG_VAKKEN,
    ATTR_MAANDAG_START_UREN,
    ATTR_MAANDAG_STOP_UREN,
    ATTR_MAANDAG_KLASSEN,
    ATTR_DINSDAG_VAKKEN_TOTAAL,
    ATTR_DINSDAG_VAKKEN,
    ATTR_DINSDAG_START_UREN,
    ATTR_DINSDAG_STOP_UREN,
    ATTR_DINSDAG_KLASSEN,
    ATTR_WOENSDAG_VAKKEN_TOTAAL,
    ATTR_WOENSDAG_VAKKEN,
    ATTR_WOENSDAG_START_UREN,
    ATTR_WOENSDAG_STOP_UREN,
    ATTR_WOENSDAG_KLASSEN,
    ATTR_DONDERDAG_VAKKEN_TOTAAL,
    ATTR_DONDERDAG_VAKKEN,
    ATTR_DONDERDAG_START_UREN,
    ATTR_DONDERDAG_STOP_UREN,
    ATTR_DONDERDAG_KLASSEN,
    ATTR_VRIJDAG_VAKKEN_TOTAAL,
    ATTR_VRIJDAG_VAKKEN,
    ATTR_VRIJDAG_START_UREN,
    ATTR_VRIJDAG_STOP_UREN,
    ATTR_VRIJDAG_KLASSEN,
    API_ENDPOINT,
    CONF_ID
)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_SEL_JAAR, default="2021"): cv.string,
        vol.Required(CONF_OBJID, default="56226836"): cv.string,
        vol.Required(CONF_SC_OBJID, default="51917133"): cv.string,
        vol.Required(CONF_UPDATE_FREQUENCY, default=10): cv.string,
        vol.Optional(CONF_ID, default=""): cv.string,
    }
)


def setup_platform(hass, config, add_entities, discovery_info=None):
    _LOGGER.debug("Setup sensor")

    id_name = config.get(CONF_ID)
    sel_jaar = config.get(CONF_SEL_JAAR).lower().strip()
    objid = config.get(CONF_OBJID).strip()
    sc_objid = config.get(CONF_SC_OBJID).strip()
    update_frequency = timedelta(seconds=(int(config.get(CONF_UPDATE_FREQUENCY))))

    entities = []

    try:
        entities.append(
            Sensor(
                sel_jaar,
                objid,
                sc_objid,
                update_frequency,
                id_name,
            )
        )
    except urllib.error.HTTPError as error:
        _LOGGER.error(error.reason)
        return False

    add_entities(entities)


class Sensor(Entity):
    def __init__(
        self, sel_jaar, objid, sc_objid, update_frequency, id_name
    ):
        self.data = None
        self.sel_jaar = sel_jaar
        self.objid = objid
        self.sc_objid = sc_objid
        self.update = Throttle(update_frequency)(self._update)
        self._name = (
            SENSOR_PREFIX
            + (id_name + " " if len(id_name) > 0 else "")
            + sel_jaar
            + "_"
            + objid
            + "_"
            + sc_objid
        )
        self._state = None
        self._last_update = None
        self._update_frequency = None
        self._day = None
        self._turn_on_light_klas_2_85 = None
        self._turn_on_light_klas_2_65 = None
        self._turn_off_light_klas_2_85 = None
        self._turn_off_light_klas_2_65 = None
        self._turn_off_light = None
        self._vakken_maandag = None
        self._vakken_dinsdag = None
        self._vakken_woensdag = None
        self._vakken_donderdag = None
        self._vakken_vrijdag = None
        
        self._vakken_maandag_totaal = None
        self._vakken_dinsdag_totaal = None
        self._vakken_woensdag_totaal = None
        self._vakken_donderdag_totaal = None
        self._vakken_vrijdag_totaal = None
        
        self._start_uren_maandag = None
        self._start_uren_dinsdag = None
        self._start_uren_woensdag = None
        self._start_uren_donderdag = None
        self._start_uren_vrijdag = None
        
        self._stop_uren_maandag = None
        self._stop_uren_dinsdag = None
        self._stop_uren_woensdag = None
        self._stop_uren_donderdag = None
        self._stop_uren_vrijdag = None
        
        self._maandag_klassen = None
        self._dinsdag_klassen = None
        self._woensdag_klassen = None
        self._donderdag_klassen = None
        self._vrijdag_klassen = None
        
        self._attr_unique_id = sel_jaar + objid + sc_objid
        

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._state

    @property
    def extra_state_attributes(self):
        return {
            ATTR_LAST_UPDATE: self._last_update,
            ATTR_UPDATE_FREQUENCY: self._update_frequency,
            ATTR_DAY: self._day,
            ATTR_TURN_ON_LIGHT_KLAS_2_85: self._turn_on_light_klas_2_85,
            ATTR_TURN_ON_LIGHT_KLAS_2_65: self._turn_on_light_klas_2_65,
            ATTR_TURN_OFF_LIGHT_KLAS_2_85: self._turn_off_light_klas_2_85,
            ATTR_TURN_OFF_LIGHT_KLAS_2_65: self._turn_off_light_klas_2_65,
            
            ATTR_MAANDAG_VAKKEN_TOTAAL: self._vakken_maandag_totaal,
            ATTR_MAANDAG_VAKKEN: self._vakken_maandag,
            ATTR_MAANDAG_START_UREN: self._start_uren_maandag,
            ATTR_MAANDAG_STOP_UREN: self._stop_uren_maandag,
            ATTR_MAANDAG_KLASSEN: self._maandag_klassen,
            
            ATTR_DINSDAG_VAKKEN_TOTAAL: self._vakken_dinsdag_totaal,
            ATTR_DINSDAG_VAKKEN: self._vakken_dinsdag,
            ATTR_DINSDAG_START_UREN: self._start_uren_dinsdag,
            ATTR_DINSDAG_STOP_UREN: self._stop_uren_dinsdag,
            ATTR_DINSDAG_KLASSEN: self._dinsdag_klassen,
            
            ATTR_WOENSDAG_VAKKEN_TOTAAL: self._vakken_woensdag_totaal,
            ATTR_WOENSDAG_VAKKEN: self._vakken_woensdag,
            ATTR_WOENSDAG_START_UREN: self._start_uren_woensdag,
            ATTR_WOENSDAG_STOP_UREN: self._stop_uren_woensdag,
            ATTR_WOENSDAG_KLASSEN: self._woensdag_klassen,
            
            ATTR_DONDERDAG_VAKKEN_TOTAAL: self._vakken_donderdag_totaal,
            ATTR_DONDERDAG_VAKKEN: self._vakken_donderdag,
            ATTR_DONDERDAG_START_UREN: self._start_uren_donderdag,
            ATTR_DONDERDAG_STOP_UREN: self._stop_uren_donderdag,
            ATTR_DONDERDAG_KLASSEN: self._donderdag_klassen,
            
            ATTR_VRIJDAG_VAKKEN_TOTAAL: self._vakken_vrijdag_totaal,
            ATTR_VRIJDAG_VAKKEN: self._vakken_vrijdag,
            ATTR_VRIJDAG_START_UREN: self._start_uren_vrijdag,
            ATTR_VRIJDAG_STOP_UREN: self._stop_uren_vrijdag,
            ATTR_VRIJDAG_KLASSEN: self._vrijdag_klassen
        }

        


    def _update(self):
        url = (
            API_ENDPOINT
            + "laden.htm?sap-params=&sem=&otype=CE&kuloket=&objid="
            + self.objid
            + "&sc_objid="
            + self.sc_objid
            + "&taal=N&nieuwedatum=00000000&sel_jaar="
            + self.sel_jaar
            + "&acad_jaar=0000&combi_nr=000000&reeks_id_ce=000000&stage_studjar=&uname_docent=&print_versie=&sessionid=&OnInputProcessing=Continue"
        )
        
        start_dagen = ["Maandag","Dinsdag","Woensdag","Donderdag","Vrijdag"]
        end_dagen = ["Dinsdag","Woensdag","Donderdag","Vrijdag","Zaterdag"]
        maandag = []
        dinsdag = []
        woensdag = []
        donderdag = []
        vrijdag = []
        maandag_vakken = []
        dinsdag_vakken = []
        woensdag_vakken = []
        donderdag_vakken = []
        vrijdag_vakken = []
        maandag_start_uren = []
        dinsdag_start_uren = []
        woensdag_start_uren = []
        donderdag_start_uren = []
        vrijdag_start_uren = []
        maandag_stop_uren = []
        dinsdag_stop_uren = []
        woensdag_stop_uren = []
        donderdag_stop_uren = []
        vrijdag_stop_uren = []
        maandag_klassen = []
        dinsdag_klassen = []
        woensdag_klassen = []
        donderdag_klassen = []
        vrijdag_klassen = []
        
        def find_all(a_str, sub):
            start = 0
            while True:
                start = a_str.find(sub, start)
                if start == -1: return
                yield start
                start += len(sub)
                
                
        def parse_vak(substring, dag):
            listvariable3 = list(find_all(substring, "<I> "))
            listvariable4 = list(find_all(substring, "</I><BR><hr"))
            start2 = substring.find("<I> ", listvariable3[0]) + len("<I> ")
            end2 = substring.find("</I><BR><hr", listvariable4[0])
            substring3 = substring[start2:end2]
            if "Maandag" == dag:
                return maandag_vakken.append(substring3.rstrip())
            elif "Dinsdag" == dag:
                return dinsdag_vakken.append(substring3.rstrip())
            elif "Woensdag" == dag:
                return woensdag_vakken.append(substring3.rstrip())
            elif "Donderdag" == dag:
                return donderdag_vakken.append(substring3.rstrip())
            elif "Vrijdag" == dag:
                return vrijdag_vakken.append(substring3.rstrip())
            else:
                return None
        
        def parse_start_uur(substring, dag):
            listvariable3 = list(find_all(substring, "color=white>"))
            listvariable4 = list(find_all(substring, " tot"))
            start2 = substring.find("color=white>", listvariable3[0]) + len("color=white>")
            end2 = substring.find(" tot", listvariable4[0])
            substring3 = substring[start2:end2]
            if "Maandag" == dag:
                return maandag_start_uren.append(substring3)
            elif "Dinsdag" == dag:
                return dinsdag_start_uren.append(substring3)
            elif "Woensdag" == dag:
                return woensdag_start_uren.append(substring3)
            elif "Donderdag" == dag:
                return donderdag_start_uren.append(substring3)
            elif "Vrijdag" == dag:
                return vrijdag_start_uren.append(substring3)
            else:
                return None
            
        def parse_stop_uren(substring, dag):
            listvariable3 = list(find_all(substring, "tot "))
            listvariable4 = list(find_all(substring, "');"))
            start2 = substring.find("tot ", listvariable3[0]) + len("tot ")
            end2 = substring.find("');", listvariable4[0])
            substring3 = substring[start2:end2]
            if "Maandag" == dag:
                return maandag_stop_uren.append(substring3)
            elif "Dinsdag" == dag:
                return dinsdag_stop_uren.append(substring3)
            elif "Woensdag" == dag:
                return woensdag_stop_uren.append(substring3)
            elif "Donderdag" == dag:
                return donderdag_stop_uren.append(substring3)
            elif "Vrijdag" == dag:
                return vrijdag_stop_uren.append(substring3)
            else:
                return None
                
                
        def parse_klassen(substring, dag):
            
            listvariable3 = list(find_all(substring, "lokaal "))
            listvariable4 = list(find_all(substring, " ("))
                
            if listvariable3 and listvariable4:
                start2 = substring.find("lokaal ", listvariable3[0]) + len("lokaal ")
                end2 = substring.find(" (", listvariable4[0])
                substring3 = substring[start2:end2]
            else:
                substring3 = "online"
                    
            if ")</a>," in substring:
                new_substring = substring.split(")</a>,")[1]
                listvariable4 = list(find_all(new_substring, "lokaal "))
                listvariable5 = list(find_all(new_substring, " ("))
                start2 = new_substring.find("lokaal ", listvariable4[0]) + len("lokaal ")
                end2 = new_substring.find(" (", listvariable5[0])
                substring4 = new_substring[start2:end2]
                
                if "Maandag" == dag:
                    return maandag_klassen.append(substring3 + "-" + substring4)
                elif "Dinsdag" == dag:
                    return dinsdag_klassen.append(substring3 + "-" + substring4)
                elif "Woensdag" == dag:
                    return woensdag_klassen.append(substring3 + "-" + substring4)
                elif "Donderdag" == dag:
                    return donderdag_klassen.append(substring3 + "-" + substring4)
                elif "Vrijdag" == dag:
                    return vrijdag_klassen.append(substring3 + "-" + substring4)
                    
            if (listvariable3 and listvariable4) or (substring3 == "online"): 
                if "Maandag" == dag:
                    return maandag_klassen.append(substring3)
                elif "Dinsdag" == dag:
                    return dinsdag_klassen.append(substring3)
                elif "Woensdag" == dag:
                    return woensdag_klassen.append(substring3)
                elif "Donderdag" == dag:
                    return donderdag_klassen.append(substring3)
                elif "Vrijdag" == dag:
                    return vrijdag_klassen.append(substring3)
                
            return None
                    
        
        
        # sending get request
        r = requests.get(url=url)
        # extracting html response
        self.data = html.unescape(r.text)
        # multiply the price
        s = self.data

        try:
            if s:
                counter_end_dagen = 0
                for x in range(len(start_dagen)):
                    
                    # dagen van de week
                    start = s.find(start_dagen[x]) + len(start_dagen[x])
                    end = s.find(end_dagen[counter_end_dagen])
                    substring = s[start:end]

                    # vakken en uur pakken
                    listvariable = list(find_all(substring, "Om de links te bezoeken"))
                    listvariable1 = list(find_all(substring, "javascript:niets"))
                    count_vakken = len(listvariable)
                    
                    if count_vakken > 0:
                        for b in range(count_vakken):
                            start1 = substring.find("'<img src=icons/teacher.gif border=0>", listvariable[b]) + len("'<img src=icons/teacher.gif border=0>")
                            end1 = substring.find("javascript:niets", listvariable1[b])
                            substring1 = substring[start1:end1]
                            # add to array
                            if start_dagen[x] == "Maandag":
                                maandag.append(substring1)
                            elif start_dagen[x] == "Dinsdag":
                                dinsdag.append(substring1)    
                            elif start_dagen[x] == "Woensdag":
                                woensdag.append(substring1)               
                            elif start_dagen[x] == "Donderdag":
                                donderdag.append(substring1)
                            elif start_dagen[x] == "Vrijdag":
                                vrijdag.append(substring1)
                            else:
                                None
                                
                    
                    if x == 0 and len(maandag) > 0:
                        for y in range(len(maandag)):
                            substring2 = maandag[y]
                            
                            # parse vak
                            parse_vak(substring2, "Maandag")
                            
                            # parse start uur
                            parse_start_uur(substring2, "Maandag")
                            
                            # parse stop uur
                            parse_stop_uren(substring2, "Maandag")     

                            # parse klassen
                            parse_klassen(substring2, "Maandag")                            
                        
                        
                        
                    if x == 1 and len(dinsdag) > 0:
                        for ya in range(len(dinsdag)):
                            substring2 = dinsdag[ya]
                            
                            # parse vak
                            parse_vak(substring2, "Dinsdag")
                            
                            # parse start uur
                            parse_start_uur(substring2, "Dinsdag")
                            
                            # parse stop uur
                            parse_stop_uren(substring2, "Dinsdag")
                            
                            # parse klassen
                            parse_klassen(substring2, "Dinsdag")
                        
                        
                    if x == 2 and len(woensdag) > 0:
                        for yb in range(len(woensdag)):
                            substring2 = woensdag[yb]
                            
                            # parse vak
                            parse_vak(substring2, "Woensdag")
                            
                            # parse start uur
                            parse_start_uur(substring2, "Woensdag")
                            
                            # parse stop uur
                            parse_stop_uren(substring2, "Woensdag")
                            
                            # parse klassen
                            parse_klassen(substring2, "Woensdag")                            
                        
                        
                    if x == 3 and len(donderdag) > 0:
                        for yc in range(len(donderdag)):
                            substring2 = donderdag[yc]
                            
                            # parse vak
                            parse_vak(substring2, "Donderdag")
                            
                            # parse start uur
                            parse_start_uur(substring2, "Donderdag")
                            
                            # parse stop uur
                            parse_stop_uren(substring2, "Donderdag")
                            
                            # parse klassen
                            parse_klassen(substring2, "Donderdag")                            
                            
                        
                    if x == 4 and len(vrijdag) > 0:
                        for yd in range(len(vrijdag)):
                            substring2 = vrijdag[yd]
                            
                            # parse vak
                            parse_vak(substring2, "Vrijdag")
                            
                            # parse start uur
                            parse_start_uur(substring2, "Vrijdag")
                            
                            # parse stop uur
                            parse_stop_uren(substring2, "Vrijdag")
                            
                            # parse klassen
                            parse_klassen(substring2, "Vrijdag")                            
                            
                    
                    
                    # increment counter_end_dagen
                    counter_end_dagen = counter_end_dagen + 1   
            
            
            
                # Set the values of the sensor  "%d-%m-%Y %H:%M"
                self._last_update = datetime.today().strftime("%d-%m-%Y 17:00")
                my_date = date.today()
                self._day = calendar.day_name[my_date.weekday()]
                self._state = None
                self._update_frequency = "10 seconds"


                # set the attributes of the sensor

                # maandag
                self._vakken_maandag_totaal = len(maandag_vakken)
                self._vakken_maandag = maandag_vakken
                self._start_uren_maandag = maandag_start_uren
                self._stop_uren_maandag = maandag_stop_uren
                self._maandag_klassen = maandag_klassen
                # dinsdag
                self._vakken_dinsdag_totaal = len(dinsdag_vakken)
                self._vakken_dinsdag = dinsdag_vakken
                self._start_uren_dinsdag = dinsdag_start_uren
                self._stop_uren_dinsdag = dinsdag_stop_uren
                self._dinsdag_klassen = dinsdag_klassen
                # woensdag
                self._vakken_woensdag_totaal = len(woensdag_vakken)
                self._vakken_woensdag = woensdag_vakken
                self._start_uren_woensdag = woensdag_start_uren
                self._stop_uren_woensdag = woensdag_stop_uren
                self._woensdag_klassen = woensdag_klassen
                # donderdag
                self._vakken_donderdag_totaal = len(donderdag_vakken)
                self._vakken_donderdag = donderdag_vakken
                self._start_uren_donderdag = donderdag_start_uren
                self._stop_uren_donderdag = donderdag_stop_uren
                self._donderdag_klassen = donderdag_klassen
                # vrijdag
                self._vakken_vrijdag_totaal = len(vrijdag_vakken)
                self._vakken_vrijdag = vrijdag_vakken
                self._start_uren_vrijdag = vrijdag_start_uren
                self._stop_uren_vrijdag = vrijdag_stop_uren
                self._vrijdag_klassen = vrijdag_klassen
                # light
                self._turn_on_light_klas_2_85 = "false"
                self._turn_on_light_klas_2_65 = "false"
                self._turn_off_light_klas_2_85 = "false"
                self._turn_off_light_klas_2_65 = "false"


                # Calculating when to turn the lights on or off
                calcday = self._day
                calc_parse_time = self._last_update.split('2022 ')[1]
                calc_time_split1 = calc_parse_time.split(':')[0]
                calc_time_split2 = calc_parse_time.split(':')[1]
                
                if calcday == "Monday":
                    vakken_maandag = self._vakken_maandag_totaal
                    if vakken_maandag > 0:
                        for i in range(0, vakken_maandag):
                            
                            check = False
                            if self._maandag_klassen[i] == "02.85":
                                check = True
                                
                            check1 = False
                            if self._maandag_klassen[i] == "02.65":
                                check1 = True
                                
                            check2 = False    
                            if self._maandag_klassen[i] == "02.65-02.85":
                                check2 = True
                            
                            start_uur = self._start_uren_maandag[i]
                            start_uur_slit1 = start_uur.split(':')[0]
                            start_uur_slit2 = start_uur.split(':')[1]

                            if start_uur_slit1 == calc_time_split1 and (check or check2):
                                if calc_time_split2 == start_uur_slit2:
                                    self._turn_on_light_klas_2_85 = "true"
                                    
                            if start_uur_slit1 == calc_time_split1 and (check1 or check2):
                                if calc_time_split2 == start_uur_slit2:
                                    self._turn_on_light_klas_2_65 = "true"


                            
                            stop_uur = self._stop_uren_maandag[i]
                            stop_uur_slit1 = stop_uur.split(':')[0]
                            stop_uur_slit2 = stop_uur.split(':')[1]

                            if stop_uur_slit1 ==  calc_time_split1 and (check or check2):
                                if calc_time_split2 == stop_uur_slit2:
                                    self._turn_off_light_klas_2_85 = "true"
                                    
                            if stop_uur_slit1 ==  calc_time_split1 and (check1 or check2):
                                if calc_time_split2 == stop_uur_slit2:
                                    self._turn_off_light_klas_2_65 = "true"
                
                if calcday == "Tuesday":
                    vakken_dinsdag = self._vakken_dinsdag_totaal
                    if vakken_dinsdag > 0:
                        for i in range(0, vakken_dinsdag):
                                                        
                            check = False
                            if self._dinsdag_klassen[i] == "02.85":
                                check = True
                                    
                            check1 = False
                            if self._dinsdag_klassen[i] == "02.65":
                                check1 = True
                                    
                            check2 = False    
                            if self._dinsdag_klassen[i] == "02.65-02.85":
                                check2 = True
                                
                            start_uur = self._start_uren_dinsdag[i]
                            start_uur_slit1 = start_uur.split(':')[0]
                            start_uur_slit2 = start_uur.split(':')[1]
    
                            if start_uur_slit1 == calc_time_split1 and (check or check2):
                                if calc_time_split2 == start_uur_slit2:
                                    self._turn_on_light_klas_2_85 = "true"
                                        
                            if start_uur_slit1 == calc_time_split1 and (check1 or check2):
                                if calc_time_split2 == start_uur_slit2:
                                    self._turn_on_light_klas_2_65 = "true"
    
    
                                
                            stop_uur = self._stop_uren_dinsdag[i]
                            stop_uur_slit1 = stop_uur.split(':')[0]
                            stop_uur_slit2 = stop_uur.split(':')[1]
    
                            if stop_uur_slit1 ==  calc_time_split1 and (check or check2):
                                if calc_time_split2 == stop_uur_slit2:
                                    self._turn_off_light_klas_2_85 = "true"
                                        
                            if stop_uur_slit1 ==  calc_time_split1 and (check1 or check2):
                                if calc_time_split2 == stop_uur_slit2:
                                    self._turn_off_light_klas_2_65 = "true"

                                    
                                    
                if calcday == "Wednesday":
                    vakken_woensdag = self._vakken_woensdag_totaal
                    if vakken_woensdag > 0:
                        for i in range(0, vakken_woensdag):
                            check = False
                            if self._woensdag_klassen[i] == "02.85":
                                check = True
                                
                            check1 = False
                            if self._woensdag_klassen[i] == "02.65":
                                check1 = True
                                
                            check2 = False    
                            if self._woensdag_klassen[i] == "02.65-02.85":
                                check2 = True
                            
                            start_uur = self._start_uren_woensdag[i]
                            start_uur_slit1 = start_uur.split(':')[0]
                            start_uur_slit2 = start_uur.split(':')[1]

                            if start_uur_slit1 == calc_time_split1 and (check or check2):
                                if calc_time_split2 == start_uur_slit2:
                                    self._turn_on_light_klas_2_85 = "true"
                                    
                            if start_uur_slit1 == calc_time_split1 and (check1 or check2):
                                if calc_time_split2 == start_uur_slit2:
                                    self._turn_on_light_klas_2_65 = "true"


                            
                            stop_uur = self._stop_uren_woensdag[i]
                            stop_uur_slit1 = stop_uur.split(':')[0]
                            stop_uur_slit2 = stop_uur.split(':')[1]

                            if stop_uur_slit1 ==  calc_time_split1 and (check or check2):
                                if calc_time_split2 == stop_uur_slit2:
                                    self._turn_off_light_klas_2_85 = "true"
                                    
                            if stop_uur_slit1 ==  calc_time_split1 and (check1 or check2):
                                if calc_time_split2 == stop_uur_slit2:
                                    self._turn_off_light_klas_2_65 = "true"

                if calcday == "Thursday":
                    vakken_donderdag = self._vakken_donderdag_totaal
                    if vakken_donderdag > 0:
                        for i in range(0, vakken_donderdag):
                            check = False
                            if self._donderdag_klassen[i] == "02.85":
                                check = True
                                
                            check1 = False
                            if self._donderdag_klassen[i] == "02.65":
                                check1 = True
                                
                            check2 = False    
                            if self._donderdag_klassen[i] == "02.65-02.85":
                                check2 = True
                            
                            start_uur = self._start_uren_donderdag[i]
                            start_uur_slit1 = start_uur.split(':')[0]
                            start_uur_slit2 = start_uur.split(':')[1]

                            if start_uur_slit1 == calc_time_split1 and (check or check2):
                                if calc_time_split2 == start_uur_slit2:
                                    self._turn_on_light_klas_2_85 = "true"
                                    
                            if start_uur_slit1 == calc_time_split1 and (check1 or check2):
                                if calc_time_split2 == start_uur_slit2:
                                    self._turn_on_light_klas_2_65 = "true"


                            
                            stop_uur = self._stop_uren_donderdag[i]
                            stop_uur_slit1 = stop_uur.split(':')[0]
                            stop_uur_slit2 = stop_uur.split(':')[1]

                            if stop_uur_slit1 ==  calc_time_split1 and (check or check2):
                                if calc_time_split2 == stop_uur_slit2:
                                    self._turn_off_light_klas_2_85 = "true"
                                    
                            if stop_uur_slit1 ==  calc_time_split1 and (check1 or check2):
                                if calc_time_split2 == stop_uur_slit2:
                                    self._turn_off_light_klas_2_65 = "true"


                if calcday == "Friday":
                    vakken_vrijdag = self._vakken_vrijdag_totaal
                    if vakken_vrijdag > 0:
                        for i in range(0, vakken_vrijdag):
                            check = False
                            if self._vrijdag_klassen[i] == "02.85":
                                check = True
                                
                            check1 = False
                            if self._vrijdag_klassen[i] == "02.65":
                                check1 = True
                                
                            check2 = False    
                            if self._vrijdag_klassen[i] == "02.65-02.85":
                                check2 = True
                            
                            start_uur = self._start_uren_vrijdag[i]
                            start_uur_slit1 = start_uur.split(':')[0]
                            start_uur_slit2 = start_uur.split(':')[1]

                            if start_uur_slit1 == calc_time_split1 and (check or check2):
                                if calc_time_split2 == start_uur_slit2:
                                    self._turn_on_light_klas_2_85 = "true"
                                    
                            if start_uur_slit1 == calc_time_split1 and (check1 or check2):
                                if calc_time_split2 == start_uur_slit2:
                                    self._turn_on_light_klas_2_65 = "true"


                            
                            stop_uur = self._stop_uren_vrijdag[i]
                            stop_uur_slit1 = stop_uur.split(':')[0]
                            stop_uur_slit2 = stop_uur.split(':')[1]

                            if stop_uur_slit1 ==  calc_time_split1 and (check or check2):
                                if calc_time_split2 == stop_uur_slit2:
                                    self._turn_off_light_klas_2_85 = "true"
                                    
                            if stop_uur_slit1 ==  calc_time_split1 and (check1 or check2):
                                if calc_time_split2 == stop_uur_slit2:
                                    self._turn_off_light_klas_2_65 = "true"
            else:
                raise ValueError()
        except ValueError:
            self._state = None
            self._last_update = datetime.today().strftime("%d-%m-%Y %H:%M")
            self._update_frequency = None
            self._day = None
            self._turn_on_light_klas_2_85 = None
            self._turn_on_light_klas_2_65 = None
            self._turn_off_light_klas_2_85 = None
            self._turn_off_light_klas_2_65 = None
            self._vakken_maandag = None
            self._vakken_dinsdag = None
            self._vakken_woensdag = None
            self._vakken_donderdag = None
            self._vakken_vrijdag = None
            
            self._vakken_maandag_totaal = None
            self._vakken_dinsdag_totaal = None
            self._vakken_woensdag_totaal = None
            self._vakken_donderdag_totaal = None
            self._vakken_vrijdag_totaal = None
        
            self._start_uren_maandag = None
            self._start_uren_dinsdag = None
            self._start_uren_woensdag = None
            self._start_uren_donderdag = None
            self._start_uren_vrijdag = None
        
            self._stop_uren_maandag = None
            self._stop_uren_dinsdag = None
            self._stop_uren_woensdag = None
            self._stop_uren_donderdag = None
            self._stop_uren_vrijdag = None
            
            self._maandag_klassen = None
            self._dinsdag_klassen = None
            self._woensdag_klassen = None
            self._donderdag_klassen = None
            self._vrijdag_klassen = None