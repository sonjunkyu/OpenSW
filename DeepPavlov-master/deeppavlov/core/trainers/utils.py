# Copyright 2019 Neural Networks and Deep Learning lab, MIPT
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from collections import OrderedDict, namedtuple
from dataclasses import is_dataclass
from functools import partial
from json import JSONEncoder
from typing import List, Tuple, Union, Iterable

import numpy as np

from deeppavlov.core.common.metrics_registry import get_metric_by_name

Metric = namedtuple('Metric', ['name', 'fn', 'inputs', 'alias'])


def parse_metrics(metrics: Iterable[Union[str, dict]], in_y: List[str], out_vars: List[str]) -> List[Metric]:
    metrics_functions = []
    for metric in metrics:
        if isinstance(metric, str):
            metric = {'name': metric, 'alias': metric}

        metric_name = metric.pop('name')
        alias = metric.pop('alias', metric_name)

        f = get_metric_by_name(metric_name)

        inputs = metric.pop('inputs', in_y + out_vars)
        if isinstance(inputs, str):
            inputs = [inputs]

        metrics_functions.append(Metric(metric_name, partial(f, **metric), inputs, alias))

    return metrics_functions


def prettify_metrics(metrics: List[Tuple[str, float]], precision: int = 4) -> OrderedDict:
    """Prettifies the dictionary of metrics."""
    prettified_metrics = OrderedDict()
    for key, value in metrics:
        if key in prettified_metrics:
            Warning("Multiple metrics with the same name {}.".format(key))
        if isinstance(value, float):
            value = round(value, precision)
        prettified_metrics[key] = value
    return prettified_metrics


class NumpyArrayEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif is_dataclass(obj):
            return obj.__dict__
        return JSONEncoder.default(self, obj)
