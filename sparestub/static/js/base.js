/**
 * Created by nicholasdrane on 10/6/14.
 */
$(document).ready(function ($) {
    'use strict';
    $('.contact-form-button').on('click', function () {
        // If the modal content has already been loaded, don't do it again
        if ($('#modal-contact-form-content').children().length > 0) {
            return;
        }
        $.get(window.additional_parameters.contact_form_url, function (data) {
            $('#modal-contact-form-content').html(data);
            initialize_bootstrap_validator();
        });
    });

}(window.jQuery));