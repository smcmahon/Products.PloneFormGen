// Support for PFG Quick Edit

var pfgFormBuild = {};

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

