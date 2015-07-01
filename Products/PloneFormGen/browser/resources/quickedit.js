// Support for PFG Quick Edit

/*global pfgQEdit_messages, requirejs */

/*jslint unparam: true, white: true, browser: true, nomen: true, plusplus: true, bitwise: true, newcap: true, regexp: false */

requirejs(['jquery', 'jquery.event.drag', 'jquery.event.drop'], function ($, drag, drop) {
    'use strict';

    $(".ArchetypesCaptchaWidget .captchaImage")
        .replaceWith("<div>" + pfgQEdit_messages.NO_CAPTCHA_MSG + "</div>");

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

    var dd_defaults = {
        dragClass: 'item-dragging',
        cloneClass: 'drag-proxy',
        drop: null // function to handle drop event
        };

    function dd_init(drag_selector, drop_selector, opts) {
        var options = $.extend({}, dd_defaults, opts);

        $(drag_selector)
            .drag("start", function(ev, dd) {
                return $(this).clone()
                    .addClass(options.cloneClass)
                    .appendTo($('body'));
            })
            .drag(function(ev, dd){
                $(dd.proxy).css({
                    top: dd.offsetY,
                    left: dd.offsetX
                });
            })
            .drag("end",function(ev, dd){
                $(dd.proxy).remove();
            });
        // $(drop_selector).drop(function(ev, dd){
        //     console.log('drop');
        // });
    }

    dd_init('.qefield', '.qefield', {});

});
