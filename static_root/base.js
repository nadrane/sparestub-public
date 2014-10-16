/**
 * Created by nicholasdrane on 10/6/14.
 */

var $ = jQuery;
var document = window.document;

$(document).ready(function ($) {
    'use strict';
    $('.contact-form-button').on('click', function () {
        // If the modal content has already been loaded, don't do it again
        if ($('#modal-contact-form-content').children().length > 0) {
            return;
        }
        $.get(window.additional_parameters.contact_form_url, function (data) {
            $('#modal-contact-form-content').html(data);
            initialize_bootstrap_validator_contact();
        });
    });

    $('.signup-form-button').on('click', function () {
        // If the modal content has already been loaded, don't do it again
        if ($('#modal-signup-form-content').children().length > 0) {
            return;
        }
        $.get(window.additional_parameters.signup_form_url, function (data) {
            $('#modal-signup-form-content').html(data);
            initialize_bootstrap_validator_signup();
        });
    });

    $('.login-form-button').on('click', function () {
        // If the modal content has already been loaded, don't do it again
        if ($('#modal-login-form-content').children().length > 0) {
            return;
        }
        $.get(window.additional_parameters.login_form_url, function (data) {
            $('#modal-login-form-content').html(data);
            initialize_bootstrap_validator_login();
        });
    });

}(window.jQuery));