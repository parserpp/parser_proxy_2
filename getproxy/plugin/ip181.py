#! /usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals, absolute_import, division, print_function

import re
import logging
import retrying
import requests


logger = logging.getLogger(__name__)


class Proxy(object):
    def __init__(self):
        self.url = 'http://www.ip181.com/'
        self.re_ip_port_pattern = re.compile(
            r"<tr>\s+<td>(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})</td>\s+<td>(\d{1,5})</td>", re.I)

        self.cur_proxy = None
        self.proxies = []
        self.result = []

    @retrying.retry(stop_max_attempt_number=3)
    def extract_proxy(self):
        try:
            rp = requests.get(self.url, proxies=self.cur_proxy, timeout=10)
            re_ip_port_result = self.re_ip_port_pattern.findall(rp.text)

            if not re_ip_port_result:
                raise Exception("empty")

        except Exception as e:
            logger.error("[-] Request error: {error}".format( error=str(e)))
            while self.proxies:
                new_proxy = self.proxies.pop(0)
                self.cur_proxy = {new_proxy['type']: "%s:%s" % (new_proxy['host'], new_proxy['port'])}
                raise e
            else:
                return []

        return [{"host": host, "port": int(port), "from": "ip181"} for host, port in re_ip_port_result]

    def start(self):
        page_result = self.extract_proxy()
        if not page_result:
            return

        self.result.extend(page_result)


if __name__ == '__main__':
    p = Proxy()
    p.start()

    for i in p.result:
        print(i)
