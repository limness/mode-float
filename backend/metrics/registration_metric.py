import logging

from prometheus_client import Counter

from backend.metrics.enums import RegMetricNameEnum

logger = logging.getLogger(__name__)


class StartMetric:
    def __init__(self):
        self.start_counter_metric = Counter(
            name='starts', documentation='Total launches of the bot'
        )

    def inc(self):
        try:
            self.start_counter_metric.inc()
        except Exception as e:
            logger.error(f'Prometheus error: {e!s}')


class RegistrationMetric:
    def __init__(self):
        self.registration_counter_metric = Counter(
            name='registration_steps',
            documentation='Total registration steps',
            labelnames=['step'],
        )

    def inc(self, step: RegMetricNameEnum):
        try:
            self.registration_counter_metric.labels(step=step.value).inc()
        except Exception as e:
            logger.error(f'Prometheus error: {e!s}')


start_metric = StartMetric()
reg_metric = RegistrationMetric()
