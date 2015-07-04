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
            },
            options = $.extend({}, dd_defaults, config),
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

    // activate toggles on actions and thanks pages
    $("#pfgActionEdit input[name^=cbaction-]").bind('change', function (e) {
        $.post('toggleActionActive', {
            item_id: this.name.substr('cbaction-'.length),
            _authenticator: getAuthToken()
        });
    });
    $("#pfgThanksEdit input[name^=thanksRadio]").bind('click', function (e) {
        $.post('setThanksPageTTW', {
            value: this.value,
            _authenticator: getAuthToken()
        });
    });


    // We need the required markers outside the label
    $("div.field label span.required").each(function () {
        var jqt = $(this);

        jqt.insertAfter(jqt.parent());
    });


    /*
        Initialize title editing.
        The function is only needed to put a closure around the node
        variable.
     */
    (function editTitles () {
        // first we create a new dynamic node (which will be used to edit content)
        var node = document.createElement("input");
        node.setAttribute('name', "change");
        node.setAttribute("type", "text");

        $('#pfg-qetable label.formQuestion').attr('title', 'Edit label')

        // then we attach a new event to label fields
        $("#pfg-qetable").on('click', ".qefield label.formQuestion", function (e) {
            var jqt = $(this),
                content = jqt.text(),
                tmpfor = jqt.attr('for');

            content = content.replace(/^\s*(.*?)\s*$/, '$1');
            jqt.html($(node).val(content));
            jqt.append(node);
            $(node).fadeIn();
            jqt.children().unwrap();
            node.focus();
            node.select();

            $(node).blur(function (e) {
                var jqt = $(this),
                    args;

                jqt.wrap("<label class='formQuestion' for='" + tmpfor + "'></label>");
                jqt.parent().html(jqt.val());
                args = {
                    item_id: tmpfor,
                    title: jqt.val(),
                    _authenticator: getAuthToken()
                };
                if (args.title !== content) { // only update if we actually changed the field
                    $("img.ajax-loader").css('visibility', 'visible');
                    $.post("updateFieldTitle", args, function () {
                        console.log('title updated');
                    });
                }
            });
        });
    })();

    // The function is used as a closure.
    (function toggleRequired () {
        var target, jqt;

        jqt = $(this);
        target = $("div.field label").next();

        target.each(function () {
            var jqt;

            jqt = $(this);
            if (!jqt.is("span")) {
                $("<span class='not-required' title='Make it required?'></span>")
                    .insertBefore(this);
            } else {
                jqt.attr("title", "Remove required flag?");
            }
        });

        $(document).on("click", "span.not-required", function (event) {
            var item, jqt;

            jqt = $(this);
            item = jqt.parent().attr('id').substr('archetypes-fieldname-'.length);
            // AJAX
            $.post('toggleRequired', {
                item_id: item,
                _authenticator: getAuthToken()
                }, function () {
                console.log('toggle required');
            });
            $('#archetypes-fieldname-' + item).find('[name^=' + item + ']').attr("required", "required");
            jqt.removeClass("not-required");
            jqt.addClass("required");
            // jqt.html("            ■").css({'color' : 'rgb(255,0,0)', 'display' : 'none'}).fadeIn().css("display", "inner-block");
            jqt.attr("title", "Remove required flag?");
        });

        $(document).on("click", "span.required", function (event) {
            var item, jqt;

            jqt = $(this);
            item = jqt.parent().attr('id').substr('archetypes-fieldname-'.length);
            // AJAX
            $.post('toggleRequired', {
                item_id: item,
                _authenticator: getAuthToken()
                }, function () {
                console.log('toggle required');
            });
            $('#archetypes-fieldname-' + item).find('[name^=' + item + ']').removeAttr("required");
            jqt.removeClass("required");
            jqt.addClass("not-required");
            // jqt.html("").fadeIn().css("display", "inline-block");
            jqt.attr("title", "Make it required?");
        });
    })();


});
