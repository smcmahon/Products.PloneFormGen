jq(function(){
    // show preview if no errors
    if (jq('#form-confirmation').length) {
      jq('#form-confirmation').hide();
      if (!jq('.error').length) {
        jq('#form-confirmation').overlay({api:true,expose:true}).load();
      }
    }
});
