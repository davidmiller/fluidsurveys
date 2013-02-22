"""
fluidsurveys

Package init file
"""
import collections
import json
import os
import time

import requests

from _version import __version__

__all__ = [
    '__version__',
    'FluidAPI'
    ]

SimpleCache = collections.namedtuple('SimpleCache', 'access data')

def cache(name):
    """
    Decorator to cache the results of this method, using NAME as the
    key to our cache dict.

    Arguments:
    - `name`: str

    Return: callable
    Exceptions: None
    """
    def lazy_method(meth):
        "Wrapping meth"

        def cache_check_method(self, *args, **kwargs):
            "Workmethod"
            if name in self._cache:
                if time.time() - self._cache[name].access < self.cache_timeout:
                    return self._cache[name].data
            data = meth(self, *args, **kwargs)
            self._cache[name] = SimpleCache(time.time(), data)
            return data

        return cache_check_method

    return lazy_method

class FluidAPI(object):
    def __init__(self, key, password,
                 base_url='https://fluidsurveys.com/api/v2/',
                 cache_timeout=120):
        self.key = key
        self.password = password
        self.base_url = base_url
        self.cache_timeout = {}
        self._cache = {}

    def apicall(self, url):
        """
        Make a call to URL with the appropriate Auth credentials
        and return the result as a Python dict

        Arguments:
        - `url`: str

        Return: {,}
        Exceptions: None
        """
        resp = requests.get(url, auth=(self.key, self.password))
        return json.loads(resp.content)

    @cache('surveys')
    def surveys(self):
        """
        Return a list of available surveys as a Python dict

        Return: {,}
        Exceptions: None
        """
        restful = os.path.join(self.base_url, 'surveys/')
        return self.apicall(restful)

    def survey_details(self, surveyid):
        """
        Given a SURVEYID, return the details of the survey as a
        Python dict.

        Arguments:
        - `surveyid`: str

        Return: {,}
        Exceptions: None
        """
        # When this is a str the no-op isn't time consuming.
        # When this is an int. like when passed direct from
        # a survey dict as returned by the API, it stops path.join
        # blowing up.
        surveyid = str(surveyid)
        restful = os.path.join(self.base_url, 'surveys', surveyid)
        if restful[-1] != '/':
            restful += '/'
        return self.apicall(restful)

    def survey_named(self, name):
        """
        Given the NAME of a survey, return the survey details for that name
        or None.

        Arguments:
        - `name`: str

        Return: {,} or None
        Exceptions: None
        """
        surveys = self.surveys()
        matching = [s for s in surveys['surveys'] if s['name'] == name]
        if not matching:
            return
        the_survey = matching[0]
        return self.survey_details(the_survey['id'])
