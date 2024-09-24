import os
import pytest
from urls_checker import *
from unittest.mock import patch, AsyncMock


@pytest.fixture
def url_checker():
    return UrlStatusChecker()


@pytest.mark.asyncio
async def test_check_urls_invalid(url_checker):
    with patch('aiohttp.ClientSession') as mock_session:
        mock_instance = mock_session.return_value
        mock_instance.__aenter__.return_value = mock_instance

        # Mocking the head response to return a non-200 status
        mock_head_response = AsyncMock()
        mock_head_response.status = 404
        mock_instance.head.return_value = mock_head_response

        list_urls = ['http://google.com']
        result = await url_checker.check_urls(list_urls)

        assert 'http://google.com' not in result


@pytest.mark.asyncio
async def test_check_urls_invalid_format(url_checker):
    with patch('sys.exit') as mock_exit:
        await url_checker.check_urls([])
        mock_exit.assert_called_once()


def test_read_file(url_checker):
    filename = 'temp_file.txt'
    with open(filename, 'w') as w:
        w.write(filename)
        w.close()
    assert read_file(filename)
    os.remove(filename)
