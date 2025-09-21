# import logging
#
# from prometheus_client import Counter
#
# from src.metrics.enums import EventCreationMetricNameEnum, EventMetricNameEnum
#
# logger = logging.getLogger(__name__)
#
#
# class EventMetric:
#     def __init__(self):
#         self.event_counter_metric = Counter(
#             name='events',
#             documentation='Common events metrics',
#             labelnames=['event'],
#         )
#
#     def inc(self, event: EventMetricNameEnum):
#         try:
#             self.event_counter_metric.labels(event=event.value).inc()
#         except Exception as e:
#             logger.error(f'Prometheus error: {e!s}')
#
#
# class EventCreationMetric:
#     def __init__(self):
#         self.event_creation_counter_metric = Counter(
#             name='event_creations',
#             documentation='Event creation metrics',
#             labelnames=['event_creation'],
#         )
#
#     def inc(self, event: EventCreationMetricNameEnum):
#         try:
#             self.event_creation_counter_metric.labels(event_creation=event.value).inc()
#         except Exception as e:
#             logger.error(f'Prometheus error: {e!s}')
#
#
# event_metric = EventMetric()
# event_creation_metric = EventCreationMetric()
