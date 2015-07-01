// Support for PFG Quick Edit

/*global console, requirejs */

/*jslint unparam: true, white: true, browser: true, nomen: true, plusplus: true, bitwise: true, newcap: true, regexp: false */

var pfgQEdit = {};


requirejs(['jquery'], function ($) {
    'use strict';

    // $(".ArchetypesCaptchaWidget .captchaImage")
    //     .replaceWith("<div>" + pfgQEdit.messages.NO_CAPTCHA_MSG + "</div>");

    // disable and dim input elements
    $("#pfg-fieldwrapper .field :input")
        .css('opacity', 0.5)
        .each(function () {
            if (this.disabled !== undefined) {
                this.disabled = true;
            }
        });

    // widget accordion
    $("#allWidgets").tabs(".widgetPane", {tabs: "h2", effect: 'slide'});

});
