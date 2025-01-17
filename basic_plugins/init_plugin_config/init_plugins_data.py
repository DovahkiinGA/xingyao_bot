
from ruamel.yaml import YAML
from utils.manager import plugins_manager
from utils.utils import get_matchers
from services.log import logger

try:
    import ujson as json
except ModuleNotFoundError:
    import json


_yaml = YAML(typ="safe")


def init_plugins_data(data_path):
    """
    初始化插件数据信息
    """
    plugin2data_file = data_path / "manager" / "plugin_manager.json"
    plugin2data_file.parent.mkdir(parents=True, exist_ok=True)
    _data = {}
    if plugin2data_file.exists():
        _data = json.load(open(plugin2data_file, "r", encoding="utf8"))
    _matchers = get_matchers(True)
    for matcher in _matchers:
        _plugin = matcher.plugin
        if not _plugin:
            continue
        metadata = _plugin.metadata
        try:
            _module = _plugin.module
        except AttributeError:
            if matcher.plugin_name not in _data.keys():
                plugins_manager.add_plugin_data(
                    matcher.plugin_name, matcher.plugin_name, error=True
                )
            else:
                plugins_manager.set_module_data(matcher.plugin_name, "error", True)
                plugin_data = plugins_manager.get(matcher.plugin_name)
                if plugin_data:
                    plugins_manager.set_module_data(
                        matcher.plugin_name, "version", plugin_data.get("version")
                    )
        else:
            try:
                plugin_version = None
                if metadata:
                    plugin_version = metadata.extra.get("version")
                if not plugin_version:
                    try:
                        plugin_version = _module.__getattribute__("__plugin_version__")
                    except AttributeError:
                        pass
                if metadata:
                    plugin_name = metadata.name
                else:
                    try:
                        plugin_name = _module.__getattribute__("__zx_plugin_name__")
                    except AttributeError:
                        plugin_name = matcher.plugin_name
                plugin_author = None
                if metadata:
                    plugin_author = metadata.extra.get('author')
                try:
                    plugin_author = _module.__getattribute__("__plugin_author__")
                except AttributeError:
                    pass
                if matcher.plugin_name in plugins_manager.keys():
                    plugins_manager.set_module_data(matcher.plugin_name, "error", False)
                if matcher.plugin_name not in plugins_manager.keys():
                    plugins_manager.add_plugin_data(
                        matcher.plugin_name,
                        plugin_name=plugin_name,
                        author=plugin_author,
                        version=plugin_version,
                    )
                    # metadata不检测version
                elif isinstance(plugin_version, str) or plugins_manager[matcher.plugin_name]["version"] is None or (
                    plugin_version is not None
                    and plugin_version > float(plugins_manager[matcher.plugin_name]["version"])
                ):
                    plugins_manager.set_module_data(
                        matcher.plugin_name, "plugin_name", plugin_name
                    )
                    plugins_manager.set_module_data(matcher.plugin_name, "author", plugin_author)
                    plugins_manager.set_module_data(
                        matcher.plugin_name, "version", plugin_version
                    )
                if matcher.plugin_name in _data.keys():
                    plugins_manager.set_module_data(
                        matcher.plugin_name, "error", _data[matcher.plugin_name]["error"]
                    )
                    plugins_manager.set_module_data(
                        matcher.plugin_name, "plugin_name", _data[matcher.plugin_name]["plugin_name"]
                    )
            except Exception as e:
                logger.error(f"插件数据 {matcher.plugin_name} 加载发生错误 {type(e)}：{e}")
    plugins_manager.save()
