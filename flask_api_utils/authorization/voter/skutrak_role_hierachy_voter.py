from flask_api_utils.authorization.voter import ABSTAIN, GRANTED, DENIED


class SkutrakRoleHierarchyVoter:
    def __init__(self, hierarchy, host_name_key):
        self.role_hierarchy = hierarchy
        self.host_name_key = host_name_key

    def vote(self, user, subject, attributes):
        extracted_roles = self.extract_roles(user)
        host_name, retailer = self.get_host_name_retailer_parts(subject)

        result = ABSTAIN

        for attribute in attributes:
            if not isinstance(attribute, str):
                continue

            result = DENIED
            if host_name:
                if host_name == '*':
                    if retailer == '*':
                        for organisation_config in extracted_roles.values():
                            for r, roles in organisation_config.items():
                                if attribute in roles:
                                    return GRANTED
                    else:
                        for organisation_config in extracted_roles.values():
                            for r, roles in organisation_config.items():
                                if r == retailer and attribute in roles:
                                    return GRANTED

                elif host_name in extracted_roles:
                    # Check in all retailers
                    if retailer == '*':
                        for roles in extracted_roles[host_name].values():
                            if attribute in roles:
                                return GRANTED
                    # Single retailer
                    elif retailer in extracted_roles.get(host_name) \
                            and attribute in extracted_roles[host_name][retailer]:
                        return GRANTED
            else:
                # Staff roles, no need for organisation check, use global retailer only
                retailer = 'global'
                for organisation_config in extracted_roles.values():
                    if retailer in organisation_config and attribute in organisation_config.get(retailer, {}):
                        return GRANTED

        return result

    def extract_roles(self, user):
        extracted = {}
        for host_name, organisation_config in user.get(self.host_name_key).items():
            extracted[host_name] = {}
            for retailer, roles in organisation_config.get('roles').items():
                extracted[host_name][retailer] = self.role_hierarchy.get_reachable_role_names(roles)

        return extracted

    def get_host_name_retailer_parts(self, subject):
        host_name = None
        retailer = None
        if isinstance(subject, str):
            parts = subject.split('.', 1)
            if len(parts) == 2:
                host_name = parts[0]
                retailer = parts[1]
            elif len(parts) == 1:
                host_name = parts[0]
                retailer = '*'

        return host_name, retailer
