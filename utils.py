from collections import namedtuple
from pprint import pprint
import time

import psutil
import pynvml

pynvml.nvmlInit()

def get_infos():
    """获取所有显卡的信息。
    """

    infos = {}
    Device = namedtuple(
        "Device",
        [
            "id",
            "name",
            "free",
            "used",
            "total",
            "temperature",
            "fan_speed",
            "power_usage",
            "power_state",
            "process",
        ],
    )
    Process = namedtuple(
        "Process",
        [
            "pid",
            "memory_percent",
            "status",
            "username",
            "num_threads",
            "cpu_num",
            "cpu_percent",
            "name",
            "cmdline",
            "used_gpu_mem",
            "create_time",
        ],
    )
    driver_version = pynvml.nvmlSystemGetDriverVersion().decode()
    device_count = pynvml.nvmlDeviceGetCount()
    info = []
    for i in range(device_count):
        handle = pynvml.nvmlDeviceGetHandleByIndex(i)
        name = pynvml.nvmlDeviceGetName(handle).decode()
        mem_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
        power_usage = pynvml.nvmlDeviceGetPowerUsage(handle)  # 电源使用量，单位为毫瓦 mW
        processes = pynvml.nvmlDeviceGetComputeRunningProcesses(handle)  # 哪些进程在使用该 GPU
        # process_info = [(item.pid, item.usedGpuMemory) for item in process_info]
        process_info = []
        for p in processes:
            # append Process object to process_info
            pid = p.pid
            used_gpu_mem = p.usedGpuMemory
            p = psutil.Process(pid=pid)
            _ = p.cpu_percent()
            time.sleep(0.05)
            process_info.append(
                Process(
                    pid=pid,
                    memory_percent=p.memory_percent(),
                    status=p.status(),
                    username=p.username(),
                    num_threads=p.num_threads(),
                    cpu_num=p.cpu_num(),
                    cpu_percent=p.cpu_percent(),
                    name=p.name(),
                    cmdline=" ".join(p.cmdline()),
                    used_gpu_mem=used_gpu_mem,
                    create_time=p.create_time(),
                )
            )
        try:
            fan_speed = pynvml.nvmlDeviceGetFanSpeed(handle)
        except pynvml.NVMLError_NotSupported as e:
            fan_speed = None
        power_usage = pynvml.nvmlDeviceGetPowerUsage(handle)
        power_state = pynvml.nvmlDeviceGetPowerState(handle)
        temperature = pynvml.nvmlDeviceGetTemperature(
            handle, pynvml.NVML_TEMPERATURE_GPU
        )
        info.append(
            Device(
                id=i,
                name=name,
                free=mem_info.free,
                used=mem_info.used,
                total=mem_info.total,
                temperature=temperature,
                fan_speed=fan_speed,
                power_usage=power_usage,
                power_state=power_state,
                process=process_info,
            )
        )

    infos["count"] = device_count
    infos["driver_version"] = driver_version
    infos["info"] = info
    return infos


if __name__ == "__main__":
    infos = get_infos()
    pprint(infos, indent=4)
