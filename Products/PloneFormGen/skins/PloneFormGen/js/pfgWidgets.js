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
	},
	
	getPos: function(node) {
	    var pos = node.parent().children('.draggable').index(node[0]);
	    return pos == -1 ? null : pos;
	},
	
	updatePositionOnServer: function(i, t) {
	    var args = {
	      item_id: i,
	      target_id: t
	    };
	    $.post('reorderField', args)
	}
	
	
};

//$(document).ready(function($){ pfgWidgets.init(); });	
	
})(jQuery)