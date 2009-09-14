// Support functions
jqPost = function(action, data) {
    //sync request to server
    var rs;
    jQuery.ajax({
        url: 'formbuild',
        error: function(request, statusmsg, errorthrow) {
            addPortalMessage("error", "Internal server error.");
            rs = null;
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
    rs = JSON.parse(rs);
    if (rs.message != null)
        addPortalMessage(rs.message.type, rs.message.content)
    return rs;
}

addPortalMessage = function(type, content) {
    //Add a portal message
    var portalmsg = jq("#kssPortalMessage");
    var msgtypes = ["info", "warning", "error"];
    for (var i = 0; i < msgtypes.length; i++)
        if (msgtypes[i] != type) portalmsg.removeClass(msgtypes[i]);
    portalmsg.addClass(type)
    portalmsg.find("dt").html(type[0].toUpperCase() + type.substr(1));
    portalmsg.find("dd").html(content);
    portalmsg.css("display", "block");
    setTimeout(function(){ jq("#kssPortalMessage").fadeOut() }, 5000);
}


