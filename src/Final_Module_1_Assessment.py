import logging
import sys
import traceback

from typing import List, Optional, Set, Dict

class Incident:
    def __init__(self, id: str, location: str, emergency_type: str, priority: str, required_resources: List[str]):
        self.id: str = id
        self.location: str = location
        self.emergency_type: str = emergency_type
        self.priority: str = priority
        self.required_resources: List[str] = required_resources
        self.allocated_resources: List[Resource] = []
        self.status: str = "Pending"

class Resource:
    def __init__(self, id: str, type: str, location: str):
        self.id: str = id
        self.type: str = type
        self.location: str = location
        self.available: bool = True

class ResourceManager:
    def __init__(self):
        self.resources: List[Resource] = []
        self.resource_type_counters: Dict[str, int] = {}

    def add_resource(self, resource: Resource) -> None:
        self.resources.append(resource)

    def get_all_available_resources_by_type(self, type: str) -> List[Resource]:
        return [r for r in self.resources if r.available and r.type == type]

    def allocate_correct_resource(self, resource_id: str) -> Optional[Resource]:
        for r in self.resources:
            if r.id == resource_id and r.available:
                r.available = False
                return r
        return None

    def free_resource(self, resource_id: str) -> None:
        for r in self.resources:
            if r.id == resource_id:
                r.available = True

    def generate_resource_id(self, resource_type: str) -> str:
        prefix = ''.join(word[0] for word in resource_type.title().split())
        self.resource_type_counters.setdefault(prefix, 0)
        self.resource_type_counters[prefix] += 1
        return f"{prefix.upper()}{self.resource_type_counters[prefix]:03}"

class IncidentManager:
    def __init__(self):
        self.incidents: List[Incident] = []

    def add_incident(self, incident: Incident) -> None:
        self.incidents.append(incident)

    def get_unresolved_incidents(self) -> List[Incident]:
        return [i for i in self.incidents if i.status != 'Resources have now been assigned']

    def reprioritize_and_allocate(self, resource_manager: ResourceManager) -> None:
        try:
            self.incidents.sort(key=lambda i: ['High', 'Medium', 'Low'].index(i.priority))
            for incident in self.incidents:
                if incident.status == "Resources have now been assigned":
                    continue
                for req_type in incident.required_resources:
                    available: List[Resource] = resource_manager.get_all_available_resources_by_type(req_type)
                    if available:
                        res: Resource = available[0]
                        resource_manager.allocate_correct_resource(res.id)
                        incident.allocated_resources.append(res)

                if len(incident.allocated_resources) == len(incident.required_resources):
                    incident.status = "Resources have now been assigned"
        except Exception as e:
            logger: logging.Logger = logging.getLogger()
            logger.setLevel(logging.INFO)
            exception_type, exception_value, exception_traceback = sys.exc_info()
            traceback_string = traceback.format_exception(exception_type, exception_value, exception_traceback)
            err_msg: dict = {
                'errorType': exception_type.__name__,
                'errorMessage': str(exception_value),
                'stackTrace': traceback_string
            }
            logger.error(str(err_msg))

class UserConsole:
    def __init__(self):
        self.incident_manager: IncidentManager = IncidentManager()
        self.resource_manager: ResourceManager = ResourceManager()
        self.logger: logging.Logger = logging.getLogger()
        self.logger.setLevel(logging.INFO)
        self.known_types: Set[str] = {"Ambulance", "Fire Truck", "Medical Team"}
        self.load_default_resources()
        self.load_default_incidents()

    def load_default_resources(self) -> None:
        defaults = [
            Resource("AMB001", "Ambulance", "Zone 1"),
            Resource("FIRE001", "Fire Truck", "Zone 2"),
            Resource("MED001", "Medical Team", "Zone 1")
        ]
        for res in defaults:
            self.resource_manager.add_resource(res)

    def load_default_incidents(self) -> None:
        sample_incidents = [
            Incident("INC001", "Zone 1", "Fire", "High", ["Fire Truck"]),
            Incident("INC002", "Zone 1", "Medical Emergency", "Medium", ["Ambulance", "Medical Team"]),
            Incident("INC003", "Zone 2", "Traffic Accident", "Low", ["Ambulance"])
        ]
        for inc in sample_incidents:
            self.incident_manager.add_incident(inc)

    def menu(self) -> None:
        while True:
            print("\n--- Emergency Resource Allocation System ---")
            print("1. Add Incident")
            print("2. Add Resource")
            print("3. View Incidents")
            print("4. View Resources")
            print("5. Allocate Resources")
            print("6. Exit")
            choice: str = input("Choose an option: ")

            match choice:
                case '1':
                    self.add_incident()
                case '2':
                    self.add_resource()
                case '3':
                    self.view_incidents()
                case '4':
                    self.view_resources()
                case '5':
                    self.logger.info("Starting allocation based on incident priority...")
                    self.incident_manager.reprioritize_and_allocate(self.resource_manager)
                    print("Resources allocated.")
                case '6':
                    break
                case _:
                    print("Invalid choice. Try again.")

    def add_incident(self) -> None:
        try:
            id: str = input("Incident ID: ")

            # This will check for any duplicate IDs
            if any(i.id == id for i in self.incident_manager.incidents):
                print(f"Incident with ID '{id}' already exists. Please enter a unique ID.")
                return  # If there are duplcaite IDs the operation will be cancelled

            location: str = input("Location: ")
            emergency_type: str = input("Emergency Type: ")
            priority: str = input("Priority (High/Medium/Low): ")
            required: List[str] = input("Required Resources (comma-separated): ").split(',')

            incident: Incident = Incident(id, location, emergency_type, priority, required)
            self.incident_manager.add_incident(incident)
            print("Incident added.")

        except Exception as e:
            self.logger.error(f"Sorry, there has been an error adding incident: {str(e)}")


    def add_resource(self) -> None:
        try:
            print("Resource types can be: " + ", ".join(sorted(self.known_types)))
            type_input: str = input("Resource Type: ").strip().title()
            if type_input not in {t.title() for t in self.known_types}:
                confirm = input(f"'{type_input}' is a new resource type. Add it anyway? (yes/no): ").strip().lower()
                if confirm != 'yes':
                    print("Resource addition cancelled.")
                    return
                self.known_types.add(type_input)
            id: str = self.resource_manager.generate_resource_id(type_input)
            print(f"Generated Resource ID: {id}")
            location: str = input("Location: ")
            resource: Resource = Resource(id, type_input, location)
            self.resource_manager.add_resource(resource)
            print("Resource added.")
        except Exception as e:
            self.logger.error(f"Sorry, there has been an error adding resource: {str(e)}")

    def view_incidents(self) -> None:
        print("\n--- Incidents ---")
        for i in self.incident_manager.incidents:
            allocated: str = ', '.join([r.id for r in i.allocated_resources]) or 'None'
            print(f"ID: {i.id}, Type: {i.emergency_type}, Priority: {i.priority}, Status: {i.status}, Resources: {allocated}")

    def view_resources(self) -> None:
        print("\n--- Resources ---")
        for r in self.resource_manager.resources:
            status: str = "Available" if r.available else "Assigned"
            print(f"ID: {r.id}, Type: {r.type}, Location: {r.location}, Status: {status}")

if __name__ == '__main__':
    UserConsole().menu()