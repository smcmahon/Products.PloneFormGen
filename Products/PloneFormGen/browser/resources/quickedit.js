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


    // field drag and drop

    $('#pfg-qetable .qefield')
        .drag("start",function( ev, dd ){
            var jqt = $(this);

            console.log('starting drag');
            jqt.addClass('dragging');
            return jqt.clone()
                .addClass('drag-proxy')
                .appendTo( document.body );
        })
        .drag(function( ev, dd ){
            var drop = dd.drop[0],
            method = $.data( drop || {}, "drop+reorder" );

            // console.log('drag event', dd.drop);

            $( dd.proxy ).css({
                top: dd.offsetY,
                left: dd.offsetX
            });

            if ( drop && ( drop != dd.current || method != dd.method ) ){
                console.log('drag action');
                $( this )[ method ]( drop );
                dd.current = drop;
                dd.method = method;
                dd.update();
            }
        })
        .drag("end",function( ev, dd ){
            console.log('drag end');
            $( this ).removeClass('dragging');
            $( dd.proxy ).remove();
        })
        .drop("init",function( ev, dd ){
            console.log('dropinit', this, dd.drag);
            return !( this == dd.drag );
        });

    $.drop({
        tolerance: function( event, proxy, target ){
            var test = event.pageY > ( target.top + target.height / 2 );

            console.log('tolerance', this, event, proxy, target);

            $.data( target.elem, "drop+reorder", test ? "insertAfter" : "insertBefore" );
            return this.contains( target, [ event.pageX, event.pageY ] );
        }
    });

});