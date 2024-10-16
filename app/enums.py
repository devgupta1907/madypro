from enum import Enum

class CustomerStatus(Enum):
    ACTIVE = "Active"
    BLOCKED = "Blocked"
    
    
class ProfessionalStatus(Enum):
    PENDING = "Pending"
    ACTIVE = "Active"
    BLOCKED = "Blocked"
    

class ServiceRequestStatus(Enum):
    REQUESTED = "Requested"
    ACCEPTED = "Accepted"
    REJECTED = "Rejected"
    CLOSED = "Closed"