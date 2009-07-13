// pdgFormBuild class
var pfgFormBuild = {};

pfgFormBuild.selectedfield = null;
pfgFormBuild.form = null;
pfgFormBuild.fieldstable = null;
pfgFormBuild.fields = null;
pfgFormBuild.actions = null;
pfgFormBuild.thanks = null;
pfgFormBuild.controls = null;

pfgFormBuild.initialize = function() {
    this.form = jq("#fgform");
    this.fieldstable = jq("#fgfields");
    this.fields = this.fieldstable.children(".fgfield-wrapper");
    this.controls = jq("#fgformcontrols");
    this.actions = jq("#pfgActionEdit");
    this.thanks = jq("#pfgThanksEdit");
    this.selectedfield = null;
    this.blankPlaceHolder = jq("#fgfield-blankspaceholder");

    //Make fields sortable
    this.fieldstable.sortable({
        item : ".fgfield-wrapper",
        revert : "false",
        forcePlaceholderSize : "true",
        placeholder : "fgfield-placeholder",
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
            var fieldid = field.attr("id").substr("fgfield-".length);
            var pos = pfgFormBuild.getPosition(field);
            result = pfgFormBuild.moveField(jq(field), pos);
            if (result.status == "failure")
                jq(this).sortable("cancel");
        }
    });

    //Add event handlers, make dropable
    for (var i = 0; i < this.fields.length; i++) {
        var field = jq(this.fields[i]);
        this.addEventHandlers(field);
        this.makeDropable(field);
    //Add fields' index
    }
    this._refreshFieldList();
}

//Add event handler for field's buttons
pfgFormBuild.addEventHandlers = function(field) {

    //Disable input
    field.attr("disabled", true);
    
    //Focus + select
    field.bind("mouseover", function(event){
        pfgFormBuild.focus(jq(event.currentTarget));
    });
    field.bind("mouseout", function(event){
        pfgFormBuild.unfocus(jq(event.currentTarget));
    });
    field.children(".fgfield-view-wrapper").bind("click", function(event){
        //We just bind fgfield-view with click event
        //to avoid double event handling at this and editbuttons
        var field = jq(event.currentTarget).parents(".fgfield-wrapper");
        if (pfgFormBuild.getSelect(field))
            pfgFormBuild.unselect();
        else
            pfgFormBuild.select(field)
    });

    //Copy/Edit/Delete buttons
    field.find(".fgfield-editbutton-edit").bind("click", function(event){
        var field = jq(event.currentTarget).parents(".fgfield-wrapper");
        if (!pfgFormBuild.getShowEdit(field)) {
            //If not showed then show 
            pfgFormBuild.select(field);
            pfgFormBuild.showEdit(field);
        } 
        else {
            pfgFormBuild.hideEdit(field);
        }
    });
    field.find(".fgfield-editbutton-copy").bind("click", function(event){
        var field = jq(event.currentTarget).parents(".fgfield-wrapper");
        pfgFormBuild.copyField(field);
    });
    field.find(".fgfield-editbutton-delete").bind("click", function(event){
        var field = jq(event.currentTarget).parents(".fgfield-wrapper");
        pfgFormBuild.deleteField(field);
    });
    field.find(".fgfield-formbutton-save").bind("click", function(event){
        var field = jq(event.currentTarget).parents(".fgfield-wrapper");
        pfgFormBuild.saveField(field);
    });
    field.find(".fgfield-formbutton-cancel").bind("click", function(event){
        var field = jq(event.currentTarget).parents(".fgfield-wrapper");
        pfgFormBuild.unselect();
    });
}

pfgFormBuild.makeDropable = function(field) {
    field.droppable({
            accept : ".addableItem",
            drop : function (event, ui){
                        var drag = ui.draggable;
                        var fieldtype = drag.attr("id").substr("addableItem-".length);
                        var index = parseInt(jq(this).attr("index"));
                        pfgFormBuild.addField(fieldtype, index);
                        pfgFormBuild.blankPlaceHolder.css("display", "none");
                    },
            over : function (event, ui) {
                        var placeholder = pfgFormBuild.blankPlaceHolder;
                        jq(this).before(placeholder[0]);
                        placeholder.css("display", "block");
                    },
            out : function (event, ui) {
                        pfgFormBuild.blankPlaceHolder.css("display", "none");
                    }
            });
}

pfgFormBuild._refreshFieldList = function() {
    //Update the field list
    this.fields = this.fieldstable.children(".fgfield-wrapper");
    //Update the position of available field
    this.fields.each(function(i) {
        jq(this).attr("index", i)
    });
}

pfgFormBuild.focus = function(field) {
    //Focus on a field
    if (this.selectedfield != null) 
        //If we already selected a field, then we need to disable focus
        return;
    field.addClass("fgfield-focus");
    field.find(".fgfield-editbuttons").css("display", "block"); 
}

pfgFormBuild.unfocus = function(field) {
    //Unfocus on a field
    field.removeClass("fgfield-focus");
    if (this.selectedfield == null)
        //Dangerous set, should only call when not in select
        field.find(".fgfield-editbuttons").css("display", "none"); 
}

pfgFormBuild.getSelect = function(field) {
    //Is the field shows selected or not
    return (pfgFormBuild.selectedfield != null && pfgFormBuild.selectedfield[0] == field[0])
}

