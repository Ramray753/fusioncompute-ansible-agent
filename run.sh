#!/bin/bash

# ==============================================================================
# UNIVERSAL DYNAMIC ENVIRONMENT EXECUTION GATEWAY
# ==============================================================================

# Determine the script's absolute runtime directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Dynamically resolve the active Python binary from the current shell PATH
# This mechanism natively respects activated Conda envs, venvs, or system globals
if command -v python &> /dev/null; then
    PYTHON_CMD="python"
elif command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
else
    echo "[FATAL ERROR] No accessible Python interpreter discovered in the current PATH."
    echo "Please activate your virtual environment (Conda/venv) or install Python first."
    exit 1
fi

# Execute the core production crew controller
# Seamlessly forwards all incoming command-line pipeline parameters
# Exmaple 1: 编写一个Ansible Playbook，用户指定一个虚拟机名称，查询虚拟机的详细信息，输出这个虚拟机每个磁盘所属的数据存储的名称，打印在控制台上。
# Exmaple 2: 编写一个Ansible Playbook，用户指定一个虚拟机名称，查询到ID和操作系统类型。如果这个虚拟机类型为Linux，通过API接口"给虚拟机上传自定义脚本"上传自定义脚本，脚本内容为"hostname"；如果这个虚拟机类型为Windows，通过API接口<给虚拟机上传自定义脚本>上传自定义脚本，脚本内容为"Get-ComputerInfo"。等待任务执行结束后，打印执行结果。
# Exmaple 3: 编写一个Ansible Playbook，用户指定一个CSV文件路径（./vm_names.csv），这个文件中的每一行代表一个虚拟机名称，没有表头。对于每个虚拟机名称，并行执行以下操作（并行度修改为5）：查询虚拟机详细信息（如果虚拟机名称对应多个ID则仅考虑第一个），从详细信息中获取Tools的运行状态和版本，并将结果汇总到./vm_tools.csv。汇总文件为CSV文件，有表头，包含4列：虚拟机名，ID，Tools状态，Tools版本。
# Exmaple 4: 编写一个Ansible Playbook，用户指定两个CSV文件路径（./host_names.csv和./datastore_names.csv），这两个CSV文件没有表头，host_names.csv代表主机名称列表，每一行都是一个主机名称；datastore_names.csv表示已经创建成功的数据存储名称列表，每一行都是一个数据存储名称。对于每个数据存储存储，先获取数据存储的基本信息，再遍历每一个主机，通过API<创建数据存储>完成主机关联数据存储操作。虽然这个接口名称是<创建数据存储>，但是也可以用来关联已经存在数据存储和新的主机，必须参数保持和这个数据存储的基本信息一致。必须顺序执行，严禁并行执行。
"$PYTHON_CMD" crew_task.py "$@"