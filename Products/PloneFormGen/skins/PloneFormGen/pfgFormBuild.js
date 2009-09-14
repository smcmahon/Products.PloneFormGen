// pdgFormBuild class
var pfgFormBuild = {};

pfgFormBuild.blankPlaceHolder = null;
pfgFormBuild.selectedfield = null;
pfgFormBuild.form = null;
pfgFormBuild.fieldstable = null;
pfgFormBuild.fields = null;
pfgFormBuild.actions = null;
pfgFormBuild.thanks = null;
pfgFormBuild.controls = null;
pfgFormBuild.helperjs = null;
pfgFormBuild.helpercss = null;
pfgFormBuild.baseurl = null;

pfgFormBuild.initialize = function() {
    this.form = jq("#fgform");
    this.fieldstable = jq("#fgfields");
    this.fields = this.fieldstable.children(".fgfield-wrapper");
    this.controls = jq("#fgformcontrols");
    this.actions = jq("#pfgActionEdit");
    this.thanks = jq("#pfgThanksEdit");
    this.selectedfield = null;
    this.helperjs = [];
    this.helpercss = [];

    //Create a blank place holder (use for add object)
    var divTag = document.createElement("div");
    divTag.id = "fgfield-blankspaceholder";
    divTag.className ="fgfield-placeholder";
    divTag.style.display = "none";
    divTag.innerHTML = "";
    document.body.appendChild(divTag);
    this.blankPlaceHolder = jq("#fgfield-blankspaceholder");

    //Make form dropable (receive other item than fields)
//    this.form.droppable({
//        accept : ".addableItem-fgadapter, .addableItem-fgthanker",
//        drop : function (event, ui){
//                    var drag = ui.draggable;
//                    var fieldtype = drag.attr("id").substr("addableItem-".length);
//                    pfgFormBuild.addField(fieldtype, jq(this));
//                    pfgFormBuild.blankPlaceHolder.css("display", "none");
//                    //Silly fix for propagation problem: Disable drop on parent
//                    jq(this).parents(".fgfield-wrapper").droppable('enable');
//                    return false;
//                },
//        over : function (event, ui) {
//                },
//        out : function (event, ui) {
//                }
//    });

    //Make fields sortable
    jq(".fgfield-sortable").each(function() {
         pfgFormBuild.makeSortable(jq(this));
    });

    //Bind switch buttons
    jq("#switch-fgform").bind("click", this.switchToForm);
    jq("#switch-fgother").bind("click", this.switchToOther);

    //Add fields' bindings
    for (var i = 0; i < this.fields.length; i++) {
        var field = jq(this.fields[i]);
        this.addEventHandlers(field);
    }
    this.fieldstable.find(".fgfield-blank").each(function() {
         pfgFormBuild.makeDroppable(jq(this));
    });
    //reindex fieldlist
    this._reindexFieldList();
}

//Add event handler for field's buttons
pfgFormBuild.addEventHandlers = function(field) {

    var fieldview = field.children(".fgfield-view-wrapper")
    var editbuttons = field.children(".fgfield-editbuttons");
    var fieldedit = field.children(".fgfield-edit-wrapper");

    //Make dropable
    pfgFormBuild.makeDroppable(field);
    
    //Focus + select
    field.hover(
        function(event){
            pfgFormBuild.focus(jq(this));
        },
        function(event){
            pfgFormBuild.unfocus(jq(this));
        });

    fieldview.bind("click", function(event){
        //We just bind fgfield-view with click event
        //to avoid double event handling at this and editbuttons
        var field = jq(event.currentTarget).parents(".fgfield-wrapper:first");
        if (pfgFormBuild.getSelect(field))
            pfgFormBuild.unselect();
        else
            pfgFormBuild.select(field);
        return false;
    });

    //Copy/Edit/Delete buttons
    editbuttons.children(".fgfield-editbutton-edit").bind("click", function(event){
        var field = jq(event.currentTarget).parent(".fgfield-editbuttons").parent(".fgfield-wrapper");
        if (!pfgFormBuild.getShowEdit(field)) {
            //If not showed then show 
            pfgFormBuild.select(field);
            pfgFormBuild.showEdit(field);
        } 
        else {
            pfgFormBuild.hideEdit(field);
        }
        return false;
    });
    editbuttons.children(".fgfield-editbutton-copy").bind("click", function(event){
        var field = jq(event.currentTarget).parents(".fgfield-wrapper:first");
        pfgFormBuild.copyField(field);
        return false;
    });
    editbuttons.children(".fgfield-editbutton-delete").bind("click", function(event){
        var field = jq(event.currentTarget).parents(".fgfield-wrapper:first");
        pfgFormBuild.deleteField(field);
        return false;
    });
    fieldedit.find(".fgfield-formbutton-save").bind("click", function(event){
        var field = jq(event.currentTarget).parents(".fgfield-wrapper:first");
        pfgFormBuild.saveField(field);
        return false;
    });
    fieldedit.find(".fgfield-formbutton-cancel").bind("click", function(event){
        var field = jq(event.currentTarget).parents(".fgfield-wrapper:first");
        pfgFormBuild.unselect();
        return false;
    });

    var fieldset = fieldview.find(".fgfield-fieldset:first")
    if (fieldset.length > 0) {
        //This means we caught a fieldset
        var children = fieldset.children(".fgfield-wrapper");
        for (var i = 0; i < children.length; i++) {
            pfgFormBuild.addEventHandlers(jq(children[i]));
        }
        this.makeSortable(fieldset);
        this.makeDroppable(fieldset.children(".fgfield-blank"));
    } 
    else {
        //This means we caught a field. Disable input is needed then.
        fieldview.find(":input:first").each( function(i) {
            jq(this).get(0).disabled = true;
        });
    }
}

