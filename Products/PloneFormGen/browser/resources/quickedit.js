// Support for PFG Quick Edit

/*global console, confirm, alert, pfgQEdit_messages, requirejs */

/*jslint unparam: true, white: true, browser: true, nomen: true, plusplus: true, bitwise: true, newcap: true, regexp: true */


/*

TODO:

    Generalize add new via d&d

*/

// recurrenceinput has the jquerytools tabs code
requirejs([
        'jquery',
        'jquery.event.drag',
        'jquery.event.drop',
        'jquery.recurrenceinput',
        'mockup-patterns-modal',
        'mockup-utils'
        ], function ($, drag, drop, recurrenceinput, Modal, utils) {

    'use strict';


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
        console.log(item, target, method);
        $.post('reorderField', post_args, function () {
            console.log('reordered');
        });
    }


    function removeFieldFromForm(item) {
        var post_args = {
            item_id: item,
            _authenticator: getAuthToken()
        };
        $.post('removeFieldFromForm', post_args, function () {
            console.log('removed');
        });
    }

    $('.qefield').click('.pfgdelbutton', function (e){
        var jqt = $(this),
            item_id = jqt.attr('data-fieldname');

        e.preventDefault();

        if (confirm('Do you really want to delete this item?\n\n• ' + item_id)) {
            console.log('delete me');
            jqt.remove();
            removeFieldFromForm(item_id);
        }
    });

    // $('.qefield').on('click', '.pfgdelbutton', function(e) {
    //     $(this).preventDefault();
    //     alert('clicked');
    //     console.log($(this).parents('["data-fieldname"]').attr('data-fieldname'));
    // });

    // $('.pfgdelbutton').patPloneModal({
    //     width:400,
    //     automaticallyAddButtonActions: false,
    //     actions: {
    //         '#form-buttons-Delete': {
    //             displayInModal: false,
    //             redirectOnResponse: false,
    //             reloadWindowOnClose: false,
    //             onSuccess: function(self, response, state, xhr, form) {
    //                 var amatch;

    //                 // remove the deleted field/action's node
    //                 amatch = form[0].action.match(/.*?([^\/]*)\/delete_confirmation.*/);
    //                 if (amatch) {
    //                     console.log('deleting node #archetypes-fieldname-' + amatch[1]);
    //                     $('#archetypes-fieldname-' + amatch[1]).parent().remove();
    //                     $('#action-name-' + amatch[1]).remove();
    //                     $('#pfgThanksEdit')
    //                         .find('[data-field=' + amatch[1] + ']')
    //                         .remove();
    //                 }
    //             }
    //         },
    //         '#form-buttons-Cancel': {
    //             displayInModal: false,
    //             redirectOnResponse: false,
    //             reloadWindowOnClose: false
    //         }
    //     }
    // });


    $('.pfgeditbutton').patPloneModal({
        width:600,
        automaticallyAddButtonActions: false,
        actions: {
            "input[name='form.button.save']": {
                displayInModal: false,
                redirectOnResponse: false,
                reloadWindowOnClose: true,
                onSuccess: function(self, response, state, xhr, form) {
                    self.hide();
                    // do something to show we're loading
                    self.loading.show(false);
                }
            },
            "input[name='form.button.cancel']": {
                displayInModal: false,
                redirectOnResponse: false,
                reloadWindowOnClose: false
            }
        }
    });


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
                    valid_drop = drop && $(drop).is(options.drop_selector),
                    method = $.data( drop || {}, "drop+reorder" );

                if (!valid_drop) {
                    drop_targets.removeClass("insert_before insert_after");
                }

                if (valid_drop && (drop !== dd.current || method !== dd.method)){
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
                return (this !== dd.drag);
            })
            .drop("start", function() {
                return $(this).is(options.drop_selector);
            });
    }


    /* Drag and Drop initializations */
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

    function dropNew(dd, target, method) {
        console.log('drop new field', dd, target, method);

        var item = dd.clone(),
            create_url;

        item[method](target);
        // perform the operations on the newly dragged element from the widgets manager
        item.addClass("qechild");
        item.wrap("<div class='qefield new-widget'></div>"); // on the fly wrapping with necessary table elements
        item.before("<div class='qechild'>⣿</div>");
        item.width($(item).width());
        create_url = "createObject?type_name=" + item.context.id;
        create_url += '&_authenticator=' + getAuthToken();
        //  $(item).height($(item).height());
        // AJAX stuff
        item.children("div.widget-inside")
        .load(create_url + " #content > div:last", function (response, status, xhr) {
            var inputElem,
                msg,
                jqt;

            jqt = $(this);

            if (status === "error") {
                msg = "Sorry but there was an error: ";
                jqt.html(msg + xhr.status + " " + xhr.statusText);
            }
            else {
                jqt.find("legend").remove();
                jqt.find("#fieldset-overrides").remove();
                jqt.find(".formHelp").remove();
            }
            // set the required attribute for the on the fly validation
            inputElem = jqt.find("span.required").parent().find("input");
            inputElem.attr({required: "required"});
            // hide all the error messages so far!
            if ($("div.error").length > 0) {
                $("div.error").hide();
            }
            jqt.slideDown();

        });


        $("#pfg-qetable, #pfgActionEdit").on('click', "[name='form.button.save']", function (e) {
            var formParent = $(this).closest('form'),
                formAction = formParent.attr('action'),
                values = {};

            e.preventDefault();

            // json like structure, storing names and values of the form fields
            $.each($(formParent).serializeArray(), function (i, field) {
                values[field.name] = field.value;
            });
            $.ajax({
                type: "POST",
                url: formAction,
                data: values,
                async: false,
                success: function (response, status, xhr) {
                    var item_id,
                        widgetParent;

                    item_id = $(response)
                        .find('#contentview-view a')
                        .attr('href')
                        .split('/')
                        .reverse()[1];

                    updatePositionOnServer(
                        item_id,
                        target.attr('data-fieldname'),
                        method
                    );

                    // TODO: do something more to show we're loading
                    widgetParent = formParent.parents("div.qefield");
                    widgetParent.find("div.widget-inside").slideUp('fast', function () {
                        location.reload();
                    });
                }
            });
            return false;
        });

        $("#pfg-qetable, #pfgActionEdit").on('click', "[name='form.button.cancel']", function (e) {
            var widgetParent;

            e.preventDefault();
            // hide all the error messages so far!
            if ($("div.error").length > 0) {
                $("div.error").hide();
            }
            widgetParent = $(this).parents("div.qefield");
            widgetParent.find("div.widget-inside").slideUp('fast', function () {
                widgetParent.fadeOut('slow', function () {
                    widgetParent.remove();
                });
            });
        });
    }


    dd_init({
        drag_selector: '#fieldWidgets .widget, #fieldsetWidgets .widget',
        drop_selector: '#pfg-qetable .qefield',
        drop: dropNew
    });

    dd_init({
        drag_selector: '#pfgActionEdit .qefield',
        drop_selector: '#pfgActionEdit .qefield',
        reorder: true,
        drop: function (dd, target, method) {
            console.log('drop action', dd, target, method);
            updatePositionOnServer(
                // dd.attr('data-field').slice(12),
                // target.attr('id').slice(12),
                dd.attr('data-fieldname'),
                target.attr('data-fieldname'),
                method
            );
        }
    });

    dd_init({
        drag_selector: '#actionWidgets .widget',
        drop_selector: '#pfgActionEdit .qefield',
        drop: dropNew
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


    // We need the form help outside the label
    $("div.field label span.formHelp").each(function () {
        var jqt = $(this);

        jqt.insertAfter(jqt.parent());
    });
    // Also, the required markers; as a separate operation from help
    // to get the order right.
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

        $('#pfg-qetable label.formQuestion').attr('title', 'Edit label');

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
                    $.post("updateFieldTitle", args, function () {
                        console.log('title updated');
                    });
                }
            });
        });
    }());


    /*
        Label editing
    */

    // initialize the markers
    $("div.field label").next().each(function () {
        var jqt;

        jqt = $(this);
        if (!jqt.is("span")) {
            $("<span class='not-required' title='Make it required?'></span>")
                .insertBefore(this);
        } else {
            jqt.attr("title", "Remove required flag?");
        }
    });

    // click to edit event
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

    /*
        Required flag toggling
    */
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

    /* handle global AJAX error */
    $(document).ajaxError(function (event, request, settings) {
        alert(pfgQEdit_messages.AJAX_FAILED_MSG + settings.url);
    });


});
