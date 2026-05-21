from typing import List, Optional
from .bpmn_spec import ALLOWED_TASK_TYPES, ALLOWED_GATEWAY_TYPES

class FlowObject:
    """Base class for all BPMN Flow Objects (Events, Activities, Gateways)"""
    def __init__(self, id: str, name: str):
        self.id = id
        self.name = name

class StartEvent(FlowObject):
    """BPMN Start Event - indicates where a process begins"""
    def __init__(self, id: str, name: str = "Start Event", event_type: str = "none"):
        super().__init__(id, name)
        self.event_type = event_type

class EndEvent(FlowObject):
    """BPMN End Event - indicates where a process terminates"""
    def __init__(self, id: str, name: str = "End Event", event_type: str = "none"):
        super().__init__(id, name)
        self.event_type = event_type

class Task(FlowObject):
    """BPMN Task - represents work to be performed
    
    Task types (BPMN 2.0):
    - abstract: Generic task
    - user: Human-performed task
    - service: Automated service task
    - manual: Physical task outside the system
    - script: Script execution task
    - send: Message sending task
    - receive: Message receiving task
    - business_rule: Business rules execution task
    """
    def __init__(self, id: str, name: str, task_type: str = "abstract"):
        super().__init__(id, name)
        self.task_type = task_type

class Gateway(FlowObject):
    """BPMN Gateway - controls divergence and convergence of sequence flows
    
    Gateway types (BPMN 2.0):
    - exclusive: XOR - only one path (default)
    - parallel: AND - all paths simultaneously
    - inclusive: OR - one or more paths
    - event_based: Decision based on events
    - complex: Complex decision logic
    """
    def __init__(self, id: str, name: str, gateway_type: str = "exclusive"):
        super().__init__(id, name)
        self.gateway_type = gateway_type

class IntermediateCatchEvent(FlowObject):
    """BPMN Intermediate Catch Event - waits for a trigger during process execution"""
    def __init__(self, id: str, name: str, event_type: str = "message"):
        super().__init__(id, name)
        self.event_type = event_type

class IntermediateThrowEvent(FlowObject):
    """BPMN Intermediate Throw Event - throws a trigger during process execution"""
    def __init__(self, id: str, name: str, event_type: str = "none"):
        super().__init__(id, name)
        self.event_type = event_type

class SequenceFlow:
    def __init__(self, source: FlowObject, target: FlowObject):
        self.source = source
        self.target = target

class DataObject:
    def __init__(self, id: str, name: str):
        self.id = id
        self.name = name

class DataStore:
    def __init__(self, id: str, name: str):
        self.id = id
        self.name = name

