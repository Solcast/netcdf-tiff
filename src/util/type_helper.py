def validate(name_of_value="", value_to_check=object, d_type=object):
    if type(value_to_check) is not d_type:
        raise ValueError("{0} must be of type {1}".format(name_of_value, str(d_type)))
