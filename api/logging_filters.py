import logging

import aiotask_context as context


class CorrelationIdFilter(logging.Filter):
    def filter(self, record):
        try:
            correlation_id = context.get("X-Correlation-Id")
        # TODO: test fix. Must set context for test and then remove try/catch
        except (ValueError, AttributeError):
            correlation_id = None
        record.correlationid = correlation_id
        return True
