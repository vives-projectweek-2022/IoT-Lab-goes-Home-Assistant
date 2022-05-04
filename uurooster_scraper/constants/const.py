import logging

CONF_ID = "id"
CONF_SEL_JAAR = "sel_jaar"
CONF_OBJID = "objid"
CONF_SC_OBJID = "sc_objid"
CONF_UPDATE_FREQUENCY = "update_frequency"

SENSOR_PREFIX = "uuroosterscraper "
ATTR_LAST_UPDATE = "last_update"
ATTR_UPDATE_FREQUENCY = "update_frequency"
ATTR_DAY = "day"
ATTR_TURN_ON_LIGHT_KLAS_2_85 = "TURN_ON_LIGHT_KLAS_2_85"
ATTR_TURN_ON_LIGHT_KLAS_2_65 = "TURN_ON_LIGHT_KLAS_2_65"
ATTR_TURN_OFF_LIGHT_KLAS_2_85 = "TURN_OFF_LIGHT_KLAS_2_85"
ATTR_TURN_OFF_LIGHT_KLAS_2_65 = "TURN_OFF_LIGHT_KLAS_2_65"
ATTR_MAANDAG_VAKKEN_TOTAAL = "maandag_vakken_totaal"
ATTR_DINSDAG_VAKKEN_TOTAAL = "dinsdag_vakken_totaal"
ATTR_WOENSDAG_VAKKEN_TOTAAL = "woensdag_vakken_totaal"
ATTR_DONDERDAG_VAKKEN_TOTAAL = "donderdag_vakken_totaal"
ATTR_VRIJDAG_VAKKEN_TOTAAL = "vrijdag_vakken_totaal"
ATTR_MAANDAG_VAKKEN = "maandag_vakken"
ATTR_DINSDAG_VAKKEN = "dinsdag_vakken"
ATTR_WOENSDAG_VAKKEN = "woensdag_vakken"
ATTR_DONDERDAG_VAKKEN = "donderdag_vakken"
ATTR_VRIJDAG_VAKKEN = "vrijdag_vakken"

ATTR_MAANDAG_START_UREN = "maandag_start_uren"
ATTR_DINSDAG_START_UREN = "dinsdag_start_uren"
ATTR_WOENSDAG_START_UREN = "woensdag_start_uren"
ATTR_DONDERDAG_START_UREN = "donderdag_start_uren"
ATTR_VRIJDAG_START_UREN = "vrijdag_start_uren"

ATTR_MAANDAG_STOP_UREN = "maandag_stop_uren"
ATTR_DINSDAG_STOP_UREN = "dinsdag_stop_uren"
ATTR_WOENSDAG_STOP_UREN = "woensdag_stop_uren"
ATTR_DONDERDAG_STOP_UREN = "donderdag_stop_uren"
ATTR_VRIJDAG_STOP_UREN = "vrijdag_stop_uren"

ATTR_MAANDAG_KLASSEN = "maandag_klassen"
ATTR_DINSDAG_KLASSEN = "dinsdag_klassen"
ATTR_WOENSDAG_KLASSEN = "woensdag_klassen"
ATTR_DONDERDAG_KLASSEN = "donderdag_klassen"
ATTR_VRIJDAG_KLASSEN = "vrijdag_klassen"

API_ENDPOINT = "http://webwsp.aps.kuleuven.be/sap(bD1ubCZjPTIwMA==)/public/bsp/sap/z_mijnuurrstrs/"

_LOGGER = logging.getLogger(__name__)