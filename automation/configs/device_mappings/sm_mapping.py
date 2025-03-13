import logging
log = logging.getLogger(__name__)

class SubsPartMap():
    def __init__(self):
        log.info("Initialize subscription part mapping class")

    @staticmethod
    def subs_part_map(device_type, device_model=None):
        if device_type == "IAP":
            subs_type = "CENTRAL_AP"
            part_number = "JW242AR"
            return (subs_type, part_number)
        if device_type == "SWITCH":
            subs_type = "CENTRAL_SWITCH"
            part_number = "JL255A"
            return (subs_type, part_number)
        if device_type == "GATEWAY" :
            subs_type = "CENTRAL_GW"
            part_number = "7005-RW"
            return (subs_type, part_number)

    @staticmethod
    def lic_tier_type_mapping(device_type, subs_type=None):
        if device_type == "IAP":
            return ["Advanced AP"]
        if device_type == "SWITCH":
            return ["Advanced-Switch-62xx/29xx", "Advanced-Switch-6200/29xx"]
        if device_type == "GATEWAY":
            return ["Advance-70XX", "Advanced-70xx/90xx"]