import pynvml
from collections import namedtuple
from pprint import pprint


def get_infos():
    """获取所有显卡的信息。

    {
        "count": 8,
        "driver_version": '419.17',
        "info": [
            {
                "0": 
                    {
                    "free": 1,
                    "used": 2,
                    "total": 3,
                    "temp": 36,
                    "fan_speed": 23,
                    "power_status": 8
                    }
            }
        ]
    }

    """

    infos = {}
    Device = namedtuple("Device", ["free", "used", "total", "temperature", "fan_speed"])
    pynvml.nvmlInit()
    driver_version = pynvml.nvmlSystemGetDriverVersion().decode()
    device_count = pynvml.nvmlDeviceGetCount()
    info = {}
    for i in range(device_count):
        info[i] = {}
        handle = pynvml.nvmlDeviceGetHandleByIndex(i)
        mem_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
        try:
            fan_speed = pynvml.nvmlDeviceGetFanSpeed(handle)
        except pynvml.NVMLError_NotSupported as e:
            fan_speed = None
        info[i]['free'] = mem_info.free
        info[i]['used'] = mem_info.used
        info[i]['total'] = mem_info.total
        info[i]['temperature'] = pynvml.nvmlDeviceGetTemperature(handle, 0)
        info[i]['fan_speed'] = fan_speed

    infos["count"] = device_count
    infos["driver_version"] = driver_version
    infos["info"] = info
    return infos


if __name__ == "__main__":
    infos = get_infos()
    pprint(infos, indent=4)
