import pytest
from hypothesis import given
from hypothesis import strategies as st

from model import ReportResponse


@given(
    last_page_loaded=st.integers(min_value=1),
    last_item_within_the_page_loaded=st.integers(min_value=0, max_value=198),
)
def test_properly_gives_back_report_name(
    last_page_loaded: int, last_item_within_the_page_loaded: int
):
    report_name = "Test Report"
    response = ReportResponse(
        report_name=report_name,
        last_page_loaded=last_page_loaded,
        last_item_within_the_page_loaded=last_item_within_the_page_loaded,
    )
    assert response.report_name == report_name


@given(
    last_page_loaded=st.integers(min_value=1),
    last_item_within_the_page_loaded=st.integers(min_value=0, max_value=198),
)
def test_properly_gives_back_last_page_loaded(
    last_page_loaded: int, last_item_within_the_page_loaded: int
):
    report_name = "Test Report"
    response = ReportResponse(
        report_name=report_name,
        last_page_loaded=last_page_loaded,
        last_item_within_the_page_loaded=last_item_within_the_page_loaded,
    )
    assert response.last_page_loaded == response.last_page_loaded


@given(
    last_page_loaded=st.integers(min_value=1),
    last_item_within_the_page_loaded=st.integers(min_value=0, max_value=198),
)
def test_properly_gives_back_last_item_within_the_page_loaded(
    last_page_loaded: int, last_item_within_the_page_loaded: int
):
    report_name = "Test Report"
    response = ReportResponse(
        report_name=report_name,
        last_page_loaded=last_page_loaded,
        last_item_within_the_page_loaded=last_item_within_the_page_loaded,
    )
    assert (
        response.last_item_within_the_page_loaded
        == response.last_item_within_the_page_loaded
    )


@given(last_page_loaded=st.integers(min_value=1))
def test_entire_page_pulled_if_last_item_loaded_is_199(last_page_loaded: int):
    report_name = "Test Report"
    last_item_within_the_page_loaded = 199
    response = ReportResponse(
        report_name=report_name,
        last_page_loaded=last_page_loaded,
        last_item_within_the_page_loaded=last_item_within_the_page_loaded,
    )
    assert response.entire_page_pulled is True


@given(
    last_page_loaded=st.integers(min_value=1),
    last_item_within_the_page_loaded=st.integers(min_value=0, max_value=198),
)
def test_entire_page_pulled_if_last_item_loaded_is_between_0_and_199(
    last_page_loaded: int, last_item_within_the_page_loaded: int
):
    report_name = "Test Report"
    response = ReportResponse(
        report_name=report_name,
        last_page_loaded=last_page_loaded,
        last_item_within_the_page_loaded=last_item_within_the_page_loaded,
    )
    assert response.entire_page_pulled is False


@given(
    last_page_loaded=st.integers(min_value=1),
    last_item_within_the_page_loaded=st.integers(max_value=-1),
)
def test_last_item_pulled_cant_be_less_than_0(
    last_page_loaded: int, last_item_within_the_page_loaded: int
):
    report_name = "Test Report"
    with pytest.raises(ValueError):
        ReportResponse(
            report_name=report_name,
            last_page_loaded=last_page_loaded,
            last_item_within_the_page_loaded=last_item_within_the_page_loaded,
        )


@given(
    last_page_loaded=st.integers(min_value=1),
    last_item_within_the_page_loaded=st.integers(min_value=200),
)
def test_last_item_pulled_cant_be_more_than_199(
    last_page_loaded: int, last_item_within_the_page_loaded: int
):
    report_name = "Test Report"
    with pytest.raises(ValueError):
        ReportResponse(
            report_name=report_name,
            last_page_loaded=last_page_loaded,
            last_item_within_the_page_loaded=last_item_within_the_page_loaded,
        )


@given(
    last_page_loaded=st.integers(min_value=1),
    last_item_within_the_page_loaded=st.integers(min_value=0, max_value=199),
)
def test_will_pull_same_page_if_not_entire_page_is_pulled(
    last_page_loaded: int, last_item_within_the_page_loaded: int
):
    report_name = "Test Report"
    response = ReportResponse(
        report_name=report_name,
        last_page_loaded=last_page_loaded,
        last_item_within_the_page_loaded=last_item_within_the_page_loaded,
    )

    assert response.page_to_load == last_page_loaded


@given(last_page_loaded=st.integers(min_value=1))
def test_will_pull_same_page_if_not_entire_page_is_pulled(last_page_loaded: int):
    report_name = "Test Report"
    last_item_within_the_page_loaded = 199
    response = ReportResponse(
        report_name=report_name,
        last_page_loaded=last_page_loaded,
        last_item_within_the_page_loaded=last_item_within_the_page_loaded,
    )

    assert response.page_to_load == last_page_loaded + 1


@given(last_page_loaded=st.integers(min_value=1))
def test_item_to_start_loading_from_will_be_0_if_last_item_was_none(
    last_page_loaded: int,
):
    report_name = "Test Report"
    last_item_within_the_page_loaded = None
    response = ReportResponse(
        report_name=report_name,
        last_page_loaded=last_page_loaded,
        last_item_within_the_page_loaded=last_item_within_the_page_loaded,
    )

    assert response.item_to_start_loading_from == 0


@given(last_page_loaded=st.integers(min_value=1))
def test_if_last_page_was_completely_loaded_start_loading_at_0(last_page_loaded: int):
    report_name = "Test Report"
    last_item_within_the_page_loaded = 199
    response = ReportResponse(
        report_name=report_name,
        last_page_loaded=last_page_loaded,
        last_item_within_the_page_loaded=last_item_within_the_page_loaded,
    )

    assert response.item_to_start_loading_from == 0


@given(
    last_page_loaded=st.integers(min_value=1),
    last_item_within_the_page_loaded=st.integers(min_value=0, max_value=198),
)
def test_if_last_page_was_not_completely_loaded_start_loading_at_plus_one(
    last_page_loaded: int, last_item_within_the_page_loaded: int
):
    report_name = "Test Report"
    response = ReportResponse(
        report_name=report_name,
        last_page_loaded=last_page_loaded,
        last_item_within_the_page_loaded=last_item_within_the_page_loaded,
    )

    assert response.item_to_start_loading_from == last_item_within_the_page_loaded + 1
