var pfgWidgets;

(function($) {
	
pfgWidgets = {
	
	init: function() {
		var item, target, table = $("#pfg-qetable tbody");
		var initPos, finalPos;
		var fixHelper = function(e, ui) {
		    ui.children().each(function() {
			  $(this).width($(this).width());
		     });
		    return ui;	
		};
		
		table.sortable({
		  	start: function (event, ui) {
		       ui.placeholder.html('<td>&nbsp;</td>');
			   initPos = pfgWidgets.getPos(ui.item);
		    },			
			helper: fixHelper,
		    handle: '> td.draggingHook',
		    cursor: 'move',
		    placeholder: 'placeholder',
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
		$("label.formQuestion").live('dblclick', function(e) {
			e.preventDefault();
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
		$("span.required").css('cursor', 'pointer');
		$("span.required").click(function() {
			var parentId = $(this).parent().attr('id').substr('archetypes-fieldname-'.length);
			$(this).css('color', '#000000');
			alert('Changed!');
		})
	},
	
	deinit: function() {
		$("label.formQuestion").die(); // removes event handlers setup by .live
	}
	
	
};

//$(document).ready(function($){ pfgWidgets.init(); });	
	
})(jQuery)