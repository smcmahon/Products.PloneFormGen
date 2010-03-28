// Support for PFG Quick Edit

var pfgQEdit = {};

// dnd support is a minor mod of Plone's dragdropreorder

pfgQEdit.dragging = null;
pfgQEdit.table = null;
pfgQEdit.rows = null;
pfgQEdit.targetId = null;

pfgQEdit.doDown = function(e) {
    var dragging =  jq(this).parents('.draggable:first');
    if (!dragging.length) return;
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
    if (!dragging) return;
    var target = this;
    if (!target) return;
    var targetId = jq(target).attr('id');

    if (targetId != dragging.attr('id')) {
        pfgQEdit.swapElements(jq(target), dragging);
        pfgQEdit.targetId = targetId;
    };
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
        jq(t).remove();
    };
    // odd and even are 0-based, so we want them the other way around
    parent.children('[id]:odd').addClass('even');
    parent.children('[id]:even').addClass('odd');
};

pfgQEdit.doUp = function(e) {
    var dragging = pfgQEdit.dragging;
    if (!dragging) return;

    dragging.removeClass("dragging");
    pfgQEdit.updatePositionOnServer();
    dragging._position = null;
    try {
        delete dragging._position;
    } catch(e) {};
    dragging = null;
    pfgQEdit.rows.unbind('mousemove', pfgQEdit.doDrag);
    return false;
};

pfgQEdit.updatePositionOnServer = function() {
    var dragging = pfgQEdit.dragging;
    if (!dragging) return;
    
    var args = {
      item_id: dragging.attr('id').substr('folder-contents-item-'.length),
      target_id: pfgQEdit.targetId.substr('folder-contents-item-'.length)
    };
    jQuery.post('reorderField', args)
};


pfgQEdit.addTable = function () {
    // add the table elements required for quick edit of fields

    jq("#pfg-fieldwrapper").children('.field').each(
        function () {
            var fname = this.id;
            if (fname.indexOf("archetypes-fieldname-") == 0) {                      
                fname = this.id.substr('archetypes-fieldname-'.length);
            } else {
                fname = this.id.substr('pfg-fieldsetname-'.length);
            }
            felem = jq('#'+this.id)
            if (felem.hasClass('pfgHidden')) {
                felem.append('<div class="pfgqemarkup">Hidden field: '+fname+'</div>')
            }
            felem.wrap(
                '<tr id="folder-contents-item-' + fname + '" class="draggable">'+
                '<td class="ofield"></td></tr>'
                );
            felem = felem.parent()
            felem.after('<td class="draggable draggingHook editHook">::</td>')
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
    jq("#pfg-fieldwrapper")
     .wrapInner(
         '<table id="pfg-qetable" class="listing" summary="Field listing"><tbody>'+
         '</tbody></table>'
         );
    jq("table#pfg-qetable").prepend(
        '<thead><tr>'+
        '<th>Field</th><th>Delete</th><th>Edit</th><th>Order</th>'+
        '</tr>'
        );
}

pfgQEdit.initDnD = function () {
  // tie to folder-contents drag drop
  table = '#pfg-qetable';
  pfgQEdit.table = jq(table);
  if (pfgQEdit.table.length) {
    pfgQEdit.rows = jq(table + " > tr," +
                              table + " > tbody > tr");
    jq( table + " td.draggable")
        .mousedown(pfgQEdit.doDown)
        .mouseup(pfgQEdit.doUp)
  }
}

pfgQEdit.qedit = function (e) {
  jq("#pfgqedit").hide();
  jq(".ArchetypesCaptchaWidget .captchaImage").replaceWith("<div>Captcha field hidden by form editor. Refresh to view it.</div>");
  // disable and dim input elements
  blurrable = jq("div.pfg-form .blurrable, div.pfg-form input")
  blurrable.each(
    function() {
      if (typeof this.disabled != "undefined") {
        this.disabled = true;
        }
      }
    );
  blurrable.css('opacity', 0.5);
  
  pfgQEdit.addTable();
  jq("div.pfg-form table tr:nth-child(even)").addClass('even');

  pfgQEdit.initDnD();

  jq("#pfgActionEdit").show();
  jq("#pfgThanksEdit").show();
  jq("#pfgnedit").fadeIn();
  
  if (jq.fn.prepOverlay) {
      jq('.editHook a[href$=edit]').prepOverlay(
          {
              subtype: 'ajax',
              filter: "#content",
              formselector: 'form[id$=base-edit]',
              noform: 'reload',
              closeselector:'[name=form.button.cancel]'
          }
      );
      jq('.editHook a[href$=delete_confirmation]').prepOverlay(
          {
              subtype: 'ajax',
              filter: "#content",
              formselector: 'form:has(input[value=Delete])',
              noform: 'reload',
              closeselector:'[name=form.button.Cancel]'
          }
      );
      jq('#plone-contentmenu-factories .actionMenuContent a[id^=form]').prepOverlay(
            {
                subtype: 'ajax',
                filter: "#content",
                formselector: 'form[id$=base-edit]',
                noform: 'reload',
                closeselector:'[name=form.button.Cancel]'
            }
      );
  }
}

pfgQEdit.stripTable = function () {
  // remove the table elements required for quick edit of fields

  // remove overlay divs
  jq("td.editHook a[rel^=#pb]").each(function () {
      var o = jq(this);
      jq(o.attr('rel')).remove();
  });
  
  // strip editHook cells
  jq("div.pfg-form td.editHook").remove();
  // find remaining cell contents
  var content = jq("#pfg-qetable td.ofield").children();
  // substitute for table
  jq("#pfg-qetable").after(content).remove();
  // hidden field descriptions
  jq("div.pfgqemarkup").remove();
}

pfgQEdit.noedit = function (e) {
  // turn off field editing
  jq("#pfgnedit").hide();

  if (pfgQEdit.dragging) pfgQEdit.doUp(false);

  pfgQEdit.stripTable();
  // enable all blurred elements
  blurrable = jq("div.pfg-form .blurrable, div.pfg-form input")
  blurrable.each(
    function() {
      if (typeof this.disabled != "undefined") this.disabled = false;
      }
    );
  blurrable.css('opacity', 1)

  jq("#pfgActionEdit").hide();
  jq("#pfgThanksEdit").hide();
  jq("#pfgqedit").fadeIn();
}

jq(document).ready(function() {
  jq("#pfgqedit").bind('click', pfgQEdit.qedit);
  jq("#pfgnedit").bind('click', pfgQEdit.noedit);
  
  jq("#pfgActionEdit input[name^=cbaction-]").bind('change', function (e) {
    jq.post('toggleActionActive', {item_id: this.name.substr('cbaction-'.length)});
  });
  jq("#pfgThanksEdit input[name^=thanksRadio]").bind('click', function (e) {
    jq.post('setThanksPage', {value: this.value});
  });

  if (document.URL.indexOf('?qedit') == -1) {
    jq("#content #pfgqedit").show();
  } else {
    pfgQEdit.qedit();
  }

})

