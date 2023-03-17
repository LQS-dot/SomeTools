#!/opt/venv/bin/python

import json
import argparse
from pathlib import Path
from ruamel.yaml import YAML
from typing import Dict
from dataclasses import dataclass

WriteFlag = True


@dataclass(order=True)
class OriginArgs:
    conf_path: str = "/opt/nfa/nta/etc/nta/af-packet.yaml"
    conf_path_bak: str = "/opt/nfa/nta/etc/nta/af-packet.yaml.bak"


class YamlParse(object):
    """
    yaml methods:
    This method provides the processing of yml files
    """

    def __init__(self, yml_path: str):
        self._yml_path = Path(yml_path)
        self._yml_obj = YAML(typ="rt")

    def __enter__(self) -> Dict[str, any]:
        self.conf = self._yml_obj.load(self._yml_path)
        return self.conf

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        """
        dump(conf,path_obj)
          conf: file content
          path_obj: object with .write method or Path.pathlib()
        """
        if WriteFlag:
            self._yml_obj.dump(self.conf, self._yml_path)


class YamlConfig(object):
    """
    Yaml Interfaces:
      - _Print : print groups content
      - _ModifyAdd : modify or add member for groups name
      - _Delete : delete member or group
    """

    FuncMap = {
        "p": "_Print",
        "m": "_ModifyAdd",
        "d": "_Delete",
        "infa": "InfaInterfaces",
    }

    def __init__(self, conf: str, group_name, key=None, value=None):
        self.conf = conf
        self.group_name = group_name
        self.key = key
        self.value = value

    @staticmethod
    def islist(args):
        if isinstance(args, list):
            return True
        else:
            return False

    def _Print(self) -> str:
        global WriteFlag
        WriteFlag = False
        with YamlParse(self.conf) as cfg:
            if self.islist(cfg[self.group_name]):
                group_name_json = json.dumps(cfg[self.group_name][0])
            else:
                group_name_json = json.dumps(cfg[self.group_name])
            print(group_name_json)

    def _ModifyAdd(self) -> None:
        """
        if the group name exists, for the input key value,modify it or add it
        if the group name not exists, add group name and key value
        group_name: yaml group name
        """
        with YamlParse(self.conf) as cfg:
            if cfg.get(self.group_name):
                # "-" before of key, print list or dict
                if self.islist(cfg[self.group_name]):
                    cfg[self.group_name][0][self.key] = self.value
                else:
                    # modify group name
                    if self.value and self.key is None:
                        cfg[self.group_name] = self.value
                    else:
                        cfg[self.group_name][self.key] = self.value
            else:
                cfg[self.group_name] = {self.key: self.value}

    def _Delete(self):
        """
        group_name:
          delete all group
        group_name,key:
          delete key with group
        """
        with YamlParse(self.conf) as cfg:
            if self.islist(cfg[self.group_name]):
                if self.key:
                    del cfg[self.group_name][0][self.key]
                else:
                    del cfg[self.group_name][0]
            else:
                if self.key:
                    del cfg[self.group_name][self.key]
                else:
                    del cfg[self.group_name]
            # for infa
            cfg["af-packet"] = None

    def InfaInterfaces(self, inter_list: list):
        self._Delete()
        cluster_id = 88
        origin_list = list()

        with YamlParse(self.conf) as cfg:
            for inter in inter_list:
                origin_list.append({"interface": inter,"threads": 8,"cluster-id": cluster_id, "cluster-type": "cluster_flow", "defrag": True, "use-mmap": True, "ring-size": 81920, "block-size": 32768})
                cluster_id += 1
            cfg["af-packet"] = origin_list


# keep original file
def original_file():
    if not Path(OriginArgs.conf_path_bak).exists():
        origin_path = Path(OriginArgs.conf_path)
        new_path = Path(OriginArgs.conf_path_bak)
        new_path.write_text(origin_path.read_text(encoding="utf-8"), encoding="utf-8")

# input args
def args_parser():
    parser = argparse.ArgumentParser(description="make for yaml")
    parser.add_argument("-i", "--interface", nargs='*',type=str , help="all intsrface names,segmentation with space")
    parser.add_argument("-f", "--file",type=str , help="yaml file")
    parser.add_argument("-g", "--group",type=str , help="group name for yaml")
    parser.add_argument("-k", "--key",type=str , help="the key of the element in the group")
    parser.add_argument("-v", "--value",type=str , help="if key is None and value is not None, modify key of the group")
    args = parser.parse_args()
    return args

# main
def init_args(args):
    yaml_file = args.file if args.file else "/opt/nfa/nta/etc/nta/af-packet.yaml"
    gname = args.group if args.group else "af-packet"
    return yaml_file,gname

def run():
    original_file()
    args = args_parser()
    yaml_file,gname = init_args(args)

    yaml_config = YamlConfig(yaml_file, gname, args.key, args.value)
    if args.interface:
        getattr(yaml_config, yaml_config.FuncMap['d'])()
        getattr(yaml_config, yaml_config.FuncMap['infa'])(args.interface)
    elif args.file:
        getattr(yaml_config, yaml_config.FuncMap['m'])()

run()
