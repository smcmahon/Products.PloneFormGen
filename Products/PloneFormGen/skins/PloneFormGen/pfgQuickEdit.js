// Support for PFG Quick Edit

var pfgQEdit = {};
var pfgHaveDnD = typeof(ploneDnDReorder) != typeof(undefined)

pfgQEdit.addTable = function () {
    // add the table elements required for quick edit of fields
    jq("#pfg-fieldwrapper div[id^=archetypes-fieldname-]").each(
        function () {
            fname = this.id.substr('folder-contents-item-'.length);
            felem = jq('#'+this.id)
            felem.wrap(
                '<tr id="folder-contents-item-' + fname + '" class="draggable">'+
                '<td></td></tr>'
                );
            felem = felem.parent()
            if (pfgHaveDnD) {
              felem.after('<td class="draggable draggingHook editHook">::</td>')
            }
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
  ploneDnDReorder.table = jq(table);
  if (ploneDnDReorder.table.length) {
    ploneDnDReorder.rows = jq(table + " > tr," +
                              table + " > tbody > tr");
    jq( table + " td.draggable")
        .mousedown(ploneDnDReorder.doDown)
        .mouseup(ploneDnDReorder.doUp)
  }
}

pfgQEdit.qedit = function (e) {
  jq("#pfgqedit").hide();
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

  if (pfgHaveDnD) {
    pfgQEdit.initDnD();
  }

  jq("#pfgActionEdit").show();
  jq("#pfgThanksEdit").show();
  jq("#pfgnedit").fadeIn();
}

pfgQEdit.stripTable = function () {
  // remove the table elements required for quick edit of fields

  // strip editHook cells
  jq("div.pfg-form td.editHook").remove();
  // clone remaining cell contents
  var content = jq("#pfg-qetable td").children().clone();
  // substitute for table
  jq("#pfg-qetable").after(content).remove();
}

pfgQEdit.noedit = function (e) {
  // turn on field editing
  jq("#pfgnedit").hide();

  if (pfgHaveDnD && ploneDnDReorder.dragging) ploneDnDReorder.doUp(false);

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
    pfgQEdit.qedit()
  }
})

