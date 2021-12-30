import json
from abc import ABCMeta, abstractmethod

import arrow

from model import ExternalResourceResponse
from settings import (PER_PAGE)


class AbstractMaropostFacade(object, metaclass=ABCMeta):
    @abstractmethod
    def get_page_of_data(self, page_number: int) -> ExternalResourceResponse:
        pass


class FakeMaropostFacadeWorking(AbstractMaropostFacade):
    def get_page_of_data(self, page_number: int) -> ExternalResourceResponse:
        return ExternalResourceResponse(
            success_status=True,
            data=[{"Data": "Blah blah"}, {"Data": "Blah!"}],
            error=None,
        )


class FakeMaropostFacadeBroken(AbstractMaropostFacade):
    def get_page_of_data(self, page_number: int) -> ExternalResourceResponse:
        return ExternalResourceResponse(
            success_status=False,
            data=None,
            error="Maropost is currently on fire. Please send 🚒🚒🚒",
        )


class MaropostFacade(AbstractMaropostFacade):
    def __init__(self, auth_token: str, endpoint_url: str, requests):
        self._auth_token = auth_token
        self._endpoint_url = endpoint_url
        self._requests = requests

    def get_page_of_data(self, page_number: int) -> ExternalResourceResponse:
        number_of_items_to_pull = PER_PAGE
        starting_datetime = arrow.get("1970-01-01T00:00:00.000-05:00")
        ending_datetime = arrow.now()

        try:
            maropost_response = self._requests.get(
                self._endpoint_url,
                params={
                    "auth_token": self._auth_token,
                    "per": str(number_of_items_to_pull),
                    "page": str(page_number),
                    "from": starting_datetime.format("YYYY-MM-DD"),
                    "to": ending_datetime.format("YYYY-MM-DD"),
                },
                headers={
                    "Content-Type": "application / json",
                    "Accept": "application / json",
                },
            )
            return ExternalResourceResponse(
                success_status=True,
                data=json.loads(maropost_response.content),
                error=None,
            )
        except Exception as e:
            return ExternalResourceResponse(
                success_status=False, data=None, error=str(e)
            )
