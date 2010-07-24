// Support for PFG Quick Edit

var pfgQEdit = {};

// dnd support is a minor mod of Plone's dragdropreorder

pfgQEdit.dragging = null;
pfgQEdit.table = null;
pfgQEdit.rows = null;

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
         /*   felem.wrap(
                '<tr id="folder-contents-item-' + fname + '" class="draggable">'+
                '<td class="ofield"></td></tr>'
                ); */
         //   felem = felem.parent();
			felem.addClass('qechild');
			felem.wrap("<div class='qefield'></div>");
            felem.before('<div class="draggable draggingHook editHook qechild"><span class="dhcenter"></span>::</div>');
            felem.after(
                '<div class="editHook qechild">'+ // 94px
	//			'<input type="checkbox" name="required-' + fname + '" title="Required?" />'+
				'<a href="' + fname + '/edit" title="Edit Field">'+
                '<img src="edit.gif" alt="Edit" /></a>'+
                '<a href="' + fname + '/delete_confirmation" title="Delete Field">'+
                '<img src="delete_icon.gif" alt="Delete" /></a>'+
                '</div>'
                );
        }
    );
    jQuery("#pfg-fieldwrapper")
     .wrapInner(
         '<div id="pfg-qetable" class="listing" summary="Field listing"></div>'
         );
    jQuery("div#pfg-qetable").before(
        '<div class="theader">'+
        '<div style="width: 8%">Order</div><div style="width: 50%">Field</div><div style="text-align:center; width: 26%">Actions</div>'+
        '</div>'
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

  jQuery("#pfgActionEdit").show();
  jQuery("#pfgThanksEdit").show();
  jQuery("#pfgnedit").fadeIn();
  
  if (jQuery.fn.prepOverlay) {
      jQuery('.editHook a[href$=edit]').prepOverlay(
          {
              subtype: 'ajax',
              filter: "#content",
        //      formselector: 'form[id$=base-edit]',
              noform: function(){location.reload();},
              closeselector:'[name=form.button.cancel]'
          }
      );
      jQuery('.editHook a[href$=delete_confirmation]').prepOverlay(
          {
              subtype: 'ajax',
              filter: "#content",
              formselector: 'form:has(input[value=Delete])',
              noform: function(){location.reload();},
              closeselector:'[name=form.button.Cancel]'
          }
      );
      jQuery('#plone-contentmenu-factories .actionMenuContent a[id^=form]').prepOverlay(
            {
                subtype: 'ajax',
                filter: "#content",
                formselector: 'form[id$=base-edit]',
                noform: function(){location.reload();},
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
  jQuery("div.editHook a[rel^=#pb]").each(function () {
      var o = jQuery(this);
      jQuery(o.attr('rel')).remove();
  });
  
  // strip editHook cells
  jQuery("div.pfg-form div.editHook").remove();

  // remove header and unfinished widgets
  jQuery("div.theader").remove();
  jQuery('#pfg-qetable div.widget').remove();

  // find remaining cell contents
  var content = jQuery("#pfg-qetable div.qefield").children();
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

