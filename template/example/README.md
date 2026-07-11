# FusionCompute 自动化管理框架说明

本样例采用模块化设计以实现环境解耦和逻辑复用，这些文件共同构成了一套完整的华为 FusionCompute 自动化管理框架，所有文件放在同一目录下。

以下是各文件的功能职责简要描述：

## 1. 全局配置
- **`commons.yml`**: 全局基础设施配置。存放连接信息（IP、账号、密码）、系统超时阈值及并发控制参数，确保各 playbook 可以在不同环境间轻松切换。

## 2. 自动化执行入口
- **`main_single_call.yml`**: 单次操作演示。展示了从登录验证、资源搜索（获取 URN/ID）到执行单次 VM 克隆操作的完整“发现-操作”标准工作流。
- **`main_batch_sequential.yml`**: 顺序批量操作。通过读取 CSV 文件，循环执行资源停机操作。适用于对顺序有严格要求、对性能有顾虑或资源规模较小的场景。注意：当且仅当有顺序批量操作时才需要读取该文件。
- **`main_batch_parallel.yml`**: 并发批量操作。通过读取 CSV 文件，动态添加主机（add_host）并结合 serial 参数，实现了大规模并行任务的受控并发，显著提升了大规模运维的执行效率。适用于对顺序无要求、不担心系统性能或资源规模较大的场景。注意：当且仅当有并发批量操作时才需要读取该文件。

## 3. 异步任务跟踪
- **`wait_fc_system_task.yml`**: 异步任务跟踪模块，该文件对fc_task_manager做了封装。注意：禁止读取和理解该文件，禁止修改文件中的任何内容，直接参考样例脚本调用即可。

## 4. 批执行脚本业务逻辑
- **`stop_single_vm.yml`**: 文件被`main_batch_sequential.yml`调用，作为每台 VM 执行安全关机操作的具体逻辑，负责精准匹配 VM 名称、提取 ID 并发送启动 API 指令。
- **`start_single_vm.yml`**: 文件用于`main_batch_parallel.yml`调用，作为每台 VM 执行开机操作的具体逻辑，负责精准匹配 VM 名称、提取 ID 并发送启动 API 指令。

## 5. 数据源
- **`vm_names_stop.csv`**: 批量关机操作 VM 名称清单，作为脚本 `main_batch_sequential.yml` 的数据输入源。
- **`vm_names_start.csv`**: 批量开机操作 VM 名称清单，作为脚本 `main_batch_parallel.yml` 的数据输入源。