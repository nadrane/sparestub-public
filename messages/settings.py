message_model_settings = {'BODY_MAX_LENGTH': 5000}

send_message_form_settings = {'BODY_NOTEMPTY_MESSAGE': 'Please enter a message.',}
send_message_form_settings.update(message_model_settings)

# These keys need to be defined after their respective MINLENGTH and MAXLENGTH keys
#  have been defined to avoid key errors.
send_message_form_settings['BODY_LENGTH_MESSAGE'] = 'Please keep your message under {} characters'.\
                                                    format(send_message_form_settings.get('BODY_MAX_LENGTH'))

new_message_subject = 'Thanks From SpareStub!'
new_message_template = 'messages/submit_message_email.html'