// Support for PFG Quick Edit

var pfgQEdit = {};

// dnd support is a minor mod of Plone's dragdropreorder

pfgQEdit.dragging = null;
pfgQEdit.table = null;
pfgQEdit.rows = null;
pfgQEdit.targetId = null;
pfgQEdit.endPos = null;
var widgetsInit = false;

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
            felem = jQuery('#'+this.id);
            if (felem.hasClass('pfgHidden')) {
                felem.append('<div class="pfgqemarkup">Hidden field: '+fname+'</div>');
            }
            felem.wrap(
                '<tr id="folder-contents-item-' + fname + '" class="draggable">'+
                '<td class="ofield" style="width: 50%"></td></tr>'
                );
            felem = felem.parent();
            felem.after('<td class="draggable draggingHook editHook" style="width:10%"><div style="width: 100%">::</div></td>');
            felem.after(
                '<td class="editHook" style="width: 40%"><div style="width: 100%">'+ // 94px
				'<input type="checkbox" name="required-' + fname + '" title="Required?" />'+
				'<a href="' + fname + '/edit" title="Edit Field">'+
                '<img src="edit.gif" alt="Edit" /></a>'+
                '<a href="' + fname + '/delete_confirmation" title="Delete Field">'+
                '<img src="delete_icon.gif" alt="Delete" /></a>'+
                '</div></td>'
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
        '<th>Field</th><th style="text-align:center">Actions</th><th>Order</th>'+
        '</tr>'
        );
};

pfgQEdit.qedit = function (e) {
  jQuery("#pfgqedit").hide();
  // hide the error messages
  jQuery(".error").hide();
  // show widgets manager
  jQuery("#pfgWidgetWrapper").fadeIn();

  jQuery(".ArchetypesCaptchaWidget .captchaImage").replaceWith("<div>Captcha field hidden by form editor. Refresh to view it.</div>");
  // disable and dim input elements
  blurrable = jQuery("div.pfg-form .blurrable, div.pfg-form input");
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

  jQuery("#pfgActionEdit").show();
  jQuery("#pfgThanksEdit").show();
  jQuery("#pfgnedit").fadeIn();
  
  if (jQuery.fn.prepOverlay) {
      jQuery('.editHook a[href$=edit]').prepOverlay(
          {
              subtype: 'ajax',
              filter: "#content",
        //      formselector: 'form[id$=base-edit]',
              noform: 'reload',
              closeselector:'[name=form.button.cancel]'
          }
      );
      jQuery('.editHook a[href$=delete_confirmation]').prepOverlay(
          {
              subtype: 'ajax',
              filter: "#content",
              formselector: 'form:has(input[value=Delete])',
              noform: 'reload',
              closeselector:'[name=form.button.Cancel]'
          }
      );
      jQuery('#plone-contentmenu-factories .actionMenuContent a[id^=form]').prepOverlay(
            {
                subtype: 'ajax',
                filter: "#content",
                formselector: 'form[id$=base-edit]',
                noform: 'reload',
                closeselector:'[name=form.button.Cancel]'
            }
      );
  }
  location.hash = "qedit";
  pfgWidgets.init();

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
  // hide widgets manager
  jQuery("#pfgWidgetWrapper").hide();

  pfgQEdit.stripTable();
  // enable all blurred elements
  blurrable = jQuery("div.pfg-form .blurrable, div.pfg-form input");
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
  pfgWidgets.deinit();
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
    jQuery("div#pfgqedit").show();
  } else {
    pfgQEdit.qedit();
  }

});

