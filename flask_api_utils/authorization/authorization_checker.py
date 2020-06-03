from flask_api_utils.authorization.config import config
from flask_api_utils.authorization.role_hierachy import RoleHierarchy
from flask_api_utils.authorization.voter import GRANTED, DENIED
from flask_api_utils.authorization.voter.skutrak_role_hierachy_voter import SkutrakRoleHierarchyVoter

"""
Authorization mechanism inspired from Symfony
"""


class AccessDecisionManager:
    """
    Security voters are the key feature of this authorization mechanism.
    They provide the most granular way of checking permissions (e.g. "can this specific user edit the given item?")
    In order to grant or deny permission, all the voters' decisions are aggregated by the Access Decision Manager.
    Then, depending on your application config, permission is granted if all voters said yes (unanimous),
    or if the majority said yes (consensus),
    or if at least one voter said yes (affirmative).
    """

    def __init__(self,
                 strategy='affirmative',
                 allow_if_equal_granted_denied_decisions=False,
                 allow_if_all_abstain_decisions=True):
        strategy_method = getattr(self, 'decide_{}'.format(strategy))
        if strategy == '' or not callable(strategy_method):
            raise ValueError('The strategy {} is not supported.'.format(strategy))

        self.strategy = strategy_method
        self.allow_if_equal_granted_denied_decisions = allow_if_equal_granted_denied_decisions
        self.allow_if_all_abstain_decisions = allow_if_all_abstain_decisions

        self.voters = []

    def decide(self, user, attributes, subject):
        return self.strategy(user, attributes, subject)

    # Decision logic
    def decide_affirmative(self, user, attributes, subject):
        deny = 0
        for voter in self.voters:
            result = voter.vote(user, subject, attributes)

            if result == GRANTED:
                return True

            if result == DENIED:
                deny += 1

        if deny > 0:
            return False

        return config.allow_if_all_abstain_decisions

    def decide_consensus(self, user, attributes, subject):
        grant = 0
        deny = 0
        for voter in self.voters:
            result = voter.vote(user, subject, attributes)

            if result == GRANTED:
                grant += 1
            if result == DENIED:
                deny += 1

        if grant > deny:
            return True

        if deny > grant:
            return False

        if grant > 0:
            return config.allow_if_equal_granted_denied_decisions

    def decide_unanimous(self, user, attributes, subject):
        grant = 0
        for voter in self.voters:
            result = voter.vote(user, subject, attributes)

            if result == DENIED:
                return False

            if result == GRANTED:
                grant += 1

        if grant > 0:
            return True

        return config.allow_if_all_abstain_decisions

    def decide_priority(self, user, attributes, subject):
        for voter in self.voters:
            result = voter.vote(user, subject, attributes)

            if GRANTED == result:
                return True
            if DENIED == result:
                return False

        return config.allow_if_all_abstain_decisions


class AuthorizationChecker:
    """
    Already inited with SkutrakHierarchyRoleVoter
    authorization_checker.is_granted(user, 'can_edit', subject_to_check)
    Usage example:
    For skutrak permission checking

    To check permission on a specific hostname and retailer
    authorization_checker.is_granted(user, 'content_viewer', 'host_name.retailer')

    To check permission on a specific hostname regardless of retailers
    authorization_checker.is_granted(user, 'staff_content_viewer', 'host_name.*')
    or authorization_checker.is_granted(user, 'content_viewer', 'host_name')

    To check permission on a specific retailer regardless of hostname
    authorization_checker.is_granted(user, 'content_viewer', '*.retailer')

    To check permission on a all hostname and retailer
    authorization_checker.is_granted(user, 'content_viewer', '*.*')

    To check staff permission
    authorization_checker.is_granted(user, 'staff_user_manager')
    """
    access_decision_manager = None

    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        """
        Register this extension with the flask app.
        :param app:
        :return:
        """
        if not hasattr(app, 'extensions'):  # pragma: no cover
            app.extensions = {}
        app.extensions['authorization-checker'] = self

        self._set_default_configuration_options(app)

        self.access_decision_manager = AccessDecisionManager(app.config['AUTHORISATION_DECISION_STRATEGY'],
                                                             app.config['AUTHORISATION_ALLOW_IF_ALL_ABSTAIN_DECISIONS'],
                                                             app.config[
                                                                 'AUTHORISATION_ALLOW_IF_EQUAL_GRANTED_DENIED_DECISIONS'])
        # init voters
        self.init_voters(app)

    def init_voters(self, app):
        # TODO: Allow loading custom voters
        role_hierarchy = RoleHierarchy(app.config['AUTHORISATION_ROLE_HIERARCHY'])
        self.access_decision_manager.voters.append(
            SkutrakRoleHierarchyVoter(role_hierarchy, app.config['AUTH0_ORGANISATIONS_CLAIM_NAME']))

    @staticmethod
    def _set_default_configuration_options(app):
        app.config.setdefault('AUTHORISATION_DECISION_STRATEGY', 'affirmative')
        app.config.setdefault('AUTHORISATION_ALLOW_IF_EQUAL_GRANTED_DENIED_DECISIONS', False)
        app.config.setdefault('AUTHORISATION_ALLOW_IF_ALL_ABSTAIN_DECISIONS', True)
        app.config.setdefault('AUTHORISATION_ROLE_HIERARCHY', {})

    def is_granted(self, user, role, subject=None):
        return self.access_decision_manager.decide(user, [role], subject)