pfgFormBuild.makeSortable = function(fieldset) {
    fieldset.sortable({
        item : ".fgfield-wrapper",
        revert : false,
        connectWith: ".fgfield-sortable",
        delay : 100,
        //forcePlaceholderSize : true,
        placeholder : "fgfield-placeholder",
//        tolerance: 'pointer',
        over : function (event, element) {
            event.stopPropagation();
        },
        helper : function (event, element) {
            //Custom helper: + Clone the field view only (not the whole object)
            //               + Remove all decorator class (highlight, focus...) 
            var newDom = element.children(".fgfield-view-wrapper").clone();
            newDom.removeClass("fgfield-highlight");
            newDom.removeClass("fgfield-focus");
            newDom.addClass("fgfield-helper");
            return newDom[0]
        },
        stop: function(event, ui) { 
            //When stop: Call move function
            var field = ui.item;
            var pos = pfgFormBuild.getPosition(field);
            var parent = field.parents(".fgfield-wrapper:first");
            var containerpath = '';
            if (parent.length > 0) 
                containerpath = pfgFormBuild.getFieldPath(parent);
            result = pfgFormBuild.moveField(jq(field), containerpath, pos);
            if (result.status == "failure")
                jq(this).sortable("cancel");
            event.stopPropagation();
        }
    });
}

pfgFormBuild.makeDroppable = function(field) {
    field.droppable({
        accept : ".addableItem-fgfield",
        drop : function (event, ui){
                    var drag = ui.draggable;
                    var fieldtype = drag.attr("id").substr("addableItem-".length);
                    pfgFormBuild.addField(fieldtype, jq(this));
                    pfgFormBuild.blankPlaceHolder.css("display", "none");
                    //Silly fix for propagation problem: Disable drop on parent
                    jq(this).parents(".fgfield-wrapper").droppable('enable');
                    return false;
                },
        over : function (event, ui) {
                    //Silly fix for propagation problem: Disable drop on parent
                    jq(this).parents(".fgfield-wrapper").droppable('disable');
                    event.stopPropagation();
                    var placeholder = pfgFormBuild.blankPlaceHolder;
                    jq(this).before(placeholder[0]);
                    placeholder.css("display", "block");
                    return false;
                },
        out : function (event, ui) {
                    //Silly fix for propagation problem: Disable drop on parent
                    jq(this).parents(".fgfield-wrapper").droppable('enable');
                    pfgFormBuild.blankPlaceHolder.css("display", "none");
                }
    });
}


pfgFormBuild.switchToForm = function(){
    //Switch to form (field) build tab
    jq("#switch-fgform").css("display", "none");
    jq("#switch-fgother").css("display", "block");
    jq("#fgform").css("display", "none");
    jq("#fgother").css("display", "block");
}

pfgFormBuild.switchToOther = function(){
    //Switch to other tab (adapter, thankspage ...)
    jq("#switch-fgform").css("display", "block");
    jq("#switch-fgother").css("display", "none");
    jq("#fgform").css("display", "block");
    jq("#fgother").css("display", "none");
}

pfgFormBuild.getFieldPath = function (field){
    //Get fieldPath
    return field.attr("id").substr("fgfield-".length);
}

pfgFormBuild.getFieldByPath = function(fieldPath) {
    //Return jq wrapper of field object or null if not found
    var field = this.fieldstable.find("#fgfield-%s" %fieldPath);
    if (field.length) return field;
    return null;
}

pfgFormBuild.getPosition = function(field) {
    //Get field"s position
    var pos = field.parent().children('.fgfield-wrapper').index(field.get(0));
    return pos;
}

