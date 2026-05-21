"""
Data Rules
Rules for BPMN Data Objects and Data Stores
"""


class DataRules:
    """Rules for BPMN Data Objects and Data Stores"""
    
    DATA_OBJECT_USAGE = (
        "Data Objects represent information flowing through the process. "
        "They should be associated with tasks that create, read, update, or delete them."
    )
    
    DATA_STORE_PERSISTENCE = (
        "Data Stores represent persistent data storage. "
        "They can be accessed by multiple tasks and persist beyond a single process instance."
    )

