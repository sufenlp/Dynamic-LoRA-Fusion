# coding=utf-8
# Copyright 2022 The OpenBMB team.
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

import torch
import bmtrain as bmt
import math
import torch.nn.functional as F

class Linear(bmt.DistributedModule):
    r"""A fully connected layer, which performs :math:`\pmb{y} = \mathbf{W} \pmb{x} + \pmb{b}`

    Args:
        dim_in (int): input dimension of :math:`\pmb{x}`
        dim_out (int): output dimension of :math:`\pmb{y}`
        dtype (optional): Defaults to torch.half.
        init_mean (float, optional): mean of :math:`\mathbf{W}\sim\mathcal{N}(\text{mean}, \text{std}^2)`. Defaults to 0.
        init_std (float, optional): std of :math:`\mathbf{W}\sim\mathcal{N}(\text{mean}, \text{std}^2)`. Defaults to 1.
        bias (bool, optional): whether to add bias term :math:`\pmb{b}`. Defaults to False.
    """
    def __init__(self,
                 dim_in : int,
                 dim_out : int,
                 length_scale : bool = False,
                 length_scale_before : bool = False,
                 dtype = torch.half,
                 int8 : bool = False,
                 init_mean : float = 0.0,
                 init_std : float = 1,
                 bias : bool = False,
                 cps: int = 0,
                ):
        super().__init__()
        self.dim_in = self.in_features = dim_in
        self.dim_out = self.out_features = dim_out
        if cps == 1: #init for lora_B
            self.weight = bmt.DistributedParameter(
                torch.empty((dim_out, dim_in), dtype=dtype),
                init_method=bmt.ParameterInitializer(torch.nn.init.zeros_),
            )
            self.bias = None
        elif cps == 2: #init for lora_A
            self.weight = bmt.DistributedParameter(
                torch.empty((dim_out, dim_in), dtype=dtype),
                init_method=bmt.ParameterInitializer(torch.nn.init.kaiming_uniform_, a=math.sqrt(5)),
            )
            self.bias = None
        else:
            # self.weight = bmt.DistributedParameter(
            #     torch.zeros((dim_out, dim_in), dtype=dtype),
            # )
            self.weight = bmt.DistributedParameter(
                torch.empty((dim_out, dim_in), dtype=dtype),
                init_method=bmt.ParameterInitializer(torch.nn.init.zeros_)
            )
            
            self.bias = None                        
            # self.bias = bmt.DistributedParameter(
            #     torch.empty((dim_out,), dtype=dtype),
            #     init_method=bmt.ParameterInitializer(torch.nn.init.zeros_)
            # ) if bias else None
        self.length_scale = length_scale
        self.length_scale_before = length_scale_before
        self.int8 = int8

    def forward(self, x : torch.Tensor):
        """ 
        Args:
            x (:obj:`torch.Tensor` of shape ``(batch, seq_len, dim_in)``): The input of linear layer

        Returns:
            :obj:`torch.Tensor` of shape ``(batch, seq_len, dim_out)``: The output of the linear transform y.

        """
        if self.length_scale and self.length_scale_before:
            x = x / math.sqrt(self.dim_in)
        x = F.linear(x, self.weight)
        if self.length_scale and not self.length_scale_before:
            x = x / math.sqrt(self.dim_in)
        if self.bias is not None:
            x = x + self.bias
        return x

# import torch.nn as nn
# class LowRankLinear(bmt.DistributedModule):
#     #  ------------------------------------------------------------------------------------------
#     #  Copyright (c) Microsoft Corporation. All rights reserved.
#     #  Licensed under the MIT License (MIT). See LICENSE in the repo root for license information.
#     #  ------------------------------------------------------------------------------------------
#     #  copy from loralib and do some refactor
#     def __init__(self,
#         in_features,
#         out_features,
#         r=8,
#         lora_alpha=16,
#         lora_dropout=0.0,
#     ):
#         super().__init__()
#         self.r = r
#         self.lora_alpha = lora_alpha
#         self.lora_dropout = lora_dropout
#         if lora_dropout > 0.:
#             self.lora_dropout = nn.Dropout(p=lora_dropout)
#         else:
#             self.lora_dropout = lambda x: x
#         if r > 0:
#             self.lora_A = Linear(dim_out = r, dim_in = in_features, cps = 2)
#             self.lora_B = Linear(dim_out = out_features, dim_in = r, cps = 1)
#             self.scaling = self.lora_alpha / self.r

#     def forward(self, x):
#         # import pdb
#         # pdb.set_trace()
#         return (self.lora_B(self.lora_A(self.lora_dropout(x)))) * self.scaling

# loras = nn.ModuleDict({})
# import pdb
# pdb.set_trace()
# loras['lora_1'] = LowRankLinear(in_features=768, out_features=768, r=64, lora_alpha=16, lora_dropout=0.1)