pfgFormBuild.select = function(field) {
    //If already selected: unselect the old 
    if (this.selectedfield != null) 
        //If we already selected a field, then we need to unselect first
        this.unselect();
    //We also need to unfocus all focused fields    
    this.fieldstable.children(".fgfield-wrapper fgfield-focus").each(function(i) {
        pfgFormBuild.unfocus(jq(this));
    });
    //Select the field
    field.addClass("fgfield-selected");
    field.find(".fgfield-view-wrapper").addClass("fgfield-highlight");
    field.find(".fgfield-editbuttons").css("display", "block"); 
    this.selectedfield=field;
    //Remove focus classes if have
    field.removeClass("fgfield-focus");
    //Disable sortable and draggable
    this.fieldstable.sortable("disable")
}

pfgFormBuild.unselect = function() {
    if (this.selectedfield == null)
        return;
    //Free the select field
    var field = this.selectedfield;
    field.removeClass("fgfield-selected");
    field.find(".fgfield-view-wrapper").removeClass("fgfield-highlight");
    field.find(".fgfield-editbuttons").css("display", "none"); 
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
}

pfgFormBuild.hideEdit = function(field) {
    field.children(".fgfield-edit-wrapper").css("display", "none");
}

pfgFormBuild.getFieldById = function(fieldId) {
    //Return jq wrapper of field object or null if not found
    var field = this.fieldstable.children("#fgfield-%s" %fieldId);
    if (field.length) return field;
    return null;    
}

pfgFormBuild.getFieldByPosition = function(pos) {
    //Return jq wrapper of field object or null if not found
    if (this.fields.length > pos) return jq(this.fields[pos]);
    return null;    
}

pfgFormBuild.getPosition = function(field) {
    //Get field"s position
    var pos = pfgFormBuild.fieldstable.children('.fgfield-wrapper').index(field[0]);
    return pos == -1 ? null : pos;
}

pfgFormBuild.addField = function(fieldtype, pos) {
    //Add new field
    var response;
    var data = {"fieldtype": fieldtype};
    if (pos >= 0)
        data.position = pos;
    response = jqPost("add", JSON.stringify(data));    
    response = JSON.parse(response);
    if (response.status == "success") {
        //Create new field
        var newfield = jq("<div/>");
        newfield.attr("class", "fgfield-wrapper");
        newfield.attr("id", "fgfield-" + response.data.fieldid);
        newfield.html(response.data.html);
        //Add to position pos
        this.getFieldByPosition(pos).before(newfield);
        //Create form tabbing
        newfield.find("form.enableFormTabbing,div.enableFormTabbing").each(ploneFormTabbing.initializeForm);
        this.addEventHandlers(newfield);
        this.makeDropable(newfield);
        this.fieldstable.sortable('refresh');
        this._refreshFieldList();
        //Do select the new field
        this.select(newfield);
        this.showEdit(newfield);
        return true;
    }
    return false;
}

pfgFormBuild.copyField = function(field) {
    //Clone the current field
    var data = {"fieldid": field.attr("id").substr("fgfield-".length)};
    var response = jqPost("copy", JSON.stringify(data));    
    response = JSON.parse(response);
    if (response.status == "success") {
        //Create new field
        var newfield = jq("<div/>");
        newfield.attr("class", "fgfield-wrapper");
        newfield.attr("id", "fgfield-" + response.data.fieldid);
        newfield.html(response.data.html);
        //Add right after current field
        field.after(newfield);
        //Create form tabbing
        newfield.find("form.enableFormTabbing,div.enableFormTabbing").each(ploneFormTabbing.initializeForm);
        this.addEventHandlers(newfield);
        this.makeDropable(newfield);
        this.fieldstable.sortable('refresh');
        this._refreshFieldList();
        //Do select the new field
        this.select(newfield);
        return true;
    }
    return false;
}

pfgFormBuild.moveField = function(field, newpos) {
    var data = {"fieldid" : field.attr("id").substr("fgfield-".length),
                "position" : newpos
               };
    var response =  jqPost("move", JSON.stringify(data));
    response = JSON.parse(response);
    if (response.status == "success") {
        this._refreshFieldList();
        return true;
    }
    return false
}

pfgFormBuild.deleteField = function(field) {
    var data = {"fieldid" : field.attr("id").substr("fgfield-".length)};
    var response =  jqPost("delete", JSON.stringify(data));
    response = JSON.parse(response);
    if (response.status == "success") {
        //Unselect it we're selecting something
        this.unselect();
        //Selfdestruct
        field.remove();      
        this.fieldstable.sortable('refresh');
        this._refreshFieldList();
    }
    return false;
}

pfgFormBuild.saveField = function(field) {
    var data = {"fieldid" : field.attr("id").substr("fgfield-".length), 
                "poststr" : field.find(":input").serialize()
               };
    var response =  jqPost("save", JSON.stringify(data));
    response = JSON.parse(response);
    //Update the field
    field.html(response.data.html);
    field.find("form.enableFormTabbing,div.enableFormTabbing").each(ploneFormTabbing.initializeForm);
    this.addEventHandlers(field);
    this.makeDropable(field);
    this.fieldstable.sortable('refresh');
    this._refreshFieldList();

    if (response.status != "success") {
        //if not success: Show the edit form (with errors)
        this.select(field);
        this.showEdit(field);
        return true;
    }
    return false;
}

// App code
jq(document).ready(function() {

    //Create a blank place holder (use for add object)
    var divTag = document.createElement("div");
    divTag.id = "fgfield-blankspaceholder";
    divTag.className ="fgfield-placeholder";
    divTag.style.display = "none";
    divTag.innerHTML = "";
    document.body.appendChild(divTag);

    //Initialize the form build manager
    pfgFormBuild.initialize()
    
    //Make addable types drag & dropable 
    jq(".addableItem").draggable({
        helper: "clone"
    });

})

