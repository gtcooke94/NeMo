# Copyright (c) 2020, NVIDIA CORPORATION.  All rights reserved.
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

from dataclasses import dataclass
from typing import Any, List, Optional

import pytorch_lightning as ptl
from omegaconf import MISSING, DictConfig, OmegaConf

from nemo.collections.vis.datasets import CLEVRConfig
from nemo.collections.vis.models import QType, QTypeConfig
from nemo.core.config import AdamConfig, DataLoaderConfig, TrainerConfig, hydra_runner
from nemo.utils import logging


@dataclass
class AppConfig:
    """
    This is structured config for this application.
    Args:
        trainer: configuration of the trainer.
        model: configuation of the model.
    """

    model: QTypeConfig = QTypeConfig()
    dataloader: DataLoaderConfig = DataLoaderConfig()
    # text_transforms: Optional[Any] = None  # List[Any] = field(default_factory=list) ?
    train_dataset: CLEVRConfig = CLEVRConfig()
    optim: AdamConfig = AdamConfig()
    trainer: TrainerConfig = TrainerConfig()


# Load configuration file from "conf" dir using schema for validation/retrieving the default values.
@hydra_runner(config_path="conf", config_name="clevr_qtype_training", schema=AppConfig)
def main(cfg: AppConfig):
    # Show configuration.
    logging.info("Application settings\n" + OmegaConf.to_yaml(cfg))

    # Instantiate the "model".
    model = QType(cfg.model)

    # tokens = model(["Ala ma,  kota.", "kot ma pałę"])
    # tokens = model(['Are there any other things that are the same shape as the big metallic object?', 'Is there a big brown object of the same shape as the green thing?'])
    # print(tokens)

    # Instantiate the dataloader/dataset.
    train_dl = model.instantiate_dataloader(cfg.dataloader, cfg.train_dataset)
    # batch = next(iter(train_dl))
    # print(batch)
    # tokens = model(batch[3])
    # print(tokens)

    # Setup the optimization.
    model.setup_optimization(cfg.optim)

    # Create the trainer.
    trainer = ptl.Trainer(**(cfg.trainer))

    # Train the model on dataset.
    trainer.fit(model=model, train_dataloader=train_dl)


if __name__ == "__main__":
    main()