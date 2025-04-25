import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.Final_Module_1_Assessment import Incident, Resource

# This tests that a new incident is initialised correctly
def test_incident_init():
    incident = Incident("INC001", "Zone 1", "Fire", "High", ["Ambulance"])
    assert incident.id == "INC001"
    assert incident.location == "Zone 1"
    assert incident.emergency_type == "Fire"
    assert incident.priority == "High"
    assert incident.required_resources == ["Ambulance"]
    assert incident.status == "Pending"

# This tests that a resource becomes unavailable after being allocated
def test_resource_allocation_marks_unavailable():
    from src.Final_Module_1_Assessment import ResourceManager, Resource

    manager = ResourceManager()
    ambulance = Resource("AMB001", "Ambulance", "Zone 1")
    manager.add_resource(ambulance)

    # Allocate the resource
    allocated = manager.allocate_correct_resource("AMB001")

    assert allocated is not None
    assert allocated.id == "AMB001"
    assert not allocated.available 

# This tests that an incident is assigned the correct resource
def test_incident_allocation():
    from src.Final_Module_1_Assessment import IncidentManager, ResourceManager, Incident, Resource

    incident_manager = IncidentManager()
    resource_manager = ResourceManager()

    # Add an incident that requires an ambulance
    incident = Incident("INC001", "Zone 1", "Fire", "High", ["Ambulance"])
    incident_manager.add_incident(incident)

    # Assign an ambulance
    resource = Resource("AMB001", "Ambulance", "Zone 1")
    resource_manager.add_resource(resource)

    # Allocate
    incident_manager.reprioritize_and_allocate(resource_manager)

    assert incident.status == "Resources have now been assigned"
    assert len(incident.allocated_resources) == 1
    assert incident.allocated_resources[0].id == "AMB001"

# This tests that the get_unresolved_incidents function won't return those that are marked as 'assigned'
def test_get_unresolved_incidents():
    from src.Final_Module_1_Assessment import IncidentManager, Incident

    manager = IncidentManager()

    inc1 = Incident("INC001", "Zone 1", "Medical", "High", ["Ambulance"])
    inc2 = Incident("INC002", "Zone 2", "Fire", "Low", ["Fire Truck"])

    manager.add_incident(inc1)
    manager.add_incident(inc2)

    manager.incidents[1].status = "Resources have now been assigned"

    unresolved = manager.get_unresolved_incidents()

    assert len(unresolved) == 1
    assert unresolved[0].id == "INC001"

# Negative test - this is to test what happens when there are no resources available
def test_allocation_with_no_available_resources():
    from src.Final_Module_1_Assessment import Incident, IncidentManager, ResourceManager

    incident_manager = IncidentManager()
    resource_manager = ResourceManager()

    # This adds incident needing ambulance
    incident = Incident("INC999", "Zone 3", "Emergency", "High", ["Ambulance"])
    incident_manager.add_incident(incident)

    # NO ambulance is added to the resource manager
    incident_manager.reprioritize_and_allocate(resource_manager)

    assert incident.status == "Pending"  # No resource = should stay pending
    assert len(incident.allocated_resources) == 0

# This tests for what happens when an incident requires no resources
def test_incident_with_no_required_resources():
    from src.Final_Module_1_Assessment import Incident, IncidentManager, ResourceManager

    incident_manager = IncidentManager()
    resource_manager = ResourceManager()

    # This adds incident with an empty list for required resources
    incident = Incident("INC888", "Zone 4", "Minor", "Low", [])
    incident_manager.add_incident(incident)

    incident_manager.reprioritize_and_allocate(resource_manager)

    # Since no resources are needed, it should be marked as assigned immediately
    assert incident.status == "Resources have now been assigned"
    assert len(incident.allocated_resources) == 0

# Negative test - this is to test when user inputs a type with typos
def test_duplicate_incident_ids():
    from src.Final_Module_1_Assessment import Incident, IncidentManager

    manager = IncidentManager()

    incident1 = Incident("INC001", "Zone 1", "Fire", "High", ["Ambulance"])
    incident2 = Incident("INC001", "Zone 2", "Medical Emergency", "Low", ["Medical Team"])  # Same ID

    manager.add_incident(incident1)
    manager.add_incident(incident2)

    # The application prevents duplicates so on only one unique incident is to be expected
    assert len(manager.incidents) == 2 

