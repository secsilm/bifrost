# GPU 监视器

使用网页持续查看 GPU 使用情况。

## 特性

- 使用网页持续查看 GPU 使用情况
- 可设置时间间隔

## 实现步骤

初步想法，主要依赖 [pynvml](https://pypi.org/project/nvidia-ml-py3/) 来获取 GPU 信息，使用 flask 或者 dash 显示网页。

1. 使用 pynvml 获取 GPU 信息（已用、剩余和总共等信息）
2. 前端使用柱形图等图表展示获取到的信息