<!--Copyright 2023 The HuggingFace Team. All rights reserved.

Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
the License. You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.

⚠️ Note that this file is in Markdown but contain specific syntax for our doc-builder (similar to MDX) that may not be
rendered properly in your Markdown viewer.

-->

# Troubleshooting

If you encounter any issue when using PEFT, please check the following list of common issues and their solutions.

## Examples don't work

Examples often rely on the most recent package versions, so please ensure they're up-to-date. In particular, check the version of the following packages:

- `peft`
- `transformers`
- `accelerate`
- `torch`

In general, you can update the package version by running this command inside your Python environment:

```bash
python -m pip install -U <package_name>
```

Installing PEFT from source is useful for keeping up with the latest developments:

```bash
python -m pip install git+https://github.com/huggingface/peft
```

## Training errors

### Getting: ValueError: Attempting to unscale FP16 gradients

This error probably occurred because the model was loaded with `torch_dtype=torch.float16` and then used in an automatic mixed precision (AMP) context, e.g. by setting `fp16=True` in the `Trainer` class from 🤗 Transformers. The reason is that when using AMP, trainable weights should never use fp16. To make this work without having to load the whole model in FP32, add the following snippet to your code:

```python
peft_model = get_peft_model(...)

# add this:
for param in model.parameters():
    if param.requires_grad:
        param.data = param.data.float()

# proceed as usual
trainer = Trainer(model=peft_model, fp16=True, ...)
trainer.train()
```

## Bad results from a loaded PEFT model

There can be several reasons for getting a poor result from a loaded PEFT model, which are listed below. If you're still unable to troubleshoot the problem, see if anyone else had a similar [issue](https://github.com/huggingface/peft/issues) on GitHub, and if you can't find any, open a new issue.

When opening an issue, it helps a lot if you provide a minimal code example that reproduces the issue. Also, please report if the loaded model performs at the same level as the model did before fine-tuning, if it performs at a random level, or if it is only slightly worse than expected. This information helps us identify the problem more quickly.

### Random deviations

If your model outputs are not exactly the same as previous runs, there could be an issue with random elements. For example:

1. please ensure it is in `.eval()` mode, which is important, for instance, if the model uses dropout
2. if you use [`~transformers.GenerationMixin.generate`] on a language model, there could be random sampling, so obtaining the same result requires setting a random seed
3. if you used quantization and merged the weights, small deviations are expected due to rounding errors

### Incorrectly loaded model

Please ensure that you load the model correctly. A common error is trying to load a _trained_ model with `get_peft_model`, which is incorrect. Instead, the loading code should look like this:

```python
from peft import PeftModel, PeftConfig

base_model = ...  # to load the base model, use the same code as when you trained it
config = PeftConfig.from_pretrained(peft_model_id)
peft_model = PeftModel.from_pretrained(base_model, peft_model_id)
```

### Randomly initialized layers

For some tasks, it is important to correctly configure `modules_to_save` in the config to account for randomly initialized layers. 

As an example, this is necessary if you use LoRA to fine-tune a language model for sequence classification because 🤗 Transformers adds a randomly initialized classification head on top of the model. If you do not add this layer to `modules_to_save`, the classification head won't be saved. The next time you load the model, you'll get a _different_ randomly initialized classification head, resulting in completely different results.

In PEFT, we try to correctly guess the `modules_to_save` if you provide the `task_type` argument in the config. This should work for transformers models that follow the standard naming scheme. It is always a good idea to double check though because we can't guarantee all models follow the naming scheme.

When you load a transformers model that has randomly initialized layers, you should see a warning along the lines of:

```
Some weights of <MODEL> were not initialized from the model checkpoint at <ID> and are newly initialized: [<LAYER_NAMES>].
You should probably TRAIN this model on a down-stream task to be able to use it for predictions and inference.
```

The mentioned layers should be added to `modules_to_save` in the config to avoid the described problem.
