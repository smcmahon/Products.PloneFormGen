// Support for PFG Quick Edit

/*global console, require */

/*jslint unparam: true, white: true, browser: true, nomen: true, plusplus: true, bitwise: true, newcap: true, regexp: false */


var pfgQEdit = {};

require(['jquery'], function ($) {
    'use strict';

    console.log($);

    $(".ArchetypesCaptchaWidget .captchaImage")
        .replaceWith("<div>" + pfgQEdit.messages.NO_CAPTCHA_MSG + "</div>");

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

    require(['jquery.event.drag'], function(drag) {
        console.log(drag);

        require(['jquery.event.drop'], function(drop) {
            console.log(drop);

            $('#pfg-qetable .qefield')
                .drag("start", function(ev, dd){

                    drop({
                      tolerance: function(event, proxy, target) {
                        console.log('tolerance');
                      }
                    });

                    var jqt = $(this), proxy;

                    console.log('starting drag');

                    jqt.addClass('dragging');
                    proxy = jqt.clone()
                        .addClass('drag-proxy')
                        .appendTo( document.body );

                    return proxy;
                })
                .drag(function( ev, dd ){
                    console.log('drag event');
                    // var drop = dd.drop[0],
                    // method = $.data( drop || {}, "drop+reorder" );

                    $( dd.proxy ).css({
                        top: dd.offsetY,
                        left: dd.offsetX
                    });

                    // if ( drop && ( drop != dd.current || method != dd.method ) ){
                    //     console.log('drag action');
                    //     $( this )[ method ]( drop );
                    //     dd.current = drop;
                    //     dd.method = method;
                    //     dd.update();
                    // }
                })
                .drag("end",function( ev, dd ){
                    console.log('drag end');
                    $( this ).removeClass('dragging');
                    $( dd.proxy ).remove();
                })
                .drop("init",function( ev, dd ){
                    console.log('dropinit', this, this != dd.drag);
                    return (this == dd.drag) ? false: true;
                })
                ;
        });
    });


});
