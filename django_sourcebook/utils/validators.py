from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
import us
import re
import os

VALID_STATES_AND_TERRITORIES = { state.fips for state in us.STATES_AND_TERRITORIES if not state.is_obsolete }
VALID_AUDIO_FORMATS = {".mp3", ".m4a", ".wav", ".webm"}
VALID_FOIA_EXTENSIONS = {".doc", ".docx"}
FIPS_CODE_REGEX = re.compile(r"^[0-9]{2}$")
# Twitter usernames must be <= 15 characters and must only contain alphanumeric characters or underscores
TWITTER_REGEX = re.compile(r"^@[_A-Za-z0-9]{1,15}$")

def validate_fips(fips_code):
    if not isinstance(fips_code, str) or not FIPS_CODE_REGEX.match(fips_code):
        raise ValidationError("The state FIPS code must be a two-ASCII digit string.")
    if not fips_code in VALID_STATES_AND_TERRITORIES:
        raise ValidationError("Could not find state from FIPS code.")

def _validate_extension(input_file, extension_set):
    input_text = input_file.name
    _, extention = os.path.splitext(input_text)
    if not extention.lower() in extension_set:
        raise ValidationError(f"This only accepts the following extensions: {','.join(extension_set)}")

def validate_template_extension(foia_template):
    return _validate_extension(foia_template, VALID_FOIA_EXTENSIONS)

def validate_audio_extension(audio_file):
    return _validate_extension(audio_file, VALID_AUDIO_FORMATS)

ZipCodeValidator = RegexValidator(
    regex=r"^[0-9]{5}(\-[0-9]{4})?$",
    message="The ZIP code does not match a NNNNN or NNNNN-NNNN format"  
)

TwitterHandleValidator = RegexValidator(
    regex=TWITTER_REGEX,
    message="Twitter handles must start with @ and contain between 1 and 15 alphanumeric characters"
)