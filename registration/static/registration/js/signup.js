var $ = jQuery;
var document = window.document;

var send_fbuid = function () {
    /* The Facebook user ID might get stored if the user is logged into facebook the minute he gets to the homepage.
    But just because we happen to know a user's FB ID does not mean we want to link it to their account. They need
    to explicitly choose to do this by logging in with FB.
     */
    return window.sessionStorage.send_fbuid;
}

$(document).ready(function () {
    // When we load signup.html, it is loaded asynchronously, after fb.init is executed.
    // This means that the login button is never parsed by FB. We need to do this so that it renders.
    FB.XFBML.parse(document.getElementById("#fb-login-button"));

    // We need a good way to tell when the signup  modal is being displayed and when it isn't.
    // Attach an event that will give the modal an attribute that tracks this state.
    var $modal_signup_form = $('#modal-signup-form');
    $modal_signup_form.on('shown.bs.modal', function () {
        $modal_signup_form.addClass('active_onscreen');
        // If this is a new user who is logged into FB, then automatically log them out.
        // This prevents the login modal from displaying a FB's logout button, which is super confusing if the user
        // doesn't actually have a crowdsurfer account.
        if (window.sessionStorage.fb_new_user === true && window.sessionStorage.authentication_status === 'connected') {
            FB.logout(function (response) {
            });
        }

        $('#signup_fb_uid').val(window.sessionStorage.fb_uid);  // Put the FB user ID into a hidden field that is sent
                                                                // to the server with the signup form
    });
    $modal_signup_form.on('hidden.bs.modal', function () {
        $modal_signup_form.removeClass('active_onscreen');
    });
});

/*    TODO - REMOVE FROM TEMPLATE CODE
$(document).ready(function () {
    $('#signup-form-button').click(function () {
        var fb_uid = '';
        if (send_fbuid()) {
            fb_uid = window.sessionStorage.fb_uid
        };

        $.ajax({
            type: 'POST',
            url: 'registration/signup/',
            data: {first_name: $('#signup-first-name').val(),
                   last_name: $('#signup-last-name').val(),
                   email: $('#signup-email').val(),
                   password: $('#signup-password').val(),
                   fb_uid: fb_uid,
                   fb_access_token: window.sessionStorage.fb_access_token
                  },
            dataType: 'json',
            success: function (json_response) {
                if (json_response) {
                    handle_ajax_response(json_response); // Defined in base.js
                    // We are now logged in seeing the appropriate content. No need to keep the signup form around.
                    $('#modal-signup-form').modal('hide');
                }
            }
        });
    });
});
*/