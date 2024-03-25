"""
@Desc: 全局配置文件读取
"""
import argparse
import yaml
from typing import Dict, List
import os
import shutil
import sys

class Bert_gen_config:

    """bert_gen 配置"""

    def __init__(
        self,
        config_path: str,
        num_processes: int = 2,
        device: str = "cuda",
        use_multi_device: bool = False,
    ):
        self.config_path = config_path
        self.num_processes = num_processes
        self.device = device
        self.use_multi_device = use_multi_device

    @classmethod
    def from_dict(cls, dataset_path: str, data: Dict[str, any]):
        data["config_path"] = os.path.join(dataset_path, data["config_path"])

        return cls(**data)


class Emo_gen_config:
    """emo_gen 配置"""

    def __init__(
        self,
        config_path: str,
        num_processes: int = 2,
        device: str = "cuda",
    ):
        self.config_path = config_path
        self.num_processes = num_processes
        self.device = device

    @classmethod
    def from_dict(cls, dataset_path: str, data: Dict[str, any]):
        data["config_path"] = os.path.join(dataset_path, data["config_path"])

        return cls(**data)



class Webui_config:
    """webui 配置"""

    def __init__(
        self,
        device: str,
        model: str,
        config_path: str,
        language_identification_library: str,
        port: int = 7860,
        share: bool = False,
        debug: bool = False,
    ):
        self.device: str = device
        self.model: str = model  # 端口号
        self.config_path: str = config_path  # 是否公开部署，对外网开放
        self.port: int = port  # 是否开启debug模式
        self.share: bool = share  # 模型路径
        self.debug: bool = debug  # 配置文件路径
        self.language_identification_library: str = (
            language_identification_library  # 语种识别库
        )

    @classmethod
    def from_dict(cls, dataset_path: str, data: Dict[str, any]):
        data["config_path"] = os.path.join(dataset_path, data["config_path"])
        data["model"] = os.path.join(dataset_path, data["model"])
        return cls(**data)


class Server_config:
    def __init__(
        self, models: List[Dict[str, any]], port: int = 5000, device: str = "cuda"
    ):
        self.models: List[Dict[str, any]] = models  # 需要加载的所有模型的配置
        self.port: int = port  # 端口号
        self.device: str = device  # 模型默认使用设备

    @classmethod
    def from_dict(cls, data: Dict[str, any]):
        return cls(**data)



class Config:
    def __init__(self, config_path: str):
        with open(file=config_path, mode="r", encoding="utf-8") as file:
            yaml_config: Dict[str, any] = yaml.safe_load(file.read())
            dataset_path: str = yaml_config["dataset_path"]
            openi_token: str = yaml_config["openi_token"]
            self.dataset_path: str = dataset_path
            self.mirror: str = yaml_config["mirror"]
            self.openi_token: str = openi_token
            self.bert_gen_config: Bert_gen_config = Bert_gen_config.from_dict(
                dataset_path, yaml_config["bert_gen"]
            )
            self.webui_config: Webui_config = Webui_config.from_dict(
                dataset_path, yaml_config["webui"]
            )


parser = argparse.ArgumentParser()
# 为避免与以前的config.json起冲突，将其更名如下
parser.add_argument("-y", "--yml_config", type=str, default="../localtts/config.yml")
args, _ = parser.parse_known_args()
config = Config(args.yml_config)