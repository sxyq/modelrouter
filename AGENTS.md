# RTX A6000 服务器服务概况

> 本文件记录服务器 `k3s-infra-01`（RTX A6000）的基本硬件与已有服务现状。

---

## 1. 连接信息

| 项           | 值                                      |
| ----------- | -------------------------------------- |
| 别名          | `a6000`（配置于 `~/.ssh/config`）           |
| Host        | `10.16.15.202`                         |
| User / Port | `syy` / 22                             |
| 主机名         | `k3s-infra-01`                         |
| 认证方式      | 密钥认证                                |
| 私钥路径      | `~/.ssh/id_ed25519_remote_server`      |

---

## 2. 硬件配置

| 项      | 值                                 |
| ------ | --------------------------------- |
| GPU    | 1× NVIDIA RTX A6000（49140 MiB 显存） |
| CPU    | 80 核                              |
| RAM    | 376 GiB（可用约 346 GiB）          |
| 磁盘 `/` | NVMe 3.5T（已用约 64%，剩余约 1.2T） |

---

## 3. 已有服务与端口状态

|    端口 | 服务名称                             | 当前状态       | 说明 |
| ----: | ----------------------------------- | ------------- | --- |
| 11434 | Ollama GPU 网关                      | 运行中         | 对外服务入口，转发至本地回环 11435 |
| 11435 | Ollama backend                      | 运行中         | 本地回环后端 |
|  8010 | Zrald 文本服务                       | 运行中         | 基于 llama.cpp 的文本推理端点 |
|  8011 | Image API                           | 运行中         | 图像推理 API |
|  8020 | Image WebUI                         | 运行中         | 图像服务前端界面 |
|  3000 | Open WebUI                          | 运行中         | 对话前端界面 |
|  8000 | vLLM                                | 未运行         | 推理服务端口 |

---

## 4. 服务状态核验命令

```bash
# 硬件与 GPU 状态
nvidia-smi --query-gpu=index,name,memory.total,memory.used,utilization.gpu --format=csv

# 已有服务端口响应核验
for p in 8010 8011 8020 3000 8000; do
  curl -s -o /dev/null -w ":$p %{http_code}\n" --max-time 3 http://127.0.0.1:$p/health
done

# Ollama 服务状态
curl -s http://127.0.0.1:11434/api/tags
```
