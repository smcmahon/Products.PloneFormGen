// Support for PFG Quick Edit

var pfgQEdit = {};

// dnd support is a minor mod of Plone's dragdropreorder

pfgQEdit.dragging = null;
pfgQEdit.table = null;
pfgQEdit.rows = null;
pfgQEdit.targetId = null;

pfgQEdit.doDown = function(e) {
    var dragging =  jQuery(this).parents('.draggable:first');
    if (!dragging.length) {return;}
    pfgQEdit.rows.mousemove(pfgQEdit.doDrag);

    pfgQEdit.dragging = dragging;
    dragging._position = pfgQEdit.getPos(dragging);
    dragging.addClass("dragging");
    return false;
};

pfgQEdit.getPos = function(node) {
    var pos = node.parent().children('.draggable').index(node[0]);
    return pos == -1 ? null : pos;
};

pfgQEdit.doDrag = function(e) {
    var dragging = pfgQEdit.dragging;
    if (!dragging) {return;}
    var target = this;
    if (!target) {return;}
    var targetId = jQuery(target).attr('id');

    if (targetId != dragging.attr('id')) {
        pfgQEdit.swapElements(jQuery(target), dragging);
        pfgQEdit.targetId = targetId;
    }
    return false;
};

pfgQEdit.swapElements = function(child1, child2) {
    var parent = child1.parent();
    var items = parent.children('[id]');
    items.removeClass('even').removeClass('odd');
    if (child1[0].swapNode) {
        // IE proprietary method
        child1[0].swapNode(child2[0]);
    } else {
        // swap the two elements, using a textnode as a position marker
        var t = parent[0].insertBefore(document.createTextNode(''),
                                       child1[0]);
        child1.insertBefore(child2);
        child2.insertBefore(t);
        jQuery(t).remove();
    }
    // odd and even are 0-based, so we want them the other way around
    parent.children('[id]:odd').addClass('even');
    parent.children('[id]:even').addClass('odd');
};

pfgQEdit.doUp = function(e) {
    var dragging = pfgQEdit.dragging;
    if (!dragging) {return;}

    dragging.removeClass("dragging");
    pfgQEdit.updatePositionOnServer();
    dragging._position = null;
    try {
        delete dragging._position;
    } catch(e) {}
    dragging = null;
    pfgQEdit.rows.unbind('mousemove', pfgQEdit.doDrag);
    return false;
};

pfgQEdit.updatePositionOnServer = function() {
    var dragging = pfgQEdit.dragging;
    if (!dragging) {return;}
    
    var args = {
      item_id: dragging.attr('id').substr('folder-contents-item-'.length),
      target_id: pfgQEdit.targetId.substr('folder-contents-item-'.length)
    };
    jQuery.post('reorderField', args);
};


pfgQEdit.addTable = function () {
    // add the table elements required for quick edit of fields

    jQuery("#pfg-fieldwrapper").children('.field').each(
        function () {
            var fname = this.id;
            if (fname.indexOf("archetypes-fieldname-") === 0) {                      
                fname = this.id.substr('archetypes-fieldname-'.length);
            } else {
                fname = this.id.substr('pfg-fieldsetname-'.length);
            }
            var felem = jQuery('#'+this.id);
            if (felem.hasClass('pfgHidden')) {
                felem.append('<div class="pfgqemarkup">Hidden field: '+fname+'</div>');
            }
            felem.wrap(
                '<tr id="folder-contents-item-' + fname + '" class="draggable">'+
                '<td class="ofield"></td></tr>'
                );
            felem = felem.parent();
            felem.before('<td class="draggable draggingHook editHook">⣿</td>');
            felem.after(
                '<td class="editHook">'+
                '<a href="' + fname + '/delete_confirmation" title="Delete Field">'+
                '<img src="delete_icon.gif" alt="Delete" /></a>'+
                '</td>'+
                '<td class="editHook">'+
                '<a href="' + fname + '/edit" title="Edit Field">'+
                '<img src="edit.gif" alt="Edit" /></a>'+
                '</td>'
                );
        }
    );
    jQuery("#pfg-fieldwrapper")
     .wrapInner(
         '<table id="pfg-qetable" class="listing" summary="Field listing"><tbody>'+
         '</tbody></table>'
         );
    jQuery("table#pfg-qetable").prepend(
        '<thead><tr>'+
        '<th>&nbsp;</th><th>Field</th><th class="editHook">Delete</th><th class="editHook">Edit</th>'+
        '</tr>'
        );
};

