import pandas as pd
import fastf1
import numpy as np
import country_converter as coco
import datetime as dt
from plugins.base_plugin.base_plugin import BasePlugin
from utils.app_utils import resolve_path
from utils.image_utils import resize_image
import logging


logger = logging.getLogger(__name__)

class F1(BasePlugin):

    def getData(self, settings):
            
            schedule = fastf1.get_event_schedule(2025, include_testing=False, backend='fastf1', force_ergast=False)
            eventDates = schedule.loc[:, ['EventDate']]
            eventDates['dateTime'] = eventDates.apply(lambda x: pd.to_datetime(eventDates['EventDate'], format='%Y-%M-%d'))
            date = np.datetime64('today', 'D')
            eventDates.set_index('dateTime', inplace=True)

            def findNearest():
                nearest = eventDates.index.get_indexer([date], method='backfill')
                nearestEventDate = eventDates.iloc[nearest]
                scheduleIndexed = schedule.set_index('EventDate') 
                filtered = nearestEventDate.reset_index(drop=True)
                nearestEvent = scheduleIndexed.loc[filtered['EventDate']]
                return nearestEvent

            nextCountry = findNearest()['Country'].iloc[0]
            nextLocation = findNearest()['Location'].iloc[0]
            nextEventDate = findNearest().index[0].date()
            nextCountryIso = coco.convert(names=nextCountry, to='ISO2')
            previousRound = findNearest()['RoundNumber'].iloc[0] - 1
            previousEvent = schedule.get_event_by_round(previousRound)
            previousCountry = previousEvent['Country']
            previousLocation = previousEvent['Location']
            previousEventDate = previousEvent['EventDate'].date()
            previousCountryIso = coco.convert(names=previousCountry, to='ISO2')
            session = fastf1.get_session(2025, previousRound, 'Race', backend='fastf1')
            session.load()
            results = session.results.iloc[0:20].loc[:, ['BroadcastName', 'Position', 'TeamName', 'TeamColor', 'HeadshotUrl']]
            position1Name = results['BroadcastName'].iloc[0]
            position1Team = results['TeamName'].iloc[0]
            position1Photo = results['HeadshotUrl'].iloc[0]
            position1Color = results['TeamColor'].iloc[0]
            position2Name = results['BroadcastName'].iloc[1]
            position2Team = results['TeamName'].iloc[1]
            position2Photo = results['HeadshotUrl'].iloc[1]
            position2Color = results['TeamColor'].iloc[1]
            position3Name = results['BroadcastName'].iloc[2]
            position3Team = results['TeamName'].iloc[2]
            position3Photo = results['HeadshotUrl'].iloc[2]
            position3Color = results['TeamColor'].iloc[2]

            data = {
                 'plugin_settings': settings,
                 'date': date,
                 'position1': {
                      'name': position1Name,
                      'team': position1Team,
                      'color': position1Color,
                      'photo': position1Photo
                 },
                 'position2': {
                      'name': position2Name,
                      'team': position2Team,
                      'color': position2Color,
                      'photo': position2Photo
                 },
                 'position3': {
                      'name': position3Name,
                      'team': position3Team,
                      'color': position3Color,
                      'photo': position3Photo
                 },
                 'previousEvent': {
                      'location': previousLocation,
                      'date': previousEventDate,
                      'country': previousCountry,
                      'code': previousCountryIso
                 },
                 'nextEvent': {
                      'location': nextLocation,
                      'date': nextEventDate,
                      'country': nextCountry,
                      'code': nextCountryIso
                 }
            }


            return data
    
    
    
    def generate_image(self, settings, device_config):

        dimensions = device_config.get_resolution()
        if device_config.get_config("orientation") == "vertical":
            dimensions = dimensions[::-1]

        image_template_params = self.getData(settings)
        
        image = self.render_image(dimensions, "f1.html", "f1.css", image_template_params)
        if not image:
            raise RuntimeError("Failed to take screenshot, please check logs.")
        return image


    