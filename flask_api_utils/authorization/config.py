from flask import current_app


class _Config(object):
    @property
    def decision_strategy(self):
        from flask_api_utils.authorization.authorization_checker import AccessDecisionManager

        strategy = current_app.config['AUTHORISATION_DECISION_STRATEGY']
        strategy_method = getattr(AccessDecisionManager, 'decide_{}'.format(strategy))
        if strategy == '' or not callable(strategy_method):
            raise ValueError('The strategy {} is not supported.'.format(strategy))

        return strategy_method

    @property
    def allow_if_equal_granted_denied_decisions(self):
        return current_app.config['AUTHORISATION_ALLOW_IF_EQUAL_GRANTED_DENIED_DECISIONS']

    @property
    def allow_if_all_abstain_decisions(self):
        return current_app.config['AUTHORISATION_ALLOW_IF_ALL_ABSTAIN_DECISIONS']

    @property
    def role_hierarchy(self):
        return current_app.config['AUTHORISATION_ROLE_HIERARCHY']


config = _Config()
