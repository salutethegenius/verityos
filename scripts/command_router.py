

# Command router for VerityOS CLI and chat mode
from scripts.agent_module import handle_agent_commands, get_agent_report
from scripts.task_module import handle_task_commands
from scripts.agenda_module import handle_agenda_commands
from scripts.log_module import handle_log_commands
from scripts.memory_core_module import handle_memory_core_commands
from scripts.sop_module import handle_sop_commands
from scripts.builder_module import parse_command as builder_parse_command

def route_command(user_input: str, config: dict):
    """
    Dispatches user_input to the appropriate command handler.
    Returns the handler's response or None if unrecognized.
    """
    # Builder commands
    if user_input.startswith(".generate agent "):
        return builder_parse_command(user_input)
    
    # Core command handlers
    for handler in [
        handle_agent_commands,
        handle_task_commands,
        handle_agenda_commands,
        handle_log_commands,
        handle_memory_core_commands,
        handle_sop_commands
    ]:
        # memory handler does not require config param
        if handler is handle_memory_core_commands:
            result = handler(user_input)
        else:
            result = handler(user_input, config)
        if result is not None:
            return result

    # Built-in commands
    if user_input == ".help":
        from scripts.boot import get_help
        return get_help()
    if user_input == ".status":
        from scripts.boot import get_system_report
        return get_system_report()
    if user_input == ".agents":
        return get_agent_report(config)
    if user_input in (".exit",):
        return "exit"
    if user_input == ".chatmode on":
        return "chatmode_on"
    if user_input == ".chatmode off":
        return "chatmode_off"
    
    return None