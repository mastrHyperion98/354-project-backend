RULE_REQUIRED_ERROR_CODE = 400
RULE_REQUIRED_ERROR_MESSAGE = "%s is required."

def required(property_key, proprety_name, json):
    """Rule used to verify that a property_key is in a json
    
    Arguments:
        property_key {string} -- Property key that is required in the json
        proprety_name {string} -- Name of the property
        json {string} -- json that requires the property
    
    Returns:
        json|NoneType -- If porperty not in json returns an error, otherwise returns None.
    """
    if property_key not in json:
        return {
            "code": RULE_REQUIRED_ERROR_CODE,
            "message": RULE_REQUIRED_ERROR_MESSAGE % proprety_name
        }

    return None

def validate(properties, json):
    """Validate all the rules for the properties on a given json. If a rule fails the function returns an error from the rule.
    
    Arguments:
        properties {[type]} -- [description]
        json {[type]} -- [description]
    
    Returns:
        [type] -- [description]
    """
    for property in properties:
        for rule in property['rules']:
            error = rule(property['key'], property['name'], json)
        if error:
            return error