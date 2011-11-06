// Support for PFG Quick Edit

/*global jQuery, alert, window */

/*jslint white: true, browser: true, onevar: false, undef: true, nomen: true, eqeqeq: true, plusplus: true, bitwise: true, newcap: true, immed: true, regexp: false */

var pfgQEdit = {};
var pfgWidgets;

pfgQEdit.qedit = function (e) {
	var tool, blurrable;

	// Turn off form-unload protection so that we don't receive
	// misleading notifications.
	// But, first save the list of forms with unload protection
	// so that we may restore it.
	tool = window.onbeforeunload && window.onbeforeunload.tool;
	if (tool) {
		tool.savedForms = tool.forms;
		tool.forms = [];
	}	 
	
	jQuery("#pfgqedit").hide();
	// hide the error messages
	jQuery(".error").hide();
	// show widgets manager
	jQuery("#pfgWidgetWrapper").fadeIn();

	jQuery(".ArchetypesCaptchaWidget .captchaImage").replaceWith("<div>" + pfgQEdit.messages.NO_CAPTCHA_MSG + "</div>");
	
    // var chillen = jQuery('.PFGFieldsetWidget').children();
    //     chillen.unwrap();
	
	// disable and dim input elements
	blurrable = jQuery("#pfg-fieldwrapper .field :input");
	blurrable.each(function () {
		if (typeof this.disabled !== "undefined") {
			this.disabled = true;
		}
	});
	blurrable.css('opacity', 0.5);

	if (jQuery.fn.prepOverlay) {
		jQuery('#plone-contentmenu-factories .actionMenuContent a[id^=form]').prepOverlay({
			subtype: 'ajax',
			filter: "#content",
			formselector: 'form[id$=base-edit]',
			noform: function () {
				location.reload();
			},
			closeselector: '[name=form.button.Cancel]'
		});
	}

    // We need the required markers outside the label
    jQuery("div.field label span.required").each(function () {
        var jqt = jQuery(this);
        
        jqt.parent().after(jqt.detach());
    });

    $("#allWidgets").tabs(".widgetPane", {tabs:"h2",effect:'slide'});

	pfgWidgets.init();
};


jQuery(function ($) {
	// activate toggles on actions and thanks pages
	$("#pfgActionEdit input[name^=cbaction-]").bind('change', function (e) {
		$.post('toggleActionActive', {item_id: this.name.substr('cbaction-'.length)});
	});
	jQuery("#pfgThanksEdit input[name^=thanksRadio]").bind('click', function (e) {
		$.post('setThanksPage', {value: this.value});
	});
	
	// set up edit and delete popups
	if ($.fn.prepOverlay) {
		$('.editHook a[href$=edit]').prepOverlay({
			subtype: 'ajax',
			filter: "#content",
			formselector: 'form[name=edit_form]:not(.fgBaseEditForm)',
			noform: 'reload',
			closeselector: '[name=form.button.cancel]'
		});
		$('.editHook a[href$=delete_confirmation]').prepOverlay({
			subtype: 'ajax',
			filter: "#content",
			formselector: 'form:has(input[value=Delete])',
			noform: function (athis) {
				var match;
	
				// remove the deleted field/action's node
				match = athis.url.match(/.+\/(.+?)\/delete_confirmation/);
				if (match) {
					$('#archetypes-fieldname-' + match[1]).parent().remove();
					$('#action-name-' + match[1]).remove();
				}
				return 'close';
			},
			closeselector: '[name=form.button.Cancel]'
		});
	}
	
	pfgQEdit.qedit();
});

