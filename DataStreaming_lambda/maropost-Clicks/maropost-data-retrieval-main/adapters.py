from model import ReportResponse


class ReportResponseDynamodbAdapter(ReportResponse):
    def __init__(self, response_json):
        super(ReportResponseDynamodbAdapter, self).__init__(
            report_name=response_json["Item"]["report_name"],
            last_page_loaded=int(response_json["Item"]["last_page_loaded"]),
            last_item_within_the_page_loaded=response_json["Item"][
                "last_item_within_the_page_loaded"
            ],
        )
