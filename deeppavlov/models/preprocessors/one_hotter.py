# Copyright 2017 Neural Networks and Deep Learning lab, MIPT
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

from typing import List, Union
import numpy as np

from deeppavlov.core.common.errors import ConfigError
from deeppavlov.core.models.component import Component
from deeppavlov.core.common.registry import register
from deeppavlov.core.data.utils import zero_pad


@register('one_hotter')
class OneHotter(Component):
    """
    One-hot featurizer with zero-padding.
    If ``multi_label``, return the only vector per sample which can have several elements equal to ``1``.

    Parameters:
        depth: the depth for one-hotting
        pad_zeros: whether to pad elements of batch with zeros
        multi_label: whether to return one vector for the sample (sum of each one-hotted vectors)
    """
    def __init__(self, depth: int, pad_zeros: bool = False,
                 multi_label=False, *args, **kwargs):
        self._depth = depth
        self._pad_zeros = pad_zeros
        self._multi_label = multi_label
        if self._pad_zeros and self._multi_label:
            raise ConfigError("Cannot perform multi-labelling with zero padding for OneHotter")

    def __call__(self, batch: List[List[int]], **kwargs) -> Union[List[List[np.ndarray]], List[np.ndarray]]:
        """
        Convert given batch of list of labels to one-hot representation of the batch.

        Args:
            batch: list of samples, where each sample is a list of integer labels.
            **kwargs: additional arguments

        Returns:
            if ``multi_label``, list of one-hot representations of each sample,
            otherwise, list of lists of one-hot representations of each label in a sample
        """
        one_hotted_batch = []

        for utt in batch:
            if isinstance(utt, list):
                one_hotted_utt = self._to_one_hot(utt, self._depth)
            elif isinstance(utt, int):
                if self._pad_zeros or self._multi_label:
                    one_hotted_utt = self._to_one_hot([utt], self._depth)
                else:
                    one_hotted_utt = self._to_one_hot([utt], self._depth).reshape(-1)

            if self._multi_label:
                one_hotted_utt = np.sum(one_hotted_utt, axis=0)

            one_hotted_batch.append(one_hotted_utt)

        if self._pad_zeros:
            one_hotted_batch = zero_pad(one_hotted_batch)
        return one_hotted_batch

    @staticmethod
    def _to_one_hot(x, n):
        b = np.zeros([len(x), n], dtype=np.float32)
        for q, tok in enumerate(x):
            b[q, tok] = 1
        return b
