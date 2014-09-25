/**
 * Created by Nick on 1/7/14.
 */

var $ = jQuery;
var document = window.document;

$(document).ready(function () {
    // When we load login.html, it is loaded asynchronously, after fb.init is executed.
    // This means that the login button is never parsed by FB. We need to do this so that it renders.
    FB.XFBML.parse(document.getElementById("#fb-login-button"));

    // We need a good way to tell when the login modal is being displayed and when it isn't.
    // Attach an event that will give the modal an attribute that tracks this state.
    var $modal_login_form = $('#modal-login-form');
    $modal_login_form.on('shown.bs.modal', function () {
        $modal_login_form.addClass('active_onscreen');
        // If this is a new user who is logged into FB, then automatically log them out.
        // This prevents the login modal from displaying a FB's logout button, which is super confusing if the user
        // doesn't actually have a crowdsurfer account.
        if (window.sessionStorage.fb_new_user === true && window.sessionStorage.authentication_status === 'connected') {
            FB.logout(function (response) {
            });
        }
    });
    $modal_login_form.on('hidden.bs.modal', function () {
        $modal_login_form.removeClass('active_onscreen');
    });

    $('#login-form-button').click(function () {
        $.ajax({
            type: 'POST',
            url: 'registration/login/',
            data: {email: $('#login-email').val(),
                   password: $('#login-password').val()
                  },
            dataType: 'json',
            success: function (json_response) {
                if (json_response) {
                    handle_ajax_response(json_response); // Defined in base.js
                    // We are now logged in seeing the appropriate content. No need to keep the signup form around.
                    $('#modal-login-form').modal('hide');
                }
            }
        });
    });
});