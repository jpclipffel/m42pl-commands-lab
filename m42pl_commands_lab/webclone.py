from __future__ import annotations

import regex
import aiohttp
from lxml import etree
from pathlib import Path
from urllib.parse import urlparse

from m42pl.commands import StreamingCommand
from m42pl.fields import Field
from m42pl.event import derive


class WebClone(StreamingCommand):
    """Clones a webpage.

    The command also clone the page remote objects (links).
    """

    _aliases_   = ['webclone', 'web_clone']
    _syntax_    = '[url=]{page url} [path=]<sites root directory>'

    def __init__(self, url: str, path: str):
        self.url = Field(url)
        self.path = Field(path)
        self.xml_parser = etree.HTMLParser()
        self.xpath_links = etree.XPath('//link[@rel="stylesheet" or @rel="shortcut icon"]/@href | //img/@src')

    async def setup(self, event, pipeline):
        self.session = await aiohttp.ClientSession().__aenter__()
        # Setup sites root paths
        self.root = Path(await self.path.read(event, pipeline))

    def is_file(self, url_path):
        filter(None, url_path.split('/'))

    # def store_page(self, url, data: bytes|str):
    #     # Parse page URL, build its fs path and mkdir its parent
    #     page_url = urlparse(url)
    #     page_root = Path(self.root, page_url.netloc, page_url.path)
    #     page_root.parent.mkdir(parents=True, exist_ok=True)
    #     # Write page content
    #     if isinstance(data, str):
    #         page_root.write_text(data)
    #     else:
    #         page_root.write_bytes(data)

    async def target(self, event, pipeline):
        # Read and parse URL
        site_url = await self.url.read(event, pipeline)
        site_url_parsed = urlparse(site_url)
        # Deduce site root and create directory
        site_root = Path(self.root, site_url_parsed.netloc)
        # site_root.mkdir(parents=True, exist_ok=True)
        # Get URL
        async with self.session.get(site_url) as response:
            # Get response content
            page_src = await response.read()
            # Store page
            # self.store_page(url, page_src)
            # Parse response content as XML
            page_tree = etree.fromstring(
                page_src.decode('UTF-8'),
                parser=self.xml_parser
            )
            # Extract and process links
            links = self.xpath_links(page_tree)
            for link_url in links:
                # Parse link and build fs path
                link_url_parsed = urlparse(link_url)

                # Set correct netloc
                netloc = len(link_url_parsed.netloc) > 0 and link_url_parsed.netloc or site_url_parsed.netloc

                link_path = self.root.joinpath(
                    netloc,
                    link_url_parsed.path.lstrip('/')
                )
                # ---
                print(link_url)
                yield derive(event, {
                    'link': {
                        'url': link_url,
                        'path': link_path.as_posix(),
                    }
                })

    async def teardown(self, *args, **kwargs):
        try:
            await self.session.__aclose__()
        except Exception:
            pass