pfgQEdit.initDnD = function () {
  // tie to folder-contents drag drop
  var table = '#pfg-qetable';
  pfgQEdit.table = jQuery(table);
  if (pfgQEdit.table.length) {
    pfgQEdit.rows = jQuery(table + " > tr," +
                              table + " > tbody > tr");
    jQuery( table + " td.draggable")
        .mousedown(pfgQEdit.doDown)
        .mouseup(pfgQEdit.doUp);
  }
};

pfgQEdit.qedit = function (e) {
  jQuery("#pfgqedit").hide();
  jQuery(".ArchetypesCaptchaWidget .captchaImage").replaceWith("<div>Captcha field hidden by form editor. Refresh to view it.</div>");
  // disable and dim input elements
  var blurrable = jQuery("div.pfg-form .blurrable, div.pfg-form input");
  blurrable.each(
    function() {
      if (typeof this.disabled != "undefined") {
        this.disabled = true;
        }
      }
    );
  blurrable.css('opacity', 0.5);
  
  pfgQEdit.addTable();
  jQuery("div.pfg-form table tr:nth-child(even)").addClass('even');

  pfgQEdit.initDnD();

  jQuery("#pfgActionEdit").show();
  jQuery("#pfgThanksEdit").show();
  jQuery("#pfgnedit").fadeIn();
  
  if (jQuery.fn.prepOverlay) {
      jQuery('.editHook a[href$=edit]').prepOverlay(
          {
              subtype: 'ajax',
              filter: "#content",
              formselector: 'form[id$=base-edit]',
              noform:  function(){location.reload();},
              closeselector:'[name=form.button.cancel]'
          }
      );
      jQuery('.editHook a[href$=delete_confirmation]').prepOverlay(
          {
              subtype: 'ajax',
              filter: "#content",
              formselector: 'form#delete_confirmation',
              noform: function(){location.reload();},
              closeselector:'[name=form.button.Cancel]'
          }
      );
      jQuery('#plone-contentmenu-factories .actionMenuContent a[id^=form]').prepOverlay(
            {
                subtype: 'ajax',
                filter: "#content",
                formselector: 'form[id$=base-edit]',
                noform:  function(){location.reload();},
                closeselector:'[name=form.button.Cancel]'
            }
      );
  }
  location.hash = "qedit";
};

pfgQEdit.stripTable = function () {
  // remove the table elements required for quick edit of fields

  // remove overlay divs
  jQuery("td.editHook a[rel^=#pb]").each(function () {
      var o = jQuery(this);
      jQuery(o.attr('rel')).remove();
  });
  
  // strip editHook cells
  jQuery("div.pfg-form td.editHook").remove();
  // find remaining cell contents
  var content = jQuery("#pfg-qetable td.ofield").children();
  // substitute for table
  jQuery("#pfg-qetable").after(content).remove();
  // hidden field descriptions
  jQuery("div.pfgqemarkup").remove();
};

pfgQEdit.noedit = function (e) {
  // turn off field editing
  jQuery("#pfgnedit").hide();

  if (pfgQEdit.dragging) {pfgQEdit.doUp(false);}

  pfgQEdit.stripTable();
  // enable all blurred elements
  var blurrable = jQuery("div.pfg-form .blurrable, div.pfg-form input");
  blurrable.each(
    function() {
      if (typeof this.disabled != "undefined") {this.disabled = false;}
      }
    );
  blurrable.css('opacity', 1);

  jQuery("#pfgActionEdit").hide();
  jQuery("#pfgThanksEdit").hide();
  jQuery("#pfgqedit").fadeIn();
  location.hash = "";
};

jQuery(document).ready(function() {
  jQuery("#pfgqedit").bind('click', pfgQEdit.qedit);
  jQuery("#pfgnedit").bind('click', pfgQEdit.noedit);
  
  jQuery("#pfgActionEdit input[name^=cbaction-]").bind('change', function (e) {
    jQuery.post('toggleActionActive', {item_id: this.name.substr('cbaction-'.length)});
  });
  jQuery("#pfgThanksEdit input[name^=thanksRadio]").bind('click', function (e) {
    jQuery.post('setThanksPage', {value: this.value});
  });

  if (location.hash.indexOf('qedit') == -1) {
    jQuery("#content #pfgqedit").show();
  } else {
    pfgQEdit.qedit();
  }

});

