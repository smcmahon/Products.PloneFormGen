Using PFG's CAPTCHA Field
=========================

When PFG is installed in a Plone instance via add/remove products, it will 
look for evidence that either collective.captcha or collective.recaptcha are
available. If that's found, the Captcha Field will be added to the available 
field list.

If you are using collective.recaptcha, you need to take the additional step
of setting your public/private keypair. You get these by setting up an account
at recaptcha.net. The account is free. You may specify your keypair in the PFG
configlet in your site settings.

If you add a captcha facility *after* installing PFG, you will need to 
reinstall PFG (via add/remove products) to enable captcha support.

PFG's captcha support is based on Thomas Buchberger's PFGCaptchaField.  If you
were using the separate PFGCaptchaField product with a version of PloneFormGen
<= 1.5b3, you must uninstall PFGCaptchaField and remove the product from your
environment before installing PFG >= 1.5b4.  You don't need to remove existing
captcha fields from your forms though; they should continue to work.


CAPTCHA Implementations
-----------------------

If you are not already using collective.captcha or collective.recaptcha, you
will need to install one of them. These two facilities provide very different
captcha support.

collective.captcha generates its own images and wav files using skimpygimpy.

collective.recaptcha uses the Carnegie-Mellon University's very polished and
well-internationalized recaptcha.net service.

Gory Details
------------

What PFG checks for on install is the availability of a browser view named
captcha. It assumes that the view will have the facilities defined by
collective.captcha.
