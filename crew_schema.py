from pydantic import BaseModel, Field
from typing import List, Optional, Union, Literal, Annotated

# ==============================================================================
# BASE TASK MODEL
# ==============================================================================
class BuiltInTask(BaseModel):
    """
    Base model for standard built-in Ansible tasks or non-API related tasks.
    """
    task_number: str
    task_name: str
    task_object: str  # Task purpose/objective
    
    # Use Literal to help Pydantic distinguish between the base and child class later.
    task_type: Literal["builtin"] = "builtin" 
    module_name: str
    file_name: str

# ==============================================================================
# FUSIONCOMPUTE SPECIFIC TASK MODEL
# ==============================================================================
class FusionComputeTask(BuiltInTask):
    """
    Extended model specifically for tasks calling the FusionCompute REST API 
    via the fc_generic module.
    """
    task_type: Literal["fusioncompute"] = "fusioncompute"
    
    # Mandatory for fc_generic, must match the ChromaDB API index exactly
    api_chinese_name: str
    
    # High-level text description of required parameters to be extracted by the coder
    required_params: Optional[List[str]] = Field(default_factory=list)
    
    # High-level text description of what variable to register/save from the response
    register_params: Optional[List[str]] = Field(default_factory=list)

# ==============================================================================
# SUPPLEMENTARY SCRIPT MODEL
# ==============================================================================
class SupplementaryScript(BaseModel):
    """
    Model for defining isolated Python scripts needed for complex data processing.
    """
    script_type: str = Field(default="py")
    script_name: str
    script_object: str

# ==============================================================================
# MASTER BLUEPRINT SCHEMA (PIPELINE HANDSHAKE)
# ==============================================================================
class BlueprintSchema(BaseModel):
    """
    The strict master output schema that the Automation Architect MUST adhere to.
    This replaces the free-form Markdown text for cross-agent data handovers.
    """
    filtered_apis_chinese_names: List[str]
    
    # Use Union so Pydantic knows this list can contain both task types.
    # Field(discriminator='task_type') enforces strict object routing during instantiation.
    workflow_design: List[Annotated[Union[FusionComputeTask, BuiltInTask], Field(discriminator='task_type')]]
    
    supplementary_script_purpose: Optional[List[SupplementaryScript]] = Field(default_factory=list)