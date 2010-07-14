var pfgWidgets;

(function($) {
	
pfgWidgets = {
	
	init: function() {
		var item, target, table = $("#pfg-qetable");
		var initPos, finalPos;
		var fixHelper = function(e, ui) {
		    ui.children().each(function()  {
	//		  $(this).clone(true);
			  $(this).width($(this).width());
		    });
		    return ui;	
		};
		
		$("div.qefield").each(function() {
			$(this).height($(this).height()); // workaround for children's height not being able to set using %s
		})
		
		table.sortable({
			start: function (event, ui) {
		//       ui.placeholder.html('<td>&nbsp;</td><td class="placeholder">&nbsp;</td>');
			   ui.placeholder.height(ui.item.height())
			   initPos = pfgWidgets.getPos(ui.item);	
		    },			
			helper: 'clone',
			items: '.qefield',
		    handle: '> div.draggingHook',
//		    cursor: 'move',
		    placeholder: 'placeholder',
			containment: 'document',
		    update: function(e, ui) {
				if (ui.item.is("div.widget")) {
					// perform the operations on the newly dragged element from the widgets manager
					var item = ui.item;
					$(item).addClass("qechild");
					$(item).wrap("<div class='qefield'></div>"); // on the fly wrapping with necessary table elements
					$(item).before("<div class='draggable draggingHook editHook qechild'>::</td>");
					$(item).after('<div class="editHook qechild">&nbsp;</td>');
					$(item).children("div.widget-inside").slideDown();
				} 
				else {
					finalPos = pfgWidgets.getPos(ui.item)
					if (initPos > finalPos) { // we came from lower rows
						target = $(ui.item).next()
					}
					else { // we came from upper rows
						target = $(ui.item).prev()
					}
					item = $(ui.item).find(".field").attr('id').substr('folder-contents-item-'.length)
					target = target.find(".field").attr('id').substr('folder-contents-item-'.length)
					pfgWidgets.updatePositionOnServer(item, target)
				}
			}
		});
		
		this.editTitles();
		this.toggleRequired();
		this.limitFields();
		
		$("div.widget").tooltip({
			tip: ".tooltip",
			position: "top center",
			relative: "true",
			offset: [-3, 0],
			effect: "fade",
			predelay: 700,
			opacity: 0.9
		});
		
		$("div.widget").draggable({
		  connectToSortable: "#pfg-qetable",
		  helper: 'clone',
		  containment: 'document'
		})
		
		/* handle AJAX error */
		$(document).ajaxError(function(event, request, settings) {
			$("img.ajax-loader").css('visibility', 'hidden');
			alert("The has been an AJAX error on requesting page: " + settings.url);
		});
	},
	
	getPos: function(node) {
	    var pos = node.parent().children('.qefield').index(node[0]);
	    return pos == -1 ? null : pos;
	},
	
	updatePositionOnServer: function(i, t) {
		if (i && t) {
			$("img.ajax-loader").css('visibility', 'visible');
		}
	    var args = {
	      item_id: i,
	      target_id: t
	    };
	    $.post('reorderField', args, function() { $("img.ajax-loader").css('visibility', 'hidden')} )
	},
	
	editTitles: function() {
		// first we create a new dynamic node (which will be used to edit content)
		var node = document.createElement("input");
		node.setAttribute('name', "change");
		node.setAttribute("type", "text");
		
		// then we attach a new event to label fields
		$("#pfg-qetable label.formQuestion").live('dblclick', function(e) {
			var content = $(this).text();
			var tmpfor = $(this).attr('for');
			$(this).append(node);
			$(this).html($(node).val(content));
			$(node).fadeIn();
			$(this).children().unwrap();
			node.focus(); node.select();
		 
			$(node).blur(function(e) {
		  		$(this).wrap("<label class='formQuestion' for='"+ tmpfor +"'></label>");
		  		$(this).parent().html($(this).val())
				var args = {
					item_id: tmpfor,
					title: $(this).val()
				};
				if (args['title']!=content) { // only update if we actually changed the field
					$("img.ajax-loader").css('visibility', 'visible');					
					$.post("updateFieldTitle",args, function() { $("img.ajax-loader").css('visibility', 'hidden')});
				}
		 	});
		});

	},
	
	toggleRequired: function() {
		var requiredParent = $("span.required").parent();
		$(requiredParent).each(function () {
			var parentId = $(this).attr('id').substr('archetypes-fieldname-'.length);
			$("#pfg-qetable").find("input[name=required-"+ parentId + "]").attr("checked", "checked");			
		});
		
		$("#pfg-qetable").find("input[name^=required-]").bind('change', function(event) {
		//	event.preventDefault();
			var id = $(this).attr('name').substr('required-'.length);
			var requiredSpan = $('#archetypes-fieldname-'+id).find("span.required");
			$("img.ajax-loader").css('visibility', 'visible');				
			$.post('toggleRequired', {item_id: id }, function() {
				// we put the required actions after we are sure the toggle is done on the server!
				if (requiredSpan.length) { // remove the little tile and set input's required attr
					requiredSpan.fadeOut(1000).remove();
					$('#archetypes-fieldname-'+id).find('[name^='+id+']').removeAttr("required");
				}
				else {
					var spel = document.createElement("span");	// create a new span element to mark required fields
					$(spel).attr("class", "required");
				 	$(spel).css('color','rgb(255, 0, 0)');
					$(spel).html("            ■");
					$('#archetypes-fieldname-'+id+' label.formQuestion').after($(spel).fadeIn(1000));
					$('#archetypes-fieldname-'+id).find('[name^='+id+']').attr("required", "required")
				}
				$("img.ajax-loader").css('visibility', 'hidden')
			});
			return true;
		});
	},
	
	limitFields: function() {
		$("div.w-field").slice(7).hide();
		if (!$(".more").length)			// if there's no "More fields..." link, create it.
			$("div.w-field:not(:hidden):last").after("<div class='more'>More fields...</div>");

		$(".more").toggle(
			function() {
				$(this).hide();
				$("div.widgets div.w-field").slice(7).fadeIn();
				$(this).insertAfter("div.w-field:not(:hidden):last");
				$(this).html("Less fields...").show();
			},
			function() {
				$(this).hide();
				$("div.widgets div.w-field").slice(7).fadeOut();
				$(this).insertAfter("div.w-field:not(:hidden):last");
				$(this).html("More fields...").show();
			}
		)
	},
	
	deinit: function() {
		$("label.formQuestion").die(); // removes event handlers setup by .live
		$(".more").remove();		// remove the item with bounded events to avoid conflict when "quick-edit mode" is called again
	}
	
	
};

//$(document).ready(function($){ pfgWidgets.init(); });	
	
})(jQuery)