# a bit of a hack to complete the load test setup after the profile,
# since I'm too lazy to register a custom GS import step for now
import transaction
portal.testform.setCheckAuthenticator(False)
portal.portal_workflow.doActionFor(portal.testform, 'publish')
transaction.commit()
