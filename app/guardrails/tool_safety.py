def validate_tool_inputs(tool_name: str, inputs: dict):
    # Tool safety: read-only by default, validated inputs.
    if tool_name == "tuition":
        if "major" not in inputs:
            return False
    elif tool_name == "scholarship":
        if "type" not in inputs:
            return False
    return True
