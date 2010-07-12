var pfgWidgets;

(function($) {
	
pfgWidgets = {
	
	init: function() {
		var item, target, table = $("#pfg-qetable tbody");
		var initPos, finalPos;
		var fixHelper = function(e, ui) {
		    ui.children().each(function()  {
			  $(this).clone(true);
	//		  $(this).width($(this).width());
		    });
		    return ui;	
		};
		
		table.sortable({
		  	start: function (event, ui) {
		       ui.placeholder.html('<td class="placeholder">&nbsp;</td>');
			   initPos = pfgWidgets.getPos(ui.item);
		    },			
			helper: 'clone',
		    handle: '> td.draggingHook',
		    cursor: 'move',
		    placeholder: 'placeholder',
			containment: 'document',
		    update: function(e, ui) {
				finalPos = pfgWidgets.getPos(ui.item)
				if (initPos > finalPos) { // we came from lower rows
					target = $(ui.item).next()
				}
				else { // we came from upper rows
					target = $(ui.item).prev()
				}
				item = $(ui.item).attr('id').substr('folder-contents-item-'.length)
				target = target.attr('id').substr('folder-contents-item-'.length)
				pfgWidgets.updatePositionOnServer(item, target)
			}
		});
		
		this.editTitles();
		this.toggleRequired();
		/* handle AJAX error */
		$(document).ajaxError(function(event, request, settings) {
			$("img.ajax-loader").css('visibility', 'hidden');
			alert("The has been an AJAX error on requesting page: " + settings.url);
		});
	},
	
	getPos: function(node) {
	    var pos = node.parent().children('.draggable').index(node[0]);
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
//					requiredSpan.remove();
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
	
	deinit: function() {
		$("label.formQuestion").die(); // removes event handlers setup by .live
	}
	
	
};

//$(document).ready(function($){ pfgWidgets.init(); });	
	
})(jQuery)