pfgFormBuild._reindexField_recurse = function(fieldtable) {
    //Update the position of available field
    var fields = fieldtable.children(".fgfield-wrapper");
    fields.each(function(i) {
        var field = jq(this);
        field.attr("index", i);
        var fieldset = field.find(".fgfield-fieldset:first");
        if (fieldset.length > 0){
            pfgFormBuild._reindexField_recurse(fieldset);
        }
    });
}

pfgFormBuild._reindexFieldList = function() {
    //Update the field list
    this.fields = this.fieldstable.children(".fgfield-wrapper");
    this._reindexField_recurse(this.fieldstable)
}

pfgFormBuild.focus = function(field) {
    //Focus on a field
    if (this.selectedfield != null) 
        //If we already selected a field, then we need to disable focus
        return;
    //Focus means focus to only one element
    var focuses = this.fieldstable.find(".fgfield-focus");
    if (focuses.length > 0)
        for (var i = 0; i < focuses.length; i++) {
            pfgFormBuild.unfocus(jq(focuses[i]));
        };
    field.addClass("fgfield-focus");
    field.children(".fgfield-editbuttons").css("display", "block"); 
}

pfgFormBuild.unfocus = function(field) {
    //Unfocus on a field
    field.removeClass("fgfield-focus");
    if (this.selectedfield == null)
        //Dangerous set, should only call when not in select
        field.children(".fgfield-editbuttons").css("display", "none"); 
}

pfgFormBuild.getSelect = function(field) {
    //Is the field shows selected or not
    return (pfgFormBuild.selectedfield != null && pfgFormBuild.selectedfield[0] == field[0])
}

pfgFormBuild.select = function(field) {
    if (this.selectedfield != null) 
        if (this.getShowEdit(this.selectedfield)) {
            parents = this.selectedfield.parents(".fgfield-wrapper");
            for (var i = 0; i < parents.length; i++)
                if (jq(parents[i]).attr("id") == field.attr("id"))
                    return false;
        }
        //If we already selected a field, then we need to unselect first
        this.unselect();
    //We also need to unfocus all focused fields    
    this.fieldstable.children(".fgfield-wrapper fgfield-focus").each(function(i) {
        pfgFormBuild.unfocus(jq(this));
    });
    //Select the field
    field.addClass("fgfield-selected");
    field.children(".fgfield-view-wrapper").addClass("fgfield-highlight");
    field.children(".fgfield-editbuttons").css("display", "block"); 
    this.selectedfield=field;
    //Remove focus classes if have
    field.removeClass("fgfield-focus");
}

pfgFormBuild.unselect = function() {
    if (this.selectedfield == null)
        return;
    //Free the select field
    var field = this.selectedfield;
    field.removeClass("fgfield-selected");
    field.children(".fgfield-view-wrapper").removeClass("fgfield-highlight");
    field.children(".fgfield-editbuttons").css("display", "none"); 
    pfgFormBuild.hideEdit(field)
    this.selectedfield=null;
    //Enable sortable and draggable
    this.fieldstable.sortable("enable")
}

pfgFormBuild.getShowEdit = function(field) {
    //Is the field shows edit or not
    return (field.children(".fgfield-edit-wrapper").css("display") == "block");
}

pfgFormBuild.showEdit = function(field) {
    field.children(".fgfield-edit-wrapper").css("display", "block");
    //Disable sortable and draggable
    this.fieldstable.sortable("disable")
}

pfgFormBuild.hideEdit = function(field) {
    field.children(".fgfield-edit-wrapper").css("display", "none");
}

pfgFormBuild.getCss = function(url){
    //Load css on-demand

    //
    for (var i = 0; i < this.helperjs.length; i++)
        if (this.helperjs[i] == url) return true;

    if (document.createStyleSheet){
        document.createStyleSheet(this.baseURL + '/' + url);
    }
    else {
        var styleTag = document.createElement('link');
        jq(styleTag).attr({
            href    : this.baseURL + '/' + url,
            type    : 'text/css',
            media   : 'screen',
            rel     : 'stylesheet'
        }).appendTo(jq('head').get(0));
    }
    this.helpercss.push(url);
    return true;
}

pfgFormBuild.getJs = function(url){
    //Load js on-demand

    //
    for (var i = 0; i < this.helperjs.length; i++)
        if (this.helperjs[i] == url) return true;

    var result;
    jQuery.ajax({
        url: this.baseURL + '/' + url,
        error: function(request, statusmsg, errorthrow) {
            addPortalMessage("error", statusmsg);
            result = false;
        },
        success: function(result) {
            if (result.isOk == false) {
                msg = "Unable to load " + url + 
                      ". Some of UI functions may not work.";
                addPortalMessage("error", statusmsg);
                result = false;
            } else {
                pfgFormBuild.helperjs.push(url);
                result = true;
            }
        },
        async: false,
        dataType: "script",
    });
    return result;
}

