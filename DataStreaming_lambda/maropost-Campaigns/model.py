import json
from dataclasses import dataclass
from typing import Any, Optional
from settings import (PER_PAGE)


@dataclass
class ReportResponse:
    report_name: str
    last_page_loaded: int
    last_item_within_the_page_loaded: int

    def __init__(
        self,
        report_name: str,
        last_page_loaded: int,
        last_item_within_the_page_loaded: Optional[int],
    ):
        if type(last_item_within_the_page_loaded) == int:
            if (
                last_item_within_the_page_loaded > (self.per_page - 1)
                or last_item_within_the_page_loaded < 0
            ):
                raise ValueError

        self.report_name = report_name
        self.last_page_loaded = last_page_loaded
        self.last_item_within_the_page_loaded = last_item_within_the_page_loaded
        self.per_page = PER_PAGE

    # def __str__(self):
    #     return json.dumps(self, default=lambda o: o.__dict__)

    @property
    def entire_page_pulled(self) -> bool:
        if self.last_item_within_the_page_loaded == (self.per_page - 1):
            return True
        return False

    @property
    def page_to_load(self) -> int:
        if self.entire_page_pulled is True:
            return self.last_page_loaded + 1
        return self.last_page_loaded

    @property
    def item_to_start_loading_from(self) -> int:
        if self.entire_page_pulled is True:
            return 0
        if self.last_item_within_the_page_loaded is None:
            return 0

        return self.last_item_within_the_page_loaded + 1


@dataclass
class ExternalResourceResponse:
    success_status: bool
    data: Any
    error: Optional[str]
