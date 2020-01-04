# A Django Toolkit for Journalism

## Table of Contents
- FOIA
    - [Templates](#templates)

### FOIA

#### Templates

Creating FOIA templates in this tool is fairly simple. But the tool is also picky about how you format things.

First of all, your federal FOIA template should go into the `FEDERAL_FOIA_TEMPLATE` location within your `MEDIA_ROOT/foia_templates` in `settings`. The same principal goes with a base request you use to file FOIA requests in places where you don't have a blanket form. But in the case of the base requests, you set the value of `BASE_FOIA_TEMPLATE`. (These are set to `federal_foia.docx` and `base_request.docx` by default.)

You should upload state-specific requests in the admin field in Django.

Second, any keywords in your FOIA request should be enclosed with two brackets, like `{{recipient_name}}`. You can use any amount of whitespace you want in between the brackets and the keyword. Those keywords can go anywhere you'd like, but you must limit yourself to the following keywords:

- `requested_records`: This is the field you use to specify the records you want to request. 
**Note: This is the only *mandatory* item in your template. If you do not include it, you will not be able to upload your template file.**
- `recipient_name`: The name of the FOIA Officer you're addressing the request to. If the underlying data is blank, it will automatically fill to "Public Records Officer," so you don't have to worry about not knowing the name of the public records officer.
- `public records act`: If you want to put the name of the state's public records act into the body of your request, you can do so with this keyword. This is mainly intended for base request forms and for filling out the subject line of your request.
- `expedited_processing`: This is where you offer your justification for why an agency should speed up how quickly it processes your request. This is mainly intended for federal FOIA requests, where provisions allowing for FOIA to expedite processing on some requests (rather than operating purely on a first in, first out basis) [is written into the law](https://foia.wiki/wiki/Expedited_Processing).
- `fee_waiver`: If you are asking to be exempt from charges under the public records act, use this keyword. In some places, like the federal Freedom of Information Act and the Connecticut Freedom of Information Act, there are specific provisions offering limited waivers from some fees.
- `max_response_time`: This is intended to allow you to write things like "I look forward to hearing from you within x business days." It's mainly intended for the base class. (If the state doesn't have a maximum response requirement, this skips the "within x business days" part entirely.)
- `agency_name`, `agency_street_address`, `agency_municipality`, `state`, `zip_code`: All of these are intended for you to be able to add an address into your form letter.
- `subject_line`, `foia_email`: These are mainly intended to help fill out the template and send the email. However, there may be some cases in which you'd want to use them.