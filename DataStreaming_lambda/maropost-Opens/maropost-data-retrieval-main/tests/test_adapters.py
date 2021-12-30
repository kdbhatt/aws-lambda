from hypothesis import given
from hypothesis import strategies as st

from adapters import ReportResponseDynamodbAdapter


@given(
    last_page_loaded=st.integers(min_value=1),
    last_item_within_the_page_loaded=st.integers(min_value=0, max_value=198),
)
def test_report_response_dynamodb_adapter(
    last_page_loaded: int, last_item_within_the_page_loaded: int
):
    report_name = "Test Report Name"

    response_json = {
        "Item": {
            "report_name": report_name,
            "last_page_loaded": last_page_loaded,
            "last_item_within_the_page_loaded": last_item_within_the_page_loaded,
        }
    }
    result = ReportResponseDynamodbAdapter(response_json=response_json)

    assert result.report_name == report_name
    assert result.last_page_loaded == last_page_loaded
    assert result.last_item_within_the_page_loaded == last_item_within_the_page_loaded
