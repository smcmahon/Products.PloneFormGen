// Support functions
jqPost = function(action, data) {
    //sync request to server
    var rs;
    jQuery.ajax({
        url: 'formbuild',
        error: function(request, statusmsg, errorthrow) {
            rs = JSON.stringify({
                   status : "failure",
                   msg : {"type" : "error", "content" : "Internal server error !"},
                   data : null
                 });
        },
        success: function(result) {
            if (result.isOk == false) {
                rs = JSON.stringify({
                       status : "failure",
                       message : {"type" : "error", "content" : "Internal server error !"},
                       data : null
                     });
            } else
                rs = result;
        },
        async: false,
        data: { "action": action, "data": data},
        type: "POST"
    });
    return rs;
}

addPortalMessage = function(type, content) {
    //Add a portal message
    var portalmsg = jq("#kssPortalMessage");
    for (atype in ['info', 'error', 'warning'])
        if (atype != type) portalmsg.removeClass(atype);
    portalmsg.addClass(type)
    portalmsg.find("dt").html(type[0].toUpperCase() + type.substr(1));
    portalmsg.find("dd").html(content);
    portalmsg.css("display", "block");
    setTimeout(function(){ jq("#kssPortalMessage").fadeOut() }, 2000);
}


