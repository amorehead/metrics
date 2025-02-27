# Copyright The PyTorch Lightning team.
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
from collections import namedtuple

import numpy as np
import pytest
import torch
from sklearn.metrics import auc as _sk_auc
from torch import tensor

from tests.helpers.testers import NUM_BATCHES, MetricTester
from torchmetrics.classification.auc import AUC
from torchmetrics.functional import auc

torch.manual_seed(42)


def sk_auc(x, y):
    x = x.flatten()
    y = y.flatten()
    return _sk_auc(x, y)


Input = namedtuple('Input', ["x", "y"])

_examples = []
# generate already ordered samples, sorted in both directions
for i in range(4):
    x = np.random.randint(0, 5, (NUM_BATCHES * 8))
    y = np.random.randint(0, 5, (NUM_BATCHES * 8))
    idx = np.argsort(x, kind='stable')
    x = x[idx] if i % 2 == 0 else x[idx[::-1]]
    y = y[idx] if i % 2 == 0 else x[idx[::-1]]
    x = x.reshape(NUM_BATCHES, 8)
    y = y.reshape(NUM_BATCHES, 8)
    _examples.append(Input(x=tensor(x), y=tensor(y)))


@pytest.mark.parametrize("x, y", _examples)
class TestAUC(MetricTester):

    @pytest.mark.parametrize("ddp", [False])
    @pytest.mark.parametrize("dist_sync_on_step", [True, False])
    def test_auc(self, x, y, ddp, dist_sync_on_step):
        self.run_class_metric_test(
            ddp=ddp,
            preds=x,
            target=y,
            metric_class=AUC,
            sk_metric=sk_auc,
            dist_sync_on_step=dist_sync_on_step,
        )

    def test_auc_functional(self, x, y):
        self.run_functional_metric_test(x, y, metric_functional=auc, sk_metric=sk_auc, metric_args={"reorder": False})


@pytest.mark.parametrize(['x', 'y', 'expected'], [
    pytest.param([0, 1], [0, 1], 0.5),
    pytest.param([1, 0], [0, 1], 0.5),
    pytest.param([1, 0, 0], [0, 1, 1], 0.5),
    pytest.param([0, 1], [1, 1], 1),
    pytest.param([0, 0.5, 1], [0, 0.5, 1], 0.5),
])
def test_auc(x, y, expected):
    # Test Area Under Curve (AUC) computation
    assert auc(tensor(x), tensor(y)) == expected
