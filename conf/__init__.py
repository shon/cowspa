import copy
import default

class Config(dict):
    def __getattr__(self, attr):
        return self[attr]

def parse_config():
    config = Config(**copy.deepcopy(default.config))
    try:
        import conf_local
        local_config = conf_local.config
        for section in config:
            local_config_section = local_config.get(section)
            if local_config_section:
                config[section].update(local_config_section)
    except Exception, err:
        print err
        pass
    print config
    return config

