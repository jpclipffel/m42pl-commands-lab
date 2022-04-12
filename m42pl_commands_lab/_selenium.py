from __future__ import annotations

from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.by import By

from m42pl.commands import GeneratingCommand, StreamingCommand
from m42pl.fields import Field
from m42pl.event import derive


DEFAULT_HUB: str = 'http://127.0.0.1:4444/wd/hub'
DEFAULT_BROWSER: str = 'CHROME'


class Selenium:
    """Selenium base class.
    """

    def __init__(self, hub: str = DEFAULT_HUB, browser: str = DEFAULT_BROWSER,
                    session: str|None = None, **kwargs):
        """
        :param hub:     Selenium hub URL
        :param browser: Browser name ('Chrome', 'Firefox', ...)
        :param session: Selenium's session ID
        """
        super().__init__(hub, browser, **kwargs)
        self.hub = Field(hub, default=DEFAULT_HUB, type=str)
        self.browser = Field(browser, default=DEFAULT_BROWSER, type=str)
        self.session = Field(session)

    async def setup(self, event, pipeline):
        self.hub_url = await self.hub.read(event, pipeline)
        self.driver_name = (await self.browser.read(event, pipeline)).upper()
        self.session_id = await self.session.read(event, pipeline)
        self.driver = None

    def close_driver(self):
        """Close the current driver.
        """
        try:
            if self.driver is not None and self.driver.session_id is not None:
                self.logger.debug(f'closing current session')
                self.driver.close()
        except Exception:
            pass
    
    def get_session(self, event):
        """Bind to a session or create a new one.

        :param event:   Source event
        """
        event_session_id = event['meta'].get('selenium_session_id')
        self.logger.debug(f'event session id: {event_session_id}')
        # ---
        # Source event has no session id and self has no one => create a new
        # session and inject session id in event
        if event_session_id is None and self.session_id is None:
            self.logger.debug(f'no session found, will create a new one')
            self.close_driver()
            self.logger.debug(f'creating a new driver')
            self.driver = webdriver.Remote(
                command_executor=self.hub_url,
                desired_capabilities=getattr(DesiredCapabilities, self.driver_name)
            )
            self.session_id = self.driver.session_id
            self.logger.debug(f'created new session: session_id="{self.session_id}"')
            event['meta']['selenium_session_id'] = self.driver.session_id
        # ---
        # Source event has no session id and self has one => inject session id
        # in event
        elif event_session_id is None and self.session_id is not None:
            self.logger.debug(f'injecting current session id in event: session_id="{self.session_id}"')
            event['meta']['selenium_session_id'] = self.session_id
        # ---
        # Source event has a session id and self has no one => reuse source
        # event session id
        elif event_session_id is not None and self.session_id is None:
            self.logger.debug(f'reusing existing session id: session_id={event_session_id}')
            self.close_driver()
            self.session_id = event_session_id
            self.driver = webdriver.Remote(
                command_executor=self.hub_url,
                desired_capabilities=getattr(DesiredCapabilities, self.driver_name)
            )
            self.driver.session_id = event_session_id
        # ---
        return event

    async def __aexit__(self, *args, **kwargs):
        self.close_driver()


class Get(Selenium, GeneratingCommand):
    _syntax_    = (
        '[url=]{url} [hub={hub url}] [browser={browser name}] '
        '[session={session id}]'
    )
    _aliases_   = ['selenium_get',]

    def __init__(self, url: str, **kwargs):
        super().__init__(url=url, **kwargs)
        self.url = Field(url)

    async def target(self, event, pipeline):
        try:
            event = self.get_session(event)
            url = await self.url.read(event, pipeline)
            self.driver.get(url)
        except Exception as error:
            self.logger.error(error)
            self.logger.exception(error)
        # event.meta['selenium_driver'] = self.driver
        yield derive(event, {
            'current_url': self.driver.current_url,
            'name': self.driver.name,
            'source': self.driver.page_source
        })


class Find(Selenium, StreamingCommand):
    _about_     = 'Locate elements in the current window'
    _syntax_    = '<kind> {locator}'
    _aliases_   = ['selenium_find',]

    def __init__(self, kind, locator, **kwargs):
        super().__init__(kind=kind, locator=locator, **kwargs)
        self.kind = Field(kind, default=kind)
        self.locator = Field(locator)

    async def setup(self, event, pipeline):
        await super().setup(event, pipeline)
        kind_name = await self.kind.read(event, pipeline)
        self.kind = getattr(
            By,
            kind_name.replace(' ', '_').replace('-', '_').upper()
        )

    async def target(self, event, pipeline):
        try:
            event = self.get_session(event)
            locator = await self.locator.read(event, pipeline)
            elements = self.driver.find_elements(
                self.kind,
                locator
            )
            for element in elements:
                yield derive(event, {
                    'status': {
                        'displayed': element.is_displayed(),
                        'selected': element.is_selected(),
                        'enabled': element.is_enabled(),
                    },
                    'text': element.text,
                    'source': element.get_attribute('outerHTML')
                })
        except Exception as error:
            self.logger.error(error)
            self.logger.exception(error)
