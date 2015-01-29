var $cropper_image = undefined;

function editable_profile() {
    'use strict';

    var profile_picture = $('#user-picture>div');

    /* Make the profile picture have animations that indicate that it is editable */
    profile_picture.hover(function () {
        $('#edit-profile-icon').animate({fontSize: "1.2em"}, 200);
        $('#edit-profile-text').fadeIn(200);
    }, function () {
        $('#edit-profile-icon').animate({fontSize: "1.8em"}, 200);
        $('#edit-profile-text').fadeOut(200);
    });
    profile_picture.css('cursor', 'pointer');
}

/* RELATED TO EDIT PROFILE ACTIVITY */
function initialize_select_photo() {
    'use strict';

    $('#select-photo').on('click', function () {
        $('#is-valid-photo').val(false); // A new photo has not yet been cropped, so it must be invalid.
        $('#use-old-photo').val(false);   // This will never be set to true unless the user had a photo when the edit
                                         // profile activity was loaded. This is required so users can remove profile
                                         // pics.
    });
}

function initialize_remove_photo() {
    $('#remove-photo').on('click', function () {
        $('#is-valid-photo').val(true);  // It's perfectly fine to have no photo.

        // When an image is selected, we change this width to auto so that the div scales to the child img dimensions
        $('.fileinput-preview').width('250px').height('200px');

        // Handle the case where the remove button was clicked after cropping occurred.
        $('#crop').text('Crop');
        $('#rotate-left, #rotate-right').css('cursor', 'pointer');
    });
}

function initialize_crop_button($cropper_image) {
    'use strict';

    $('#crop').click(function () {
        // Has the image been cropped yet?
        if ($('.cropper-disabled').length > 0) {
            $cropper_image.cropper('enable');
            $('#crop').text('Crop');
            $('#is-valid-photo').val(false);

            // The user can once again use the rotate buttons since they undid cropping
            // The cropper API takes care of preventing the actual image rotation
            $('#rotate-left, #rotate-right').css('cursor', 'pointer');

        // If the image has not been cropped yet
        } else {
            $cropper_image.cropper('disable');
            $('#crop').text('Uncrop');
            $('#is-valid-photo').val(true);
            store_crop();

            // The user cannot use the rotate buttons after cropping
            // The cropper API takes care of preventing the actual image rotation
            $('#rotate-left, #rotate-right').css('cursor', 'not-allowed');
        }
        $('#edit-profile-form').bootstrapValidator('revalidateField', 'profile_picture');
    });
}

function initialize_rotation_buttons($cropper_image) {
    'use strict';

    var $rotate_degrees = $('#rotate-degrees');
    $('#rotate-left').on('click', function () {
        $cropper_image.cropper('rotate', -90);

        var current_rotation_degrees = $rotate_degrees.val();

        // We need this conditional because parseInt on "" returns NaN
        if (current_rotation_degrees === "") {
            $rotate_degrees.val(-90);
        } else {
            $rotate_degrees.val(((parseInt($rotate_degrees.val(), 10)) - 90) % 360);
        }

    });
    $('#rotate-right').on('click', function () {
        $cropper_image.cropper('rotate', 90);

        var current_rotation_degrees = $rotate_degrees.val();

        // We need this conditional because parseInt on "" returns NaN
        if (current_rotation_degrees === "") {
            $rotate_degrees.val(90);
        } else {
            $rotate_degrees.val(((parseInt($rotate_degrees.val(), 10)) + 90) % 360);
        }

    });
}

function store_crop() {
    'use strict';

    var data = $cropper_image.cropper('getData');

    // parseInt will always round down, so this will introduce some rounding error,
    // but that's probably fine for this application. A integer is expected by a server, which is why we do this.
    $('#x').val(parseInt(data.x));
    $('#y').val(parseInt(data.y));
    $('#w').val(parseInt(data.width));
    $('#h').val(parseInt(data.height));
}


function resize_profile_picture_preview() {
    /* When an image is previewed for cropping, we need to ensure that it's is scaled to an appropraite size without
       distorting it's aspect ratio. This function sets a mutation observer that does just that.
    */
    'use strict';

    $('.modal-body').on('change.bs.fileinput', function (e, files) {
        var original_image = $('.fileinput-preview>img')[0];
        var width = original_image.naturalWidth;
        var height = original_image.naturalHeight;
        var aspect_ratio = 0;
        aspect_ratio = width / height;
        var new_width, new_height, scale_factor = 0;
        if (width > height) {
            if (width > 407) {
                scale_factor = width / 407;
                new_width = width / scale_factor;
                new_height = height / scale_factor;
            }
        } else {
            if (height > 407) {
                scale_factor = height / 407;
                new_width = width / scale_factor;
                new_height = height / scale_factor;
            }
        }

        $(original_image).height(new_height).width(new_width);

        // We need to edit the container of the image to avoid restricting the image size
        $('.fileinput-preview').css('width', 'auto').css('height', 'auto');

        // The croppoer demo only does this once... it seems like more img tags are produced by the API as it operates
        $cropper_image = $(".fileinput-preview img");

        // Enable the cropper once an image is selected
        $(original_image).cropper({aspectRatio : 1.0,
                                   zoomable: false});

        // Before we accidentally attach these events multiple times, remove any old instances.
        $('#rotate-right, #rotate-left, #crop').off('click');

        // These need to be done once the img tags exist.
        initialize_rotation_buttons($cropper_image);
        initialize_crop_button($cropper_image);
    });
}