// fieldset support for moving fields between them. Make the fieldsets behave like tabs.
(function ($) {
	pfgWidgets = {
		init: function () {
			$(".qefield").each(function () {
				var jqt = $(this);
				jqt.height(jqt.height()); // workaround for children's height not being able to set using %s
				jqt.width(jqt.width());	 // the same for width, for the new ui-sortable-helper
			});
			
			this.setupSortable("#pfg-qetable");
			this.setupSortable("#pfgActionEdit");

			/* Initializers for editing titles, toggling required attribute on fields and limiting number of widgets in Widgets Manager */
			this.editTitles();
			this.toggleRequired();
            // this.limitFields();

			/* set the tooltip for the widgets in Widget Manager */
			$("div.widget").tooltip({
				position: "top center",
				relative: true,
				offset: [-3, 0],
				effect: "fade",
				predelay: 700,
				opacity: 0.9
			});

			/* Set the initial tooltips for required and not-required spans */
			$("span.not-required").tooltip({
				position: "top center",
				relative: false,
				events: {
					def: "mouseenter, mouseout click"
				},
				onBeforeShow: function () {
					if (this.getTrigger().attr("title")) {
						this.getTip().html(this.getTrigger().attr("title"));
					}
				},
				onShow: function () {
					if (this.getTrigger().attr("title")) {
						this.getTrigger().removeAttr("title");
					}
					if (!this.getTrigger().parent().parent().is("div.qefield")) {
						this.hide();
					}
				},
				offset: [-6, 0]
			});

			$("span.required").tooltip({
				position: "top center",
				relative: false,
				events: {
					def: "mouseenter, mouseout click"
				},
				onBeforeShow: function () {
					if (this.getTrigger().attr("title")) {
						this.getTip().html(this.getTrigger().attr("title"));
					}
				},
				onShow: function () {
					if (this.getTrigger().attr("title")) {
						this.getTrigger().removeAttr("title");
					}
					if (!this.getTrigger().parent().parent().is("div.qefield")) {
						this.hide();
					}
				},
				offset: [-4, 0]
			});

			/* Make the widgets inside the widgets manager draggable */
			$("#fieldWidgets div.widget, #fieldsetWidgets div.widget").draggable({
				connectToSortable: "#pfg-qetable",
				helper: 'clone',
				containment: 'document'
			});
			$("#actionWidgets div.widget").draggable({
				connectToSortable: "#pfgActionEdit",
				helper: 'clone',
				containment: 'document'
			});

			/* Make the widgets manager droppable */
			$("#pfgWidgetWrapper").droppable({
				accept: function (obj) {
					return !$(obj).parent().hasClass('widgets') && (!$(obj).hasClass('w-field') && !$(obj).hasClass("w-action"));
				},
				drop: function (e, ui) {
					ui.draggable.addClass("deleting");
					$("span#deactivate-widget").hide();
				},
				over: function (e, ui) {
					$("div#pfg-qetable div.placeholder").hide();
					ui.draggable.addClass("deleting");
					ui.helper.addClass("deleting");
					$("span#deactivate-widget").show();
				},
				out: function (e, ui) {
					if (ui.draggable.hasClass("deleting")) {
						ui.draggable.removeClass("deleting");
						ui.helper.removeClass("deleting");
					}
					$("div#pfg-qetable div.placeholder").show();
					$("span#deactivate-widget").hide();
				},
				tolerance: 'pointer'
			});

			/* handle global AJAX error */
			$(document).ajaxError(function (event, request, settings) {
				$("img.ajax-loader").css('visibility', 'hidden');
				alert(pfgQEdit.messages.AJAX_FAILED_MSG + settings.url);
			});
		},

		getPos: function (node) {
			var pos = node.parent().children('.qefield').index(node[0]);
			return pos === -1 ? null : pos;
		},

		updatePositionOnServer: function (i, t) {
			if (i && t) {
				$("img.ajax-loader").css('visibility', 'visible');
			}
			var args = {
				item_id: i,
				target_id: t
			};
			$.post('reorderField', args, function () {
				$("img.ajax-loader").css('visibility', 'hidden');
			});
		},

		editTitles: function () {
			// first we create a new dynamic node (which will be used to edit content)
			var node = document.createElement("input");
			node.setAttribute('name', "change");
			node.setAttribute("type", "text");

			// then we attach a new event to label fields
			$("#pfg-qetable .qefield label.formQuestion").live('dblclick', function (e) {
				var content, tmpfor, jqt;
			
				jqt = $(this);

				content = jqt.text();
				tmpfor = jqt.attr('for');
				jqt.append(node);
				jqt.html($(node).val(content));
				$(node).fadeIn();
				jqt.children().unwrap();
				node.focus();
				node.select();

				$(node).blur(function (e) {
					var jqt, args;
				
					jqt = $(this);

					jqt.wrap("<label class='formQuestion' for='" + tmpfor + "'></label>");
					jqt.parent().html(jqt.val());
					args = {
						item_id: tmpfor,
						title: jqt.val()
					};
					if (args.title !== content) { // only update if we actually changed the field
						$("img.ajax-loader").css('visibility', 'visible');
						$.post("updateFieldTitle", args, function () {
							$("img.ajax-loader").css('visibility', 'hidden');
						});
					}
				});
			});

		},

		toggleRequired: function () {
			var target, jqt;
		
			jqt = $(this);
			target = $("div.field label").next();

			target.each(function () {
				var jqt;
				
				jqt = $(this);
				if (!jqt.is("span")) {
					$("<span class='not-required' style='display:inline-block' title='Make it required?'></span>").insertBefore(this);
				} else {
					jqt.attr("title", "Remove required flag?");
				}
			});

			$("span.not-required").live("click", function (event) {
				var item, jqt;
			
				jqt = $(this);
				item = jqt.parent().attr('id').substr('archetypes-fieldname-'.length);
				$("img.ajax-loader").css('visibility', 'visible');
				// AJAX
				$.post('toggleRequired', {item_id: item }, function () {
					$("img.ajax-loader").css('visibility', 'hidden');
				});
				$('#archetypes-fieldname-' + item).find('[name^=' + item + ']').attr("required", "required");
				jqt.removeClass("not-required");
				jqt.addClass("required");
				jqt.html("			  ■").css({'color' : 'rgb(255,0,0)', 'display' : 'none'}).fadeIn().css("display", "inner-block");
				jqt.attr("title", "Remove required flag?");
			});

			$("span.required").live("click", function (event) {
				var item, jqt;

				jqt = $(this);
				item = jqt.parent().attr('id').substr('archetypes-fieldname-'.length);
				$("img.ajax-loader").css('visibility', 'visible');
				// AJAX
				$.post('toggleRequired', {item_id: item }, function () {
					$("img.ajax-loader").css('visibility', 'hidden');
				});
				$('#archetypes-fieldname-' + item).find('[name^=' + item + ']').removeAttr("required");
				jqt.removeClass("required");
				jqt.addClass("not-required");
				jqt.html("").fadeIn().css("display", "inline-block");
				jqt.attr("title", "Make it required?");
			});
		},

		limitFields: function () {
			$("div.w-field").slice(7).hide();
			if (!$(".more").length) {		// if there's no "More fields..." link, create it.
				$("div.w-field:not(:hidden):last").next().after("<div class='more'>" + pfgQEdit.messages.MORE_FIELDS_MSG + "</div>");
			}

			$(".more").toggle(
				function () {
					var jqt = $(this);
					jqt.hide();
					$("#pfgWidgetWrapper div.w-field").slice(7).fadeIn();
					jqt.insertAfter($("div.w-field:not(:hidden):last").next());
					jqt.html(pfgQEdit.messages.LESS_FIELDS_MSG).show();
				},
				function () {
					var jqt = $(this);
					jqt.hide();
					$("#pfgWidgetWrapper div.w-field").slice(7).fadeOut();
					jqt.insertAfter($("div.w-field:not(:hidden):last").next());
					jqt.html(pfgQEdit.messages.MORE_FIELDS_MSG).show();
				}
			);
		},

		deinit: function () {
			$("label.formQuestion").die(); // removes event handlers setup by .live
			$(".more").remove();		// remove the item with bounded events to avoid conflict when "quick-edit mode" is called again
			$("span.not-required").die();
			$("span.not-required").remove(); // we don't want blank square showed in the form
			$("span.required").die(); // remove live() event listener
			// hide all the error messages so far!
			if ($("div.error").length > 0) {
				$("div.error").hide();
			}
		},

		// set up a sortable on an element
		setupSortable: function (selector) {
			var table = $(selector),
				target = table,
				item = table,
				initPos, finalPos, // initial and final positions of element being sorted (dragged)
				i = 0; // counter of newly added elements to the form

			table.sortable({
				start: function (event, ui) {
					ui.placeholder.height(ui.item.height());
					initPos = pfgWidgets.getPos(ui.item);
				},
				helper: 'clone',
				items: '.qefield',
				handle: '> div.draggingHook',
				tolerance: 'pointer',
				placeholder: 'placeholder',
	//			containment: 'document',
				update: function (e, ui) {
					var item, currpos;

					if (ui.item.hasClass("new-widget")) {
						return;
					}
					if (ui.item.is("div.widget")) {
						// perform the operations on the newly dragged element from the widgets manager
						item = ui.item;
						item.addClass("qechild");
						item.addClass("item_" + i);
						item.wrap("<div class='qefield new-widget'></div>"); // on the fly wrapping with necessary table elements
						item.before("<div class='draggable draggingHook editHook qechild'>⣿</div>");
						$("img.ajax-loader").css('visibility', 'visible');
						item.width($(item).width());
    					//	$(item).height($(item).height());
						// AJAX stuff
						item.children("div.widget-inside")
						    .load("createObject?type_name=" + 
						          ui.item.context.id + " #content > div:last",
						           function (response, status, xhr) {
							var inputElem, formElem, msg, jqt;

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
							$("img.ajax-loader").css('visibility', 'hidden');
							// set the required attribute for the on the fly validation
							inputElem = jqt.find("span.required").parent().find("input");
							formElem = jqt.find('form');
							inputElem.attr({required: "required"});
							formElem.validator({
								messageClass: formElem.attr("id") + "_" + (i - 1)  + " error",
								position: "center right",
								offset: [-10, 3]
							}).submit(function (e) {
								var tmpArray = [];
								inputElem.each(function (i, v) {
									if (!$(v).val()) {
										tmpArray.push($(v));
									}
								});
								if (tmpArray.length) {
									tmpArray[0].focus();
								}
							});
							// hide all the error messages so far!
							if ($("div.error").length > 0) {
								$("div.error").hide();
							}
							jqt.slideDown();

						});

						// bind the toggle event for toggling slideUp/slideDown
						$(".qefield div.item_" + i + " .widget-header").toggle(
							function () {
								var getId, itemNo, jqt;

								jqt = $(this);

								// hide all the error messages so far!
								if ($("div.error").length > 0) {
									$("div.error").hide();
								}
								// hide the error messages when manipulating with the widgets
								jqt.siblings("div.widget-inside").slideUp();
								getId = jqt.siblings("div.widget-inside").find("form").attr("id");
								itemNo = jqt.parent().attr("class").substr(jqt.parent().attr("class").indexOf("item") + "item_".length);
								$("div." + getId + "_" + itemNo).hide();
							},
							function () {
								// hide all the error messages so far!
								if ($("div.error").length > 0) {
									$("div.error").hide();
								}
								$(this).siblings("div.widget-inside").slideDown();
							}
						);

						// current position in the table
						currpos = $(".item_" + i).parent().index();

						$("#pfg-qetable [name=form.button.save], #pfgActionEdit [name=form.button.save]").live('click', function (e) {
							var button = $(this);
							var formParent = $(this).closest('form');
							var formAction = formParent.attr('action');
							var values = {};
							// json like structure, storing names and values of the form fields
							$.each($(formParent).serializeArray(), function (i, field) {
								values[field.name] = field.value;
							});
							$.ajax({
								type: "POST",
								url: formAction,
								data: values,  
								async: false,
								success: function () {
									//we have to calculate the position where the field
									//was dropped 
									var itemPos = pfgWidgets.getPos($('.new-widget'));
									var formFields = $('#pfg-qetable .qefield:not(.new-widget) .field, #pfg-qetable .PFGFieldsetWidget');
									if (formFields.length !== itemPos) {
										var targetElement = formFields[itemPos];
										var targetId;
										if ($(targetElement).hasClass('PFGFieldsetWidget') === true) {
											targetId = $(targetElement).attr('id').substr('pfg-fieldsetname-'.length);
										} else {
											targetId = $(targetElement).attr('id').substr('archetypes-fieldname-'.length);
										}
										var itemId;
										$.ajax({
											url: 'lastFieldIdFromForm',
											async: false,
											success: function (data) {
												itemId = data;
												pfgWidgets.updatePositionOnServer(itemId, targetId);
											}
										});
									}

									var widgetParent = button.parents("div.qefield");
									widgetParent.find("div.widget-inside").slideUp('fast', function () {
										location.reload();
									});								   
								}
							});	 
							e.preventDefault();
							return false;
						});

						$("#pfg-qetable [name=form.button.cancel], #pfgActionEdit [name=form.button.cancel]").live('click', function (e) {
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

						i += 1; // increment i on each addition
					} else {
						finalPos = pfgWidgets.getPos(ui.item);
						if (initPos > finalPos) { // we came from lower rows
							target = $(ui.item).next();
						}
						else { // we came from upper rows
							target = $(ui.item).prev();
						}
						if (target.find(".field").length) {
							target = target.find(".field").attr('id').substr('folder-contents-item-'.length);
						}
						else if (target.find(".PFGFieldsetWidget").length) {
							target = target.find(".PFGFieldsetWidget").attr('id').substr('pfg-fieldsetname-'.length);
						}

						if ($(ui.item).find(".field").length) {
							item = $(ui.item).find(".field").attr('id').substr('folder-contents-item-'.length);
						}
						else if ($(ui.item).find(".PFGFieldsetWidget").length) {
							item = $(ui.item).find(".PFGFieldsetWidget").attr('id').substr('pfg-fieldsetname-'.length);
						}
						pfgWidgets.updatePositionOnServer(item, target);
					}
				},
				out: function (e, ui) {
					if (!ui.helper) {
						return;
					}

					if (ui.helper.hasClass("widget") && (ui.helper.hasClass("w-field") || ui.helper.hasClass("w-action"))) {
						return;
					} else {
					// hide all the error messages so far!
						if ($("div.error").length > 0) {
							$("div.error").hide();
						}
						ui.helper.html(ui.helper.find("div.field label.formQuestion").text());
						ui.helper.wrapInner("<h4 class='widget-header-helper'></h4>");
						ui.helper.addClass("widget");
						ui.helper.removeClass("qefield");
						ui.helper.width("210px");
						ui.helper.height("32px");
						/*** let the helper follow the mouse! (w/o any offset between the cursor and the element) - sort: takes care of any mouse move, so this is not necessary ***/
						/*
						$(document).mousemove(function (e) {
							ui.helper.offset({top: e.pageY-15, left: e.pageX-25})
						});
						*/
						return;
					}
					return;
				},
				over: function (e, ui) {
					if (ui.helper.hasClass("widget") && (!ui.helper.hasClass("w-field") && !ui.helper.hasClass("w-action"))) {
						ui.helper.addClass("qefield");
						ui.helper.removeClass("widget");
						ui.helper.html(ui.item.html());
						ui.helper.width(ui.item.width());
						ui.helper.height(ui.item.height());
						return;
					} else {
						return;
					}
				},
				sort: function (e, ui) {
					// helper follows the mouse now and probably it's more efficient than binding mousemove event to document (because it's already binded)
					if (ui.helper.hasClass("widget")) {
						ui.helper.offset({top: e.pageY - 15, left: e.pageX - 25});
					}
				},
				stop: function (e, ui) {
					if (ui.item.hasClass('ui-draggable')) {
						ui.item.draggable('destroy');
					}
					// AJAX action to remove the item from the form
					if (ui.item.hasClass('deleting')) {
						if (ui.item.hasClass("new-widget")) {
							ui.item.remove();
							return;
						}
						var iid;
						if (ui.item.children(".field").length) {
							iid = ui.item.children(".field").attr("id").substr("archetypes-fieldname-".length);
						} else {
							iid = ui.item.children(".PFGFieldsetWidget").attr("id").substr("pfg-fieldsetname-".length);
						}
						$("img.ajax-loader").css('visibility', 'visible');
						ui.item.remove();	// remove the original item (from the DOM and thus the form)
						$.post("removeFieldFromForm", {item_id: iid}, function () {
							$("img.ajax-loader").css('visibility', 'hidden');
						});
						return;
					}
				}
			});
		}
	};

}(jQuery));
