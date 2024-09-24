import re
import sys
import aiohttp
import asyncio
import traceback


def read_file(filename: str) -> list:
    try:
        with open(filename, 'r') as r:
            list_urls = r.readlines()
    except FileNotFoundError:
        raise FileNotFoundError(f'{filename} doesn\'t exist')
    return list_urls

def repchar(number: int) -> None:
    print('-' * number)


class UrlStatusChecker:
    def __init__(self):
        self.dict_sites = {}
        self.header = {'user-agent': 'Mozilla/5.0'}

    async def check_urls(self, list_urls) -> dict:
        if not isinstance(list_urls, list) or len(list_urls) == 0:
            print('A list with url is empty')
            sys.exit(1)

        tasks = []
        REGEX_URL = r'http(.?):\//[^\s]+[\/\w+]'
        for url in list_urls:
            url = url.rstrip('\n')
            if re.match(REGEX_URL, url):
                tasks.append(self.available_url(url))
            else:
                print(f'Строка "{url}" не является ссылкой')

        await asyncio.gather(*tasks)
        return self.dict_sites

    async def available_url(self, url: str):
        """
        In this method, we will verify the available HTTP status codes for
        the specified URL. More information in rfc 7231.
        """
        HTTP_METHODS = ('GET', 'POST', 'DELETE', 'PATCH', 'OPTIONS', 'HEAD',
                        'CONNECT', 'PUT', 'TRACE')

        self.dict_sites[url] = []
        try:
            async with aiohttp.ClientSession() as session:
                async with session.head(url, headers=self.header) as head_response:
                    # Проверка, что сайт вообще доступен
                    if head_response.status != 200:
                        self.dict_sites.pop(url)
                        print(f'An url {url} doesn\'t available.\
{head_response.status}')
                        return
                for method in HTTP_METHODS:
                    try:
                        async with session.request(method, url) as r:
                            status_code = r.status
                            if status_code != 405:
                                self.dict_sites[url].append({method: status_code})
                    except Exception as e:
                        print(f'[!] An error occurred: {e}')
        except aiohttp.client_exceptions.ClientConnectorError as e:
            print(f'An error occurated: {e}')



async def main():
    checker = UrlStatusChecker()
    urls = read_file('urls.txt')
    result = await checker.check_urls(urls)
    repchar(60)
    print(result)

        
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Exiting')
        sys.exit(0)
    except Exception:
        traceback.print_exc(file=sys.stdout)
        sys.exit(1)