function valid_photo() {
    var is_valid = $('#is-valid-photo').val();
    if (is_valid === 'true' || is_valid === true) {
        return true;
    } else if (is_valid === 'false' || is_valid === false) {
        return false;
    } else {
        return false;
    }
}

function initialize_spinner(button_status_div) {
    'use strict';
    // Setup a spinning loading sign that fires when a user tries to save the answer to a profile question.

    $(button_status_div).empty(); // Remove checkmark or x before placing spinner down.
    var opts = {lines: 10,
                radius: 6.5,
                width: 4
                };
    var spinner = new Spinner(opts).spin(button_status_div);
    return spinner;
}

function update_question_form() {
    $('.question-update-form').submit(function (e) {
        e.preventDefault();

        // Get the form instance
        var $form = $(e.target);

        var button_status_div = $(e.target[2]).children();
        var spinner = initialize_spinner(button_status_div[0]); // Attach onto the 'answer-button-status' div
        $.post($form.attr('action'), $form.serialize(), 'json')
            .done(function (data, textStatus, xhr) {
                add_success_checkmark(button_status_div);
            })
            .fail(function (data, textStatus, xhr) {
                add_failure_x(button_status_div);
            })
            .always(function () {
                spinner.stop();
            });
    });

    // Remove the green checkmark or red X when the user edits their answer
    $('.answer').on('input propertychange', function () {
        $(this).siblings().find('.answer-button-status').html('');
    });
}

function initialize_bootstrap_validator_edit_profile() {
    'use strict';
    $('#edit-profile-form').bootstrapValidator({
        feedbackIcons: {
            valid: 'glyphicon glyphicon-ok',
            invalid: 'glyphicon glyphicon-remove',
            validating: 'glyphicon glyphicon-refresh'
        },
        submitButtons: $('#edit-profile-form-submit-button'),
        excluded: [] // Do not exclude hidden/not displayed fields. This allows us to run an initial round of
                     // validation on the user's current data while the form is closed. Otherwise every field would
                     // just get skipped.
    });
}

function initialize_bootstrap_validator_change_password() {
    'use strict';
    $('#change-password-form').bootstrapValidator({
        feedbackIcons: {
            valid: 'glyphicon glyphicon-ok',
            invalid: 'glyphicon glyphicon-remove',
            validating: 'glyphicon glyphicon-refresh'
        },
        submitButtons: $('#change-password-form-submit-button'),
    });
}

$(document).ready(function ($) {
    'use strict';
    // Do not let a user edit a different user's profile
    editable_profile();
    update_question_form();
    $('#user-picture').on('click', function () {
        // If the modal content has already been loaded, don't do it again
        if ($('#modal-edit-profile-form-content').children().length > 0) {
            return;
        }

        $.get(window.additional_parameters.edit_profile_form_url, function (data) {
            $('#modal-edit-profile-form-content').html(data);
            initialize_bootstrap_validator_edit_profile();
            initialize_bootstrap_validator_change_password();

            // The form comes with the user's current information filled inside it.
            // Validate the form so that all fields do not need to be changed to resumbit the form.
            // As it stands, a field will only be validated if it's changed, and all fields must be validated.
            // We to have to do every field individually because BV actually submits the form to the
            // server using it's validate method, which we obviously don't want.
            var $edit_profile_form = $('#edit-profile-form');
            $edit_profile_form.bootstrapValidator('revalidateField', 'first_name');
            $edit_profile_form.bootstrapValidator('revalidateField', 'last_name');
            $edit_profile_form.bootstrapValidator('revalidateField', 'zip_code');
            $edit_profile_form.bootstrapValidator('revalidateField', 'email');
            $edit_profile_form.bootstrapValidator('revalidateField', 'username');
            $edit_profile_form.bootstrapValidator('revalidateField', 'profile_picture');

            resize_profile_picture_preview();
            initialize_select_photo();
            initialize_remove_photo();
        });
    });
});