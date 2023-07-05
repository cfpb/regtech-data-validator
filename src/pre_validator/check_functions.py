"""Some validation functions to handle phase 1 validation.

Phase 1 validation is the simplest form of validation and verifies the
supplied data is even close to being correct. For example, numerical 
fields are actually numbers, enums are numbers and semicolons, etc.

Each field type within the fig has a corresponding pre validaiton check
function. These are named `is_TYPE` where type is one of text, single
response, multiple response, numeric, date, and special."""


from datetime import datetime


def is_text(raw_input: str, nullable=True) -> bool:
    """If nullable==True, this method just returns True. There is no
    validation that occurs on raw input text at phase 1. If nullable
    is False and the raw string input is blank, the entry is invalid and
    False is returned. Otherwise True is returned. 
    
    The only non-nullable text field is uli. 

    Args:
        raw_input (str): Input text from Text field. 
        nullable (bool, optional): Can the text string be blank for the
            given field. Defaults to False.

    Returns:
        bool: Indicates whether the text input is valid for phase 1.
    """

    if nullable:
        # raw_input could be blank or not blank. Does not matter
        return True
    elif not nullable:
        if len(raw_input) > 0:
            # raw_input is not nullable and it is not null
            return True
        else:
            # raw string is not nullable but length was not > 0: error
            return False


def is_single_response(raw_input: str) -> bool:
    """Attempts to convert raw_input to an integer. If successful, True
    is returned. Otherwise False is returned. 

    Args:
        raw_input (str): Input text from Single Response field. 

    Returns:
        bool: Indicates whether the text input is valid for phase 1.
    """
    
    try:
        int(raw_input)
        return True
    except ValueError:
        return False
    
    
def is_multiple_response(raw_input: str) -> bool:
    """Attempts to split raw_input on semicolons and cast each entry to
    an integer. If successful, True is returned. Otherwise False is 
    returned. A trailing semicolon does not cause validation to fail.

    Args:
        raw_input (str): Input text from Multiple Response field. 

    Returns:
        bool: Indicates whether the text input is valid for phase 1.
    """
    
    # remove trailing semicolon if present
    if raw_input.endswith(";"):
        raw_input = raw_input[:-1]
        
    try:
        [int(entry) for entry in raw_input.split(";")]
        return True
    except ValueError:
        return False
    

def is_numeric(raw_input: str, int_only=False) -> bool:
    """Verifies raw_input can be cast to an integer if int_only==True,
    or a float when int_only==False.
    
    For fields where the validations specify "must be a whole number",
    the `int_only` flag should be set to True. Otherwise the default
    value of False can be retained. 

    Args:
        raw_input (str): Input text from Numeric field. 
        int_only (bool, optional): Indicates whether the value can
            contain decimals. Defaults to False.

    Returns:
        bool: Indicates whether the text input is valid for phase 1.
    """
    
    if int_only:
        try:
            int(raw_input)
            return True
        except ValueError:
            return False
    else: # int_only=False
        try:
            float(raw_input)
            return True
        except ValueError:
            return False
        
    
def is_date(raw_input: str) -> bool:
    """Verifies that raw_input can be cast to a date object with format
    YYYYMMDD.

    Args:
        raw_input (str): Input text from Date field. 

    Returns:
        bool: Indicates whether the text input is valid for phase 1.
    """
    
    try:
        datetime.strptime(raw_input, "%Y%m%d")
        return True
    except ValueError:
        return False
    

def is_special(raw_input: str, width: int) -> bool:
    """Verifies the length of 'Special' field types. These are fields 
    that have a fixed length that may be null. This is used for Field 35
    and Field 39. 

    Args:
        raw_input (str): Input text from Special field.
        width (int): If raw_input is not null, it should have this 
            length. 

    Returns:
        bool: Indicates whether the text input is valid for phase 1.
    """

    return len(raw_input) == 0 or len(raw_input) == width