class Process:
    def __init__(self, name: str):
        self.name = name
        self.flow_objects: List[FlowObject] = []
        self.sequence_flows: List[SequenceFlow] = []
        self.data_objects: List[DataObject] = []
        self.data_stores: List[DataStore] = []

    def add(self, obj):
        if isinstance(obj, FlowObject):
            self.flow_objects.append(obj)
        elif isinstance(obj, SequenceFlow):
            self.sequence_flows.append(obj)
        elif isinstance(obj, DataObject):
            self.data_objects.append(obj)
        elif isinstance(obj, DataStore):
            self.data_stores.append(obj)
        else:
            print(f"Warning: Unknown object type {type(obj)} cannot be added to process.")

    def validate(self) -> bool:
        syntax_valid = self.validate_syntax()
        static_semantics_valid = self.validate_static_semantics()
        event_rules_valid = self.validate_event_rules()
        structural_rules_valid = self.validate_structural_rules()
        advanced_structural_rules_valid = self.validate_advanced_structural_rules()
        topological_rules_valid = self.validate_topological_rules()
        reachability_valid = self.validate_reachability()

        if (syntax_valid and static_semantics_valid and event_rules_valid and 
            structural_rules_valid and advanced_structural_rules_valid and 
            topological_rules_valid and reachability_valid):
            print("✅ Process is valid.")
            return True
        else:
            print("❌ Process validation failed.")
            return False

    def validate_syntax(self) -> bool:
        errors = []

        # 1. Check if there is exactly one Start Event
        start_events = [o for o in self.flow_objects if isinstance(o, StartEvent)]
        if len(start_events) != 1:
            errors.append(f"Syntax Error: Expected exactly 1 StartEvent, found {len(start_events)}.")

        # 2. Check if there is at least one End Event
        end_events = [o for o in self.flow_objects if isinstance(o, EndEvent)]
        if len(end_events) < 1:
            errors.append("Syntax Error: At least one EndEvent is required.")

        # 3. Check that each object is connected to at least one flow
        connected_ids = set()
        for flow in self.sequence_flows:
            connected_ids.add(flow.source.id)
            connected_ids.add(flow.target.id)

        for obj in self.flow_objects:
            if obj.id not in connected_ids:
                errors.append(f"Syntax Error: Object '{obj.name}' (ID: {obj.id}) is not connected.")
        
        # 4. Check for direct event-to-event flows (should have tasks/gateways between)
        for flow in self.sequence_flows:
            if (isinstance(flow.source, (StartEvent, EndEvent, IntermediateCatchEvent, IntermediateThrowEvent)) and
                isinstance(flow.target, (StartEvent, EndEvent, IntermediateCatchEvent, IntermediateThrowEvent))):
                errors.append(f"Syntax Error: Direct flow from event '{flow.source.name}' to event '{flow.target.name}' is not recommended. Insert a task or gateway between events.")

        if errors:
            print("❌ Syntax validation failed:")
            for e in errors:
                print("  -", e)
            return False
        else:
            print("✅ Syntax is valid.")
            return True

    def validate_event_rules(self) -> bool:
        """Validate event-specific rules"""
        errors = []
        
        # Rule: Start events should not have incoming flows
        for obj in self.flow_objects:
            if isinstance(obj, StartEvent):
                incoming = [f for f in self.sequence_flows if f.target.id == obj.id]
                if incoming:
                    errors.append(f"Event Rule Error: Start event '{obj.name}' has incoming flows. Start events should not have incoming flows.")
        
        # Rule: End events should not have outgoing flows
        for obj in self.flow_objects:
            if isinstance(obj, EndEvent):
                outgoing = [f for f in self.sequence_flows if f.source.id == obj.id]
                if outgoing:
                    errors.append(f"Event Rule Error: End event '{obj.name}' has outgoing flows. End events should not have outgoing flows.")
        
        # Rule: Intermediate events must have both incoming and outgoing flows
        for obj in self.flow_objects:
            if isinstance(obj, (IntermediateCatchEvent, IntermediateThrowEvent)):
                incoming = [f for f in self.sequence_flows if f.target.id == obj.id]
                outgoing = [f for f in self.sequence_flows if f.source.id == obj.id]
                if not incoming:
                    errors.append(f"Event Rule Error: Intermediate event '{obj.name}' has no incoming flows. Intermediate events must have both incoming and outgoing flows.")
                if not outgoing:
                    errors.append(f"Event Rule Error: Intermediate event '{obj.name}' has no outgoing flows. Intermediate events must have both incoming and outgoing flows.")
        
        if errors:
            print("❌ Event rules validation failed:")
            for e in errors:
                print("  -", e)
            return False
        else:
            print("✅ Event rules are valid.")
            return True

    def validate_structural_rules(self) -> bool:
        errors = []
        task_sequences = self._get_task_sequences()

        # Rule: No more than four tasks in a row
        for sequence in task_sequences:
            if len(sequence) > 4:
                errors.append(f"Structural Rule Error: Found a sequence of {len(sequence)} tasks, which exceeds the maximum of 4.")

        # Rule: No consecutive service tasks and mandatory error handling for scripts
        for i, flow in enumerate(self.sequence_flows):
            source_task = flow.source
            target_task = flow.target

            if isinstance(source_task, Task) and source_task.task_type == 'service':
                if isinstance(target_task, Task) and target_task.task_type == 'service':
                    errors.append(f"Structural Rule Error: Service task '{source_task.name}' is followed by another service task '{target_task.name}'.")
            
            if isinstance(source_task, Task) and source_task.task_type == 'script':
                if not isinstance(target_task, Gateway):
                    errors.append(f"Structural Rule Error: Script task '{source_task.name}' is not followed by a Gateway for error handling.")

        if errors:
            print("❌ Structural rules validation failed:")
            for e in errors:
                print("  -", e)
            return False
        else:
            print("✅ Structural rules are valid.")
            return True

    def validate_advanced_structural_rules(self) -> bool:
        errors = []

        # Gateway branching rule
        for obj in self.flow_objects:
            if isinstance(obj, Gateway):
                incoming_flows = [flow for flow in self.sequence_flows if flow.target.id == obj.id]
                outgoing_flows = [flow for flow in self.sequence_flows if flow.source.id == obj.id]

                if len(incoming_flows) == 1 and len(outgoing_flows) == 1:
                    errors.append(f"Advanced Structural Rule Error: Gateway '{obj.name}' is redundant with one incoming and one outgoing flow.")
                elif len(incoming_flows) > 1 and len(outgoing_flows) > 1:
                    errors.append(f"Advanced Structural Rule Error: Gateway '{obj.name}' cannot be both a joining and a splitting gateway.")

        # Event placement rule
        for flow1 in self.sequence_flows:
            if isinstance(flow1.target, IntermediateCatchEvent):
                for flow2 in self.sequence_flows:
                    if flow2.source.id == flow1.target.id:
                        source_task = flow1.source
                        target_task = flow2.target
                        if isinstance(source_task, Task) and isinstance(target_task, Task):
                            if source_task.task_type == target_task.task_type:
                                errors.append(f"Advanced Structural Rule Error: IntermediateCatchEvent is between two tasks of the same type '{source_task.task_type}'.")

        if errors:
            print("❌ Advanced structural rules validation failed:")
            for e in errors:
                print("  -", e)
            return False
        else:
            print("✅ Advanced structural rules are valid.")
            return True

    def validate_topological_rules(self) -> bool:
        errors = []
        adj = {obj.id: [] for obj in self.flow_objects}
        for flow in self.sequence_flows:
            adj[flow.source.id].append(flow.target)

        # Rule: Valid Loop Structure
        cycles = self._find_cycles()
        for cycle in cycles:
            has_task = any(isinstance(self._get_flow_object_by_id(node_id), Task) for node_id in cycle)
            if not has_task:
                errors.append(f"Topological Rule Error: Loop {cycle} contains no tasks.")
            
            has_exit = any(any(successor.id not in cycle for successor in adj[node_id]) for node_id in cycle)
            if not has_exit:
                errors.append(f"Topological Rule Error: Loop {cycle} has no exit path.")

        # Rule: Path Symmetry
        gateways = {obj.id: obj for obj in self.flow_objects if isinstance(obj, Gateway)}
        for gw_id, gw in gateways.items():
            incoming = [f for f in self.sequence_flows if f.target.id == gw_id]
            outgoing = [f for f in self.sequence_flows if f.source.id == gw_id]

            if len(incoming) == 1 and len(outgoing) > 1: # Splitting gateway
                reachable_from_branches = []
                for start_node in adj[gw.id]:
                    q, visited, reachable = [start_node], {start_node.id}, {start_node.id}
                    while q:
                        curr = q.pop(0)
                        for neighbor in adj.get(curr.id, []):
                            if neighbor.id not in visited:
                                visited.add(neighbor.id)
                                q.append(neighbor)
                        reachable.update(visited)
                    reachable_from_branches.append(reachable)
                
                if reachable_from_branches:
                    common_nodes = set.intersection(*reachable_from_branches)
                    if not any(isinstance(self._get_flow_object_by_id(nid), Gateway) and len([f for f in self.sequence_flows if f.target.id == nid]) > 1 for nid in common_nodes):
                        errors.append(f"Topological Rule Error: Splitting gateway '{gw.name}' lacks a corresponding joining gateway.")

        if errors:
            print("❌ Topological rules validation failed:")
            for e in errors:
                print("  -", e)
            return False
        else:
            print("✅ Topological rules are valid.")
            return True

    def validate_reachability(self) -> bool:
        """Validate that all nodes are reachable from start and can reach an end"""
        errors = []
        
        # Build adjacency list
        adj_forward = {obj.id: [] for obj in self.flow_objects}
        adj_backward = {obj.id: [] for obj in self.flow_objects}
        for flow in self.sequence_flows:
            adj_forward[flow.source.id].append(flow.target.id)
            adj_backward[flow.target.id].append(flow.source.id)
        
        # Find start event
        start_events = [o for o in self.flow_objects if isinstance(o, StartEvent)]
        if not start_events:
            return True  # Already caught by syntax validation
        start_id = start_events[0].id
        
        # Find end events
        end_events = [o for o in self.flow_objects if isinstance(o, EndEvent)]
        if not end_events:
            return True  # Already caught by syntax validation
        end_ids = {e.id for e in end_events}
        
        # Check reachability from start (forward)
        reachable_from_start = self._bfs(start_id, adj_forward)
        for obj in self.flow_objects:
            if obj.id not in reachable_from_start and not isinstance(obj, StartEvent):
                errors.append(f"Reachability Error: Node '{obj.name}' (ID: {obj.id}) is not reachable from the start event.")
        
        # Check reachability to end (backward from all end events)
        reachable_to_end = set()
        for end_id in end_ids:
            reachable_to_end.update(self._bfs(end_id, adj_backward))
        
        for obj in self.flow_objects:
            if obj.id not in reachable_to_end and not isinstance(obj, EndEvent):
                errors.append(f"Reachability Error: Node '{obj.name}' (ID: {obj.id}) cannot reach any end event (dead end).")
        
        if errors:
            print("❌ Reachability validation failed:")
            for e in errors:
                print("  -", e)
            return False
        else:
            print("✅ Reachability is valid.")
            return True

    def _bfs(self, start_id: str, adj: dict) -> set:
        """Breadth-first search to find all reachable nodes"""
        visited = {start_id}
        queue = [start_id]
        
        while queue:
            current = queue.pop(0)
            for neighbor in adj.get(current, []):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)
        
        return visited

    def _get_flow_object_by_id(self, object_id: str) -> Optional[FlowObject]:
        for obj in self.flow_objects:
            if obj.id == object_id:
                return obj
        return None

    def _find_cycles(self):
        adj = {obj.id: [flow.target.id for flow in self.sequence_flows if flow.source.id == obj.id] for obj in self.flow_objects}
        cycles = []
        
        for node in adj:
            path, q = [node], [(node, [node])]
            while q:
                curr, p = q.pop(0)
                for neighbor in adj.get(curr, []):
                    if neighbor == node:
                        sorted_cycle = tuple(sorted(p))
                        if sorted_cycle not in [tuple(sorted(c)) for c in cycles]:
                            cycles.append(p)
                    elif neighbor not in p:
                        q.append((neighbor, p + [neighbor]))
        return cycles

    def _get_task_sequences(self):
        sequences = []
        visited_tasks = set()
        
        for obj in self.flow_objects:
            if isinstance(obj, Task) and obj.id not in visited_tasks:
                current_sequence = []
                task = obj
                while isinstance(task, Task) and task.id not in visited_tasks:
                    visited_tasks.add(task.id)
                    current_sequence.append(task)
                    
                    # Find the next task in the sequence
                    next_task = None
                    for flow in self.sequence_flows:
                        if flow.source.id == task.id:
                            if isinstance(flow.target, Task):
                                next_task = flow.target
                                break 
                            else: # Gateway or Event
                                break
                    task = next_task
                
                if current_sequence:
                    sequences.append(current_sequence)
        return sequences

    def validate_static_semantics(self) -> bool:
        errors = []

        # Type checking for Task task_type
        for obj in self.flow_objects:
            if isinstance(obj, Task):
                if obj.task_type not in ALLOWED_TASK_TYPES:
                    errors.append(
                        f"Static Semantic Error: Task '{obj.name}' (ID: {obj.id}) has an invalid task_type: '{obj.task_type}'. Expected one of {ALLOWED_TASK_TYPES}."
                    )
            
            # Type checking for Gateway gateway_type
            if isinstance(obj, Gateway):
                if obj.gateway_type not in ALLOWED_GATEWAY_TYPES:
                    errors.append(
                        f"Static Semantic Error: Gateway '{obj.name}' (ID: {obj.id}) has an invalid gateway_type: '{obj.gateway_type}'. Expected one of {ALLOWED_GATEWAY_TYPES}."
                    )

        # Type checking for SequenceFlow source and target
        for flow in self.sequence_flows:
            if not isinstance(flow.source, FlowObject):
                errors.append(
                    f"Static Semantic Error: SequenceFlow source (ID: {flow.source.id}) is not a valid FlowObject."
                )
            if not isinstance(flow.target, FlowObject):
                errors.append(
                    f"Static Semantic Error: SequenceFlow target (ID: {flow.target.id}) is not a valid FlowObject."
                )

        # Unique ID checking
        all_ids = set()
        duplicate_ids = set()
        for obj in self.flow_objects + self.data_objects + self.data_stores:
            if obj.id in all_ids:
                duplicate_ids.add(obj.id)
            else:
                all_ids.add(obj.id)

        if duplicate_ids:
            errors.append(f"Static Semantic Error: Duplicate IDs found: {', '.join(duplicate_ids)}.")

        if errors:
            print("❌ Static semantics validation failed:")
            for e in errors:
                print("  -", e)
            return False
        else:
            print("✅ Static semantics are valid.")
            return True

    def suggest_improvements(self):
        suggestions = []

        # Syntax-related suggestions
        start_events = [o for o in self.flow_objects if isinstance(o, StartEvent)]
        if len(start_events) == 0:
            suggestions.append("Add a StartEvent to initiate the process. A BPMN process should have exactly one StartEvent.")
        elif len(start_events) > 1:
            suggestions.append("Keep only one StartEvent. A BPMN process should have exactly one StartEvent.")

        end_events = [o for o in self.flow_objects if isinstance(o, EndEvent)]
        if len(end_events) == 0:
            suggestions.append("Add at least one EndEvent to mark process termination.")

        # Check for unconnected flow objects (excluding data objects and data stores for now)
        connected_ids = set()
        for flow in self.sequence_flows:
            connected_ids.add(flow.source.id)
            connected_ids.add(flow.target.id)

        for obj in self.flow_objects:
            if obj.id not in connected_ids:
                suggestions.append(f"Connect the flow object '{obj.name}' (ID: {obj.id}) with a sequence flow. Unconnected objects can lead to dead ends or unreachable paths.")

        if not self.sequence_flows:
            suggestions.append("Add sequence flows to define the order of execution between flow objects.")

        # Static semantic-related suggestions
        all_ids = set()
        duplicate_ids = set()
        for obj in self.flow_objects + self.data_objects + self.data_stores:
            if obj.id in all_ids:
                duplicate_ids.add(obj.id)
            else:
                all_ids.add(obj.id)
        if duplicate_ids:
            suggestions.append(f"Ensure all element IDs are unique. Duplicate IDs found: {', '.join(duplicate_ids)}.")

        for obj in self.flow_objects:
            if isinstance(obj, Task):
                if obj.task_type not in ALLOWED_TASK_TYPES:
                    suggestions.append(
                        f"Task '{obj.name}' (ID: {obj.id}) has an invalid task_type: '{obj.task_type}'. Please use one of the allowed types: {ALLOWED_TASK_TYPES}."
                    )
            if isinstance(obj, Gateway):
                if obj.gateway_type not in ALLOWED_GATEWAY_TYPES:
                    suggestions.append(
                        f"Gateway '{obj.name}' (ID: {obj.id}) has an invalid gateway_type: '{obj.gateway_type}'. Please use one of the allowed types: {ALLOWED_GATEWAY_TYPES}."
                    )

        for flow in self.sequence_flows:
            if not isinstance(flow.source, FlowObject):
                suggestions.append(
                    f"SequenceFlow source (ID: {flow.source.id}) is not a valid FlowObject. Ensure sequence flows connect valid flow objects."
                )
            if not isinstance(flow.target, FlowObject):
                suggestions.append(
                    f"SequenceFlow target (ID: {flow.target.id}) is not a valid FlowObject. Ensure sequence flows connect valid flow objects."
                )

        if not suggestions:
            print("✅ No improvement suggestions. Process structure looks good.")
        else:
            print("💡 Suggestions for improvement:")
            for s in suggestions:
                print("  -", s)

    def describe(self):
        print(f"\nProcess: {self.name}")
        for obj in self.flow_objects:
            print(f"  {obj.__class__.__name__}: {obj.id} - {obj.name}")
        for flow in self.sequence_flows:
            print(f"  Sequence: {flow.source.id} -> {flow.target.id}")


class BPMN:
    """Main BPMN class that provides access to all BPMN elements and validation functionality"""
    
    def __init__(self):
        self.Process = Process
        self.StartEvent = StartEvent
        self.EndEvent = EndEvent
        self.Task = Task
        self.Gateway = Gateway
        self.IntermediateCatchEvent = IntermediateCatchEvent
        self.IntermediateThrowEvent = IntermediateThrowEvent
        self.SequenceFlow = SequenceFlow
        self.DataObject = DataObject
        self.DataStore = DataStore
        self.FlowObject = FlowObject
    
    def create_process(self, name: str) -> Process:
        """Create a new BPMN process"""
        return Process(name)
    
    def validate_process(self, process: Process) -> bool:
        """Validate a BPMN process"""
        return process.validate()
