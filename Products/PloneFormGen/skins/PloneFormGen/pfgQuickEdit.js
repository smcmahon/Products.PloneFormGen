// Support for PFG Quick Edit

var pfgQEdit = {};

pfgQEdit.addTable = function () {
    // add the table elements required for quick edit of fields
    jq("#pfg-fieldwrapper div[id^=archetypes-fieldname-]").each(
        function () {
            fname = this.id.substr('folder-contents-item-'.length);
            felem = jq('#'+this.id)
            felem.wrap('<tr id="folder-contents-item-' + fname + '" class="draggable"><td></td></tr>');
            felem = felem.parent()
            felem.after('<td class="draggable draggingHook editHook">::</td>')
            felem.after('<td class="editHook"><a href="' + fname + '/edit"><img src="edit.gif"</a></td>')
        }
    );
    jq("#pfg-fieldwrapper")
     .wrapInner('<table id="pfg-qetable" class="listing" summary="Field listing"></thead><tbody></tbody></table>')
    jq("table#pfg-qetable").prepend('<thead><tr><th>Field</th><th>Edit</th><th>Order</th></tr>')
}

pfgQEdit.qedit = function () {
  jq("#pfgqedit").hide();
  // disable and dim input elements
  blurrable = jq("div.pfg-form .blurrable")
  blurrable.each(
    function() {
      if (typeof this.disabled != "undefined") {
        this.disabled = true;
        }
      }
    );
  blurrable.css('opacity', 0.5);
  
  pfgQEdit.addTable()
  jq("div.pfg-form table tr:nth-child(even)").addClass('even');

  // tie to folder-contents drag drop
  table = '#pfg-qetable'
  ploneDnDReorder.table = jq(table);
  if (ploneDnDReorder.table.length) {
    ploneDnDReorder.rows = jq(table + " > tr," +
                              table + " > tbody > tr");
    jq( table + " td.draggable")
        .mousedown(ploneDnDReorder.doDown)
        .mouseup(ploneDnDReorder.doUp)
  }
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

pfgQEdit.noedit = function () {
  // turn on field editing
  jq("#pfgnedit").hide();

  if (ploneDnDReorder.dragging) ploneDnDReorder.doUp(false);


  pfgQEdit.stripTable()
  // enable all blurred elements
  blurrable = jq("div.pfg-form .blurrable")
  blurrable.each(
    function() {
      if (typeof this.disabled != "undefined") this.disabled = false;
      }
    );
  blurrable.css('opacity', 1)

  jq("#pfgqedit").fadeIn();
}

jq(document).ready(function() {
  jq("#pfgqedit").bind('click', pfgQEdit.qedit);
  jq("#pfgnedit").bind('click', pfgQEdit.noedit);
  jq("#content #pfgqedit").show();
})

