// Support for PFG Quick Edit

/*global jQuery, alert, window */

/*jslint white: true, browser: true, onevar: false, undef: true, nomen: true, eqeqeq: true, plusplus: true, bitwise: true, newcap: true, immed: true, regexp: false */

var pfgQEdit = {};

jQuery(function ($) {

    // initial styling

    $(".ArchetypesCaptchaWidget .captchaImage").replaceWith("<div>" + pfgQEdit.messages.NO_CAPTCHA_MSG + "</div>");

    // disable and dim input elements
    $("#pfg-fieldwrapper .field :input")
        .css('opacity', 0.5)
        .each(function () {
            if (typeof this.disabled !== "undefined") {
                this.disabled = true;
            }
        });

    $("#allWidgets").tabs(".widgetPane", {tabs:"h2", effect:'slide'});

});