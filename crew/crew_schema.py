from pydantic import BaseModel, Field
from typing import List, Optional, Union, Literal, Annotated

# ==============================================================================
# BASE TASK MODEL
# ==============================================================================
class BuiltInTask(BaseModel):
    """
    Base model for standard built-in Ansible tasks or non-API related tasks.
    """
    task_number: str = Field(
        description="Sequential identifier for the task (e.g., '[Task 1.1]')."
    )
    task_name: str = Field(
        description="A descriptive name for the task."
    )
    task_object: str = Field(
        description="The underlying business purpose or objective of this task."
    )
    task_type: Literal["builtin"] = Field(
        default="builtin",
        description="Set to 'builtin' if the task uses standard Ansible modules (e.g., debug, set_fact, file)."
    )
    module_name: str = Field(
        description="The precise Ansible module to execute (e.g., 'fc_generic', 'debug', 'copy')."
    )
    file_name: str = Field(
        description="The exact target YAML file where this task belongs (e.g., 'main.yml', 'stop_single_vm.yml')."
    )

# ==============================================================================
# FUSIONCOMPUTE SPECIFIC TASK MODEL
# ==============================================================================
class FusionComputeTask(BuiltInTask):
    """
    Extended model specifically for tasks calling the FusionCompute REST API 
    via the fc_generic module.
    """
    task_type: Literal["fusioncompute"] = Field(
        default="fusioncompute",
        description="Set to 'fusioncompute' if the task calls the FusionCompute API via the 'fc_generic' or 'fc_token_manager' module."
    )
    api_chinese_name: str = Field(
        description="The EXACT literal Chinese section name extracted from the API index."
    )
    required_params: Optional[List[str]] = Field(
        default_factory=list,
        description="A list of high-level descriptions of parameters the coder must extract and provide."
    )
    register_params: Optional[List[str]] = Field(
        default_factory=list,
        description="A list of high-level descriptions of variables to save/register from the API response for downstream tasks."
    )

# ==============================================================================
# SUPPLEMENTARY SCRIPT MODEL
# ==============================================================================
class SupplementaryScript(BaseModel):
    """
    Model for defining isolated Python scripts needed for complex data processing.
    """
    script_type: str = Field(
        default="py",
        description="The file extension type of the script."
    )
    script_name: str = Field(
        description="The exact name of the script file to be generated."
    )
    script_object: str = Field(
        description="The underlying business purpose or objective of this script."
    )

# ==============================================================================
# MASTER BLUEPRINT SCHEMA (PIPELINE HANDSHAKE)
# ==============================================================================
class BlueprintSchema(BaseModel):
    """
    The strict master output schema that the Automation Architect MUST adhere to.
    """
    filtered_apis_chinese_names: List[str] = Field(
        description="A list of exact Chinese REST API headings required for the workflow."
    )
    workflow_design: List[Annotated[Union[FusionComputeTask, BuiltInTask], Field(discriminator='task_type')]] = Field(
        description="A list of task objects defining the execution layout. Use the 'task_type' discriminator correctly."
    )
    supplementary_script_purpose: Optional[List[SupplementaryScript]] = Field(
        default_factory=list,
        description="A list of definitions for any isolated Python scripts needed for complex data processing."
    )

# ==============================================================================
# REVIEW & REMEDIATION SCHEMA (AGENT 3 -> AGENT 2 HANDSHAKE)
# ==============================================================================
class TaskReview(BaseModel):
    """
    Feedback model for a specific Ansible task that failed semantic/logic validation.
    """
    task_number: str = Field(description="The exact task_number from the original blueprint (e.g., '[Task 1.1]').")
    task_name: str = Field(description="The descriptive name of the task being reviewed.")
    file_name: str = Field(description="The exact YAML file where this task is located.")
    review_comment: str = Field(
        description="Detailed, actionable instructions on what is wrong and exactly how the Code Engineer must fix it (e.g., missing mandatory API parameters, wrong JSON payload structure, incorrect variable referencing)."
    )

class SupplementaryScriptReview(BaseModel):
    """
    Feedback model for a specific supplementary Python script that failed validation.
    """
    file_name: str = Field(description="The exact name of the Python script being reviewed.")
    review_comment: str = Field(
        description="Detailed, actionable instructions on what logic is missing or incorrect in the script."
    )

class ReviewSchema(BaseModel):
    """
    The strict master output schema for the Code Reviewer's semantic audit.
    If the codebase passes all validations perfectly, both lists MUST remain completely empty.
    """
    ansible_task_review_list: List[TaskReview] = Field(
        default_factory=list,
        description="List of tasks that contain semantic or logical errors. LEAVE EMPTY IF NO ERRORS ARE FOUND."
    )
    supplementary_script_review_list: List[SupplementaryScriptReview] = Field(
        default_factory=list,
        description="List of supplementary scripts that contain errors. LEAVE EMPTY IF NO ERRORS ARE FOUND."
    )