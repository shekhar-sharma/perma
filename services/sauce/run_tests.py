from __future__ import print_function

import new
import os
import unittest
import requests
from sauceclient import SauceClient
import sys
from selenium import webdriver


# get settings
import time
from selenium.common.exceptions import ElementNotVisibleException


SCRIPT_DIR = os.path.dirname(__file__)
HOST = os.environ.get('HOST', 'http://perma-stage.law.harvard.edu')
USERNAME = os.environ.get('SAUCE_USERNAME')
ACCESS_KEY = os.environ.get('SAUCE_ACCESS_KEY')
assert USERNAME and ACCESS_KEY, "Please make sure that SAUCE_USERNAME and SAUCE_ACCESS_KEY are set."

# base setup
sauce = SauceClient(USERNAME, ACCESS_KEY)
os.chdir(SCRIPT_DIR)


# set up browsers
# options: https://saucelabs.com/platforms
browsers = [
    {"platform": "Mac OS X 10.9",
    "browserName": "chrome",
    "version": "31"},

    {"platform": "Windows 8.1",
    "browserName": "internet explorer",
    "version": "11"},

    {"platform": "Windows 7",
     "browserName": "firefox",
     "version": "30"},

    {"platform": "Windows XP",
     "browserName": "internet explorer",
     "version": "8"},

    {"platform": "OS X 10.9",
    "browserName": "iPhone",
    "version": "7.1",
    "device-orientation": "portrait",
    "nonSyntheticWebClick": False},
]

## helpers
def on_platforms(platforms):
    """
        Run given unit test in each platform (browser) provided.
        Via http://saucelabs.com/examples/example.py
    """
    def decorator(base_class):
        module = sys.modules[base_class.__module__].__dict__
        for i, platform in enumerate(platforms):
            d = dict(base_class.__dict__)
            d['desired_capabilities'] = platform
            name = "%s_%s_%s" % (platform['platform'], platform['browserName'], platform['version'])
            module[name] = new.classobj(name, (base_class,), d)
    return decorator


@on_platforms(browsers)
class PermaTest(unittest.TestCase):
    def setUp(self):
        self.desired_capabilities['name'] = self.id()

        sauce_url = "http://%s:%s@ondemand.saucelabs.com:80/wd/hub"
        self.driver = webdriver.Remote(
            desired_capabilities=self.desired_capabilities,
            command_executor=sauce_url % (USERNAME, ACCESS_KEY)
        )
        self.driver.implicitly_wait(30)

    def test_all(self):
        # get host
        host = HOST
        if not host.startswith('http'):
            host = "http://"+host

        self.driver.implicitly_wait(10)

        # helpers
        def click_link(link_text):
            self.driver.find_element_by_link_text(link_text).click()

        def get_xpath(xpath):
            return self.driver.find_element_by_xpath(xpath)

        def get_id(id):
            return self.driver.find_element_by_id(id)

        def info(*args):
            print("%s %s %s:" % (
                self.desired_capabilities['platform'],
                self.desired_capabilities['browserName'],
                self.desired_capabilities['version'],
            ), *args)

        def repeat_while_exception(func, exception=Exception, timeout=10, sleep_time=.1):
            end_time = time.time()+timeout
            while True:
                try:
                    return func()
                except exception:
                    if time.time()>end_time:
                        raise
                    time.sleep(sleep_time)


        info("Loading homepage from %s." % host)
        self.driver.get(host)
        assert "Websites Change, Go Away, and Get Taken Down" in get_xpath('//body').text

        info("Loading docs.")
        get_xpath("//a[@href='/docs']").click()
        assert "Overview" in get_xpath('//body').text

        info("Logging in.")
        click_link("Log in")
        assert "Email address" in get_xpath('//body').text
        get_id('id_username').send_keys('test_registrar_member@example.com')
        get_id('id_password').send_keys('pass')
        get_xpath("//button[@class='btn-success login']").click()
        body_text = repeat_while_exception(lambda: get_xpath('//body').text)
        assert "Create a Perma link" in body_text

        info("Creating archive.")
        url_input = get_id('rawUrl') # type url
        url_input.click()
        url_input.send_keys("example.com")
        get_id('addlink').click() # submit
        thumbnail = get_xpath("//div[@class='library-thumbnail']/img")
        thumbnail_data = requests.get(thumbnail.get_attribute('src'))
        with open('assets/example.com_thumbnail.png') as compare_file:
            compare_data = compare_file.read()
            assert thumbnail_data.content == compare_data

        info("Viewing playback.")
        archive_url = get_xpath("//a[@class='btn-padding btn btn-success']").get_attribute('href') # get url from green button
        self.driver.get(archive_url)
        assert "Live page view" in get_xpath('//body').text
        archive_view_link = get_id('warc_cap_container_complete')
        repeat_while_exception(lambda: archive_view_link.click(), ElementNotVisibleException)
        warc_url = self.driver.find_elements_by_tag_name("iframe")[0].get_attribute('src')
        self.driver.get(warc_url)
        assert "This domain is established to be used for illustrative examples" in get_xpath('//body').text

    def tearDown(self):
        print("Link to your job: https://saucelabs.com/jobs/%s" % self.driver.session_id)
        try:
            if sys.exc_info() == (None, None, None):
                sauce.jobs.update_job(self.driver.session_id, passed=True)
            else:
                sauce.jobs.update_job(self.driver.session_id, passed=False)
        finally:
            self.driver.quit()



if __name__ == '__main__':
    unittest.main()