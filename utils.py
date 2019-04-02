import pynvml
from collections import namedtuple
from pprint import pprint
import psutil


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


    进程信息：pid、memory_percent、status、username、num_threads、cpu_num（该进程在哪个cpu上）、cpu_percent（该进程使用了多少cpu）、name、cmdline
    """

    infos = {}
    Device = namedtuple("Device", ["free", "used", "total", "temperature", "fan_speed"])
    Process = namedtuple("Process", ["pid". "memory_percent", "status", "username", "num_threads", "cpu_num", "cpu_percent", "name", "cmdline", "used_gpu_mem"])
    pynvml.nvmlInit()
    driver_version = pynvml.nvmlSystemGetDriverVersion().decode()
    device_count = pynvml.nvmlDeviceGetCount()
    info = {}
    for i in range(device_count):
        info[i] = {}
        handle = pynvml.nvmlDeviceGetHandleByIndex(i)
        mem_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
        power_usage = pynvml.nvmlDeviceGetPowerUsage(handle)  # 电源使用量，单位为毫瓦 mW
        processes = pynvml.nvmlDeviceGetComputeRunningProcesses(handle)  # 哪些进程在使用该 GPU
        process_info = [(item.pid, item.usedGpuMemory) for item in process_info]
        process_info = []
        for p in processes:
            # append Process object to process_info
            pass
        try:
            fan_speed = pynvml.nvmlDeviceGetFanSpeed(handle)
        except pynvml.NVMLError_NotSupported as e:
            fan_speed = None
        info[i]['free'] = mem_info.free
        info[i]['used'] = mem_info.used
        info[i]['total'] = mem_info.total
        info[i]['temperature'] = pynvml.nvmlDeviceGetTemperature(handle, pynvml.NVML_TEMPERATURE_GPU)
        info[i]['fan_speed'] = fan_speed

    infos["count"] = device_count
    infos["driver_version"] = driver_version
    infos["info"] = info
    return infos


if __name__ == "__main__":
    infos = get_infos()
    pprint(infos, indent=4)
