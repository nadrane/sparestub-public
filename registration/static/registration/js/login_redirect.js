/**
 * Created by nicholasdrane on 12/9/14.
 */

// This is normally a called in a callback when the login modal is loaded from the server.
initialize_bootstrap_validator_login();

(function initialize_login_form_signup_link() {
    $('#login-form-signup-link').on('click', function () {
        load_signup_modal(true, true); // Second parameter for signup with redirect to '/'
    });
}());