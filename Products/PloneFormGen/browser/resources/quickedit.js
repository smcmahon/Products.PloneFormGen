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
    // $("#allWidgets").tabs(".widgetPane", {tabs: "h2", effect: 'slide'});


    /*
        drag & drop support
    */
    function dd_init(config) {
        var dd_defaults = {
            drag_selector: null,
            drop_selector: null,
            dragClass: 'item-dragging',
            cloneClass: 'drag-proxy',
            reorder: false,
            drop: null // function to handle drop event
        };
        var options = $.extend({}, dd_defaults, config),
            drop_targets;

        $(options.drag_selector)
            .drag("start", function(ev, dd) {

                // drop is a global; we need to use it here so that our configuration
                // takes control from any previous settings.
                // set tolerance function to determine insertion point
                // and mark it with a class on the target
                drop({
                    tolerance: function(event, proxy, target) {
                        var test = event.pageY > ( target.top + target.height / 2 );

                        $.data( target.elem, "drop+reorder", test ? "insert_after" : "insert_before" );
                        return this.contains(target, [ event.pageX, event.pageY ]);
                        }
                    });

                $(this).addClass(options.dragClass);

                // create and return a proxy
                return $(this).clone()
                    .addClass(options.cloneClass)
                    .appendTo($('body'));
            })
            .drag(function(ev, dd) {
                var drop = dd.drop[0],
                    method = $.data( drop || {}, "drop+reorder" );

                if (!drop) {
                    drop_targets.removeClass("insert_before insert_after");
                }

                if (drop && (drop != dd.current || method != dd.method)){
                    drop_targets.removeClass("insert_before insert_after");
                    $(drop).addClass(method);
                    dd.current = drop;
                    dd.method = method;
                    dd.update();
                }
                // move the proxy
                $(dd.proxy).css({
                    top: dd.offsetY,
                    left: dd.offsetX
                });
            })
            .drag("end",function(ev, dd){
                var target,
                    jqt = $(this),
                    method;

                $(dd.proxy).remove();
                if (dd.drop.length) {
                    target = $(dd.drop[0]);
                    if (target.hasClass('insert_before')) {
                        method = 'insertBefore';
                    } else {
                        method = 'insertAfter';
                    }
                    if (options.reorder) {
                        jqt[method](target);
                    }
                    if (options.drop) {
                        options.drop(jqt, target, method);
                    }
                }
                $(this).removeClass(options.dragClass);
                drop_targets.removeClass("insert_before insert_after");
            });

        drop_targets = $(options.drop_selector);
        drop_targets
            .drop("init",function( ev, dd ){
                return (this != dd.drag);
            });
    }


    function getAuthToken () {
        return $('#auth_hold input').val();
    }


	function updatePositionOnServer (item, target, method) {
		var post_args = {
			item_id: item,
			target_id: target,
			method: method,
            _authenticator: getAuthToken()
		};
		$.post('reorderField', post_args, function () {
			console.log('reordered');
		});
	}


    dd_init({
        drag_selector: '#pfg-qetable .qefield',
        drop_selector: '#pfg-qetable .qefield',
        reorder: true,
        drop: function (dd, target, method) {
            console.log('drop field', dd, target, method);
            updatePositionOnServer(
                dd.find('.field').attr('data-fieldname'),
                target.find('.field').attr('data-fieldname'),
                method
            );
        }
    });

    dd_init({
        drag_selector: '#fieldWidgets .widget, #fieldsetWidgets .widget',
        drop_selector: '#pfg-qetable .qefield',
        drop: function (dd, target, method) {
            console.log('drop new field', dd, target, method);
        }
    });

    dd_init({
        drag_selector: '#pfgActionEdit .qefield',
        drop_selector: '#pfgActionEdit .qefield',
        reorder: true,
        drop: function (dd, target, method) {
            console.log('drop action', dd, target, method);
            updatePositionOnServer(
                dd.attr('id').slice(12),
                target.attr('id').slice(12),
                method
            );
        }
    });

    dd_init({
        drag_selector: '#actionWidgets .widget',
        drop_selector: '#pfgActionEdit .qefield',
        drop: function (dd, target, method) {
            console.log('drop new action', dd, target, method);
        }
    });

});
