Introduction
============

This package provides a generic Plone form generator.
Use it to build simple, one-of-a-kind, web forms that save or mail form input.

Repository for this add on is at https://github.com/smcmahon/Products.PloneFormGen.
A documentation area is at http://docs.plone.org/working-with-content/managing-content/ploneformgen/
and an issue tracker at https://github.com/smcmahon/Products.PloneFormGen/issues

Please use the Plone forum at https://community.plone.org for
support requests. If you are unable to get your questions answered
there, or are interested in helping develop the product, contact Steve
McMahon: steve@dcn.org.

.. image:: https://travis-ci.org/smcmahon/Products.PloneFormGen.svg?branch=master
    :alt: Travis CI badge; if you break it, you fix it.
    :target: https://travis-ci.org/smcmahon/Products.PloneFormGen


1.8 Notes
=========

PFG 1.8 is intended for use with Plone 5+. If you're using Plone 4.1.x-4.3.x, choose PFG 1.7.x. PFG 1.6.x targets Plone < 4.1.

collective.js.jqueryui is no longer required. If you've migrated from Plone 4.x and no other package is using it, you may uninstall it.

Known Issues
------------

 * Export/Import is not yet working;
 * The ReCAPTCHA config form is primitive.

Overview
========

PloneFormGen is a generic Plone form generator using fields,
widgets and validators from Archetypes. Use it to build simple,
one-of-a-kind, web forms that save or mail form input.

To build a web form, create a form folder, then add form fields as
contents. Individual fields can display and validate themselves for
testing purposes. The form folder creates a form from all the contained
field content objects.

Final disposition of form input is handled via plug-in action products.
Action adapters included with this release include a mailer, a
save-data adapter that saves input in tab-separated format for later
download, and a custom-script adapter that makes it possible to script
simple actions without recourse to the Zope Management Interface.

To make it easy to get started, newly created form folders are
pre-populated to act as a simple e-mail response form.

Dependencies
============

Plone: Plone 5.0b2+

Requires PythonField, TALESField and TemplateFields from Jens W.
Klein's ScriptableFields bundle: http://plone.org/products/scriptablefields/
(automatically loaded if you install via Python package).

Encryption of e-mail requires the Gnu Privacy Guard, GnuPG, also known
as gpg. See README_GPG.txt for details.

CAPTCHA support requires either collective.captcha or collective.recaptcha.
See README_CAPTCHA.txt for details.

Installation
============

*   Just add ``Products.PloneFormGen`` to the eggs section of your buildout
    configuration and run buildout.

*   Restart Zope.

*   Go to the Site Setup page in the Plone interface and click on the
    Add/Remove Products link. Choose PloneFormGen (check its checkbox) and
    click the Install button. If PloneFormGen is not available on the
    Add/Remove Products list, it usually means that the product did not
    load due to missing prerequisites.

*   If necessary, use the PloneFormGen configlet in the "Add-on Product
    Configuration" section of Site Setup to customize the product for your
    site.

Permissions
===========

Site managers may control the visibility and availability of many
PloneFormGen functions by changing permissions for user roles. A
control panel configlet controls role/permission associations for the
portal root. For an explanation of how PloneFormGen permissions map to
form folder and form field fields, see improvement proposal #3, Provide
ways to hide advanced options from classes of
users: http://plone.org/products/ploneformgen/roadmap/3 .

Security
========

As shipped, only managers may use TALES expressions to override
defaults and validators. You may wish to add additional roles, but keep
in mind that this is a potential security risk; it basically gives the
same powers as scripting or skin editing.

History
=======

PloneFormGen has been continually updated since Plone 2. The maintainers
are proud it's still maintained and reliable, but it should not be used
as a good example of a current Plone packages. It contains too many
historical layers.

Credits
=======

Archetypes has been ruthlessly mined for concepts and functionality.

Form and field icons are scavenged from Martijn Faassen's Formulator,
and were edited only to add transparency to make them look a bit better
on the add items menu.

The mail adapter is basically a tailored version of PloneFormMailer,
minus the Formulator adapter machinery. Thanks to PloneFormMailer's
authors, Jens Klein and Reinout van Rees for this code and for
continual assistance since the package's introduction.

Pierre-Yves Landure provided tremendous help with the i18n machinery.
Sebastien Douche and Pierre-Yves Landure provided the French translation.

Martin Aspeli's RichDocument has provided an invaluable reference,
particularly in how to handle installation and testing issues.

Martin Aspeli, Wichert Akkerman, Eric Steele, Jens Klein and Reinout
van Rees all provided valuable early feedback.

Titus Anderson provided the base code for the Ratings-Scale Field.
Andreas Jung contributed the record-editing feature for the Save Data
adapter.

Fulvio Casali, Alex Tokar, David Glick, Steve McMahon, Jesse Snyder,
Michael Dunlap, Paul Bugni, Jon Baldivieso and Andrew Burkhalter all
did amazing things at the December 2008 PFG sprint sponsored by OneNW.
Special thanks to David, for the CAPTCHA work, and Andrew for export/
import.

Thomas Buchberger provided the initial CAPTCHA field implementation.

Maurits van Rees has been a co-maintainer for the 1.7.x and 1.8.x series. David Glick was co-maintainer for versions
1.2.5 through 1.7.x. Thanks, Maurits and David!

Nenad Mancevic (Manca) added the widget toolbox and dramatically enhanced
the quick edit mode for his Google Summer of Code 2010 project. Thanks to
Manca and Google!

Alec Mitchell, Nathan Van Gheem and Eric Steele provided vital assistance
with the Plone 5 update.

See the CHANGES.txt file for the very long list of people who helped
with particular features or bugs.

License
=======

Distributed under the GPL v 2.

See LICENSE.txt and LICENSE.GPL for details.