pfgFormBuild.addField = function(fieldtype, afterfield) {
    //Add new field before the afterfield
    var response;
    var data = {"fieldtype": fieldtype};
    var containerpath = "";
    if (afterfield != null) {
        var pos = this.getPosition(afterfield);
        data.position = pos;
        container = afterfield.parents(".fgfield-wrapper:first");
        if (container.length > 0) {
            containerpath = this.getFieldPath(container);
            data.containerpath = containerpath;
        }
    }
    response = jqPost("add", JSON.stringify(data));
    if (response == null)
        return false;
    if (response.status == "success") {
        //Create new field
        var newfield = jq("<div/>");
        newfield.attr("class", "fgfield-wrapper");
        newfield.attr("id", "fgfield-" + response.data.fieldpath);
        newfield.html(response.data.html);
        //Add helper css and js
        var css = response.data.css;
        for (var i = 0; i < css.length; i ++)
            this.getCss(css[i]);
        var js = response.data.js;
        for (var i = 0; i < js.length; i ++)
            this.getJs(js[i]);
        //Add to position pos
        if (afterfield != null) {
            afterfield.before(newfield);
        }
        else {
            //Add to the end of the form
            this.fields[this.fields.length-1].after(newfield);
        }
        this.addEventHandlers(newfield);
        newfield.parents(".fgfield-fieldset").sortable('refresh');
        this.fieldstable.sortable('refresh');
        this._reindexFieldList();
        //Do select the new field
        this.select(newfield);
        this.showEdit(newfield);
        return true;
    }
    return false;
}

pfgFormBuild.copyField = function(field) {
    //Clone the current field
    var data = {"fieldpath": field.attr("id").substr("fgfield-".length)};
    var response = jqPost("copy", JSON.stringify(data));    
    if (response == null)
        return false;
    if (response.status == "success") {
        //Create new field
        var newfield = jq("<div/>");
        newfield.attr("class", "fgfield-wrapper");
        var fieldpath = this.getFieldPath(field);
        fieldpath = fieldpath.substr(0, fieldpath.lastIndexOf(":")) + response.data.fieldid;
        newfield.attr("id", "fgfield-" + fieldpath);
        newfield.html(response.data.html);
        //Add right after current field
        field.after(newfield);
        this.addEventHandlers(newfield);
        newfield.parents(".fgfield-fieldset").sortable('refresh');
        this.fieldstable.sortable('refresh');
        this._reindexFieldList();
        //Do select the new field
        this.select(newfield);
        return true;
    }
    return false;
}

pfgFormBuild.moveField = function(field, newpath, newpos) {
    var data = {"fieldpath" : this.getFieldPath(field),
                "containerpath": newpath,
                "position" : newpos
               };
    var response =  jqPost("move", JSON.stringify(data));
    if (response == null)
        return false;
    if (response.status == "success") {
        var oldpath = this.getFieldPath(field);
        var fieldid = oldpath;
        var pos = oldpath.lastIndexOf(":");
        if (pos >= 0)
            fieldid = oldpath.substr(pos+1);
        if (newpath != "")
            field.attr("id", "fgfield-" + newpath + ":" + fieldid)
        else
            field.attr("id", "fgfield-" + fieldid)
        this._reindexFieldList();
        return true;
    }
    return false
}

pfgFormBuild.deleteField = function(field) {
    var data = {"fieldpath" : this.getFieldPath(field)};
    var response =  jqPost("delete", JSON.stringify(data));
    if (response == null)
        return false;
    if (response.status == "success") {
        //Unselect it we're selecting something
        this.unselect();
        //Selfdestruct
        field.remove();      
        this.fieldstable.sortable('refresh');
        this._reindexFieldList();
    }
    return false;
}

pfgFormBuild.saveField = function(field) {
    var data = {"fieldpath" : this.getFieldPath(field), 
                "poststr" : field.find(":input").serialize()
               };
    var response =  jqPost("save", JSON.stringify(data));
    if (response == null)
        return false;
    //Update the field
    field.html(response.data.html);
    this.addEventHandlers(field);
    field.parents('.fgfield-fieldset').sortable('refresh');
    this.fieldstable.sortable('refresh');
    this._reindexFieldList();
    this.select(field);

    if (response.status != "success") {
        //if not success: Show the edit form (with errors)
        this.showEdit(field);
        return true;
    }
    return false;
